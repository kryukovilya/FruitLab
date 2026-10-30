"""Package the team's published Varwin build and reconstruct its editable export."""
from __future__ import annotations

import argparse
import base64
import copy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import urllib.request
import zipfile

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes

ROOT = Path(__file__).resolve().parents[1]
CONTACT_FIELDS = {"FirstName", "LastName", "Email", "Company"}
LICENSE_FIELDS = {"GUID", "ExpiresAt", "Code"}


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalize_archive_paths(archive: zipfile.ZipFile) -> None:
    """Varwin exports Windows separators, which zipfile preserves on Linux."""
    for info in archive.infolist():
        info.filename = info.filename.replace("\\", "/")
    archive.NameToInfo = {info.filename: info for info in archive.infolist()}


def runtime_codec(archive: zipfile.ZipFile) -> AESGCM:
    """Read the format from the shipped runtime; no account credentials are used."""
    pe = dnfile.dnPE(data=archive.read("VarwinClient_Data/Managed/ADec.dll"))
    method = next(m for m in pe.net.mdtables.MethodDef if str(m.Name) == "GetProjectDecJson")
    body = read_method_body_from_bytes(pe.get_data(method.Rva))
    strings = [str(pe.net.user_strings.get(i.operand.value & 0xFFFFFF))
               for i in body.instructions if i.opcode.name == "ldstr"]
    if len(strings) != 3 or strings[:2] != ["\\n", ""]:
        raise ValueError("The published runtime uses an unexpected metadata format")
    return AESGCM(hashlib.md5(strings[2].encode("utf-8")).hexdigest().encode("ascii"))


def clean_metadata(original: dict, codec: AESGCM) -> dict:
    packed = base64.b64decode(original["licenseKey"].replace("\\n", ""), validate=True)
    details = json.loads(codec.decrypt(packed[:12], packed[12:], None).rstrip(b"\0"))
    if set(details) != CONTACT_FIELDS | LICENSE_FIELDS:
        raise ValueError("Unexpected license fields; manual review is required")
    cleaned = {k: "" if k in CONTACT_FIELDS else v for k, v in details.items()}
    nonce = os.urandom(12)
    encoded = nonce + codec.encrypt(nonce, json.dumps(cleaned, separators=(",", ":")).encode(), None)
    checked = json.loads(codec.decrypt(encoded[:12], encoded[12:], None))
    if any(checked[k] for k in CONTACT_FIELDS):
        raise ValueError("Contact fields were not cleared")
    if any(checked[k] != details[k] for k in LICENSE_FIELDS):
        raise ValueError("A license entitlement parameter changed")
    result = copy.deepcopy(original)
    result["licenseKey"] = base64.b64encode(encoded).decode("ascii")
    return result


def prepare(source: Path, output: Path, recipe: dict) -> dict:
    if digest(source) != recipe["source_sha256"]:
        raise ValueError("The source build does not match the reviewed SHA-256")
    output.mkdir(parents=True, exist_ok=True)
    exe = output / "FruitLab.exe"
    export = output / "FruitLab.vwp"
    with zipfile.ZipFile(source) as old:
        normalize_archive_paths(old)
        codec = runtime_codec(old)
        metadata = clean_metadata(json.loads(old.read("project/index.json")), codec)
        payload = json.dumps(metadata, ensure_ascii=False, separators=(",", ":")).encode()
        prefix_size = min(i.header_offset for i in old.infolist())
        with source.open("rb") as reader, exe.open("wb") as writer:
            writer.write(reader.read(prefix_size))
        with zipfile.ZipFile(exe, "a", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as new:
            new.comment = old.comment
            for info in old.infolist():
                new.writestr(copy.copy(info), b"" if info.is_dir() else
                             payload if info.filename == "project/index.json" else old.read(info))
        export_metadata = copy.deepcopy(recipe["metadata"])
        export_metadata["licenseKey"] = metadata["licenseKey"]
        export_payload = json.dumps(export_metadata, ensure_ascii=False, separators=(",", ":")).encode()
        with zipfile.ZipFile(export, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as outer:
            outer.writestr("FruitLab.vwm", export_payload)
            for package in recipe["packages"]:
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as inner:
                    for member in package["members"]:
                        if member["directory"]:
                            inner.writestr(member["name"], b"")
                            continue
                        if "source" in member:
                            data = old.read(member["source"])
                        elif "resources" in member:
                            chunks = []
                            for resource in member["resources"]:
                                resource_path = (ROOT / resource).resolve()
                                if not resource_path.is_relative_to((ROOT / "distribution/resources").resolve()):
                                    raise ValueError("Unsafe resource path")
                                chunk = resource_path.read_bytes()
                                if hashlib.sha256(chunk).hexdigest() != resource_path.name:
                                    raise ValueError("A resource chunk is corrupt")
                                chunks.append(chunk)
                            data = b"".join(chunks)
                        else:
                            data = base64.b64decode(member["inline"], validate=True)
                        if hashlib.sha256(data).hexdigest() != member["sha256"]:
                            raise ValueError("A project resource does not match its recorded digest")
                        inner.writestr(member["name"], data)
                outer.writestr(package["name"], buffer.getvalue())
        with zipfile.ZipFile(exe) as new:
            if old.namelist() != new.namelist():
                raise ValueError("The Windows package lost an entry")
            for info in new.infolist():
                if not info.is_dir() and info.filename != "project/index.json":
                    if new.read(info) != old.read(info.filename):
                        raise ValueError("A runtime file changed")
        with zipfile.ZipFile(export) as outer:
            if outer.testzip() is not None:
                raise ValueError("The editable export failed its CRC check")
            for package in recipe["packages"]:
                with zipfile.ZipFile(io.BytesIO(outer.read(package["name"]))) as inner:
                    if inner.testzip() is not None:
                        raise ValueError("A nested project package failed its CRC check")
                    for member in package["members"]:
                        if not member["directory"] and hashlib.sha256(inner.read(member["name"])).hexdigest() != member["sha256"]:
                            raise ValueError("An exported resource changed")
        for path in (exe, export):
            with zipfile.ZipFile(path) as archive:
                entry = "project/index.json" if path == exe else "FruitLab.vwm"
                checked = json.loads(archive.read(entry))
                raw = base64.b64decode(checked["licenseKey"])
                details = json.loads(codec.decrypt(raw[:12], raw[12:], None))
                if any(details[k] for k in CONTACT_FIELDS):
                    raise ValueError("A distribution still contains license contact data")
    sums = "".join(f"{digest(path)}  {path.name}\n" for path in (exe, export))
    (output / "SHA256SUMS.txt").write_text(sums, encoding="ascii")
    return {"runtime_files_verified": sum(not i.is_dir() for i in old.infolist()), "project_packages_verified": len(recipe["packages"]),
            "license_contact_fields_cleared": sorted(CONTACT_FIELDS),
            "license_parameters_preserved": sorted(LICENSE_FIELDS),
            "interactive_launch_tested": False,
            "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p)} for p in (exe, export)]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="Existing copy of the published EXE")
    parser.add_argument("--output", type=Path, default=ROOT / "dist-release")
    args = parser.parse_args()
    recipe = json.loads((ROOT / "distribution/vwp-recipe.json").read_text(encoding="utf-8"))
    temporary_context = contextlib.nullcontext(None) if args.source else tempfile.TemporaryDirectory(prefix="fruitlab-")
    with temporary_context as temporary:
        source = args.source
        if source is None:
            source = Path(temporary) / "original.exe"
            request = urllib.request.Request(recipe["source_url"], headers={"User-Agent": "FruitLab-release"})
            with urllib.request.urlopen(request, timeout=120) as response, source.open("wb") as writer:
                while chunk := response.read(1024 * 1024):
                    writer.write(chunk)
        report = prepare(source, args.output, recipe)
        (args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
