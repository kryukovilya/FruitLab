"""Replace contact emails in this repository's main history with GitHub noreply."""
import argparse
import re
import subprocess

IDENTITY = b"kryukovilya <346212622+kryukovilya@users.noreply.github.com>"


def git(*args: str, data: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", *args], input=data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rewrite", action="store_true", required=True)
    parser.parse_args()
    if git("status", "--porcelain").strip():
        raise SystemExit("The working tree must be clean")
    old = git("rev-parse", "HEAD").decode().strip()
    mapping: dict[str, str] = {}
    for sha in git("rev-list", "--reverse", "--topo-order", "HEAD").decode().splitlines():
        headers, message = git("cat-file", "commit", sha).split(b"\n\n", 1)
        result = []
        signature = False
        for line in headers.splitlines():
            if line.startswith((b"gpgsig ", b"gpgsig-sha256 ")):
                signature = True
                continue
            if signature and line.startswith(b" "):
                continue
            signature = False
            if line.startswith(b"parent "):
                line = b"parent " + mapping[line[7:].decode()].encode()
            elif line.startswith((b"author ", b"committer ")):
                role = line.split(b" ", 1)[0]
                timestamp = re.search(rb" ([0-9]+ [+-][0-9]{4})$", line)
                if timestamp is None:
                    raise ValueError("Unexpected Git identity format")
                line = role + b" " + IDENTITY + b" " + timestamp.group(1)
            result.append(line)
        rewritten = b"\n".join(result) + b"\n\n" + message
        mapping[sha] = git("hash-object", "-w", "-t", "commit", "--stdin", data=rewritten).decode().strip()
    new = mapping[old]
    if git("rev-parse", old + "^{tree}") != git("rev-parse", new + "^{tree}"):
        raise ValueError("The repository contents changed during metadata cleanup")
    git("update-ref", "refs/heads/main", new, old)
    identities = git("log", "--format=%ae%n%ce", "main").decode().splitlines()
    if not all(email.endswith("@users.noreply.github.com") for email in identities):
        raise ValueError("A reachable commit still contains a contact email")
    print(f"Normalized {len(mapping)} commits; file tree preserved")


if __name__ == "__main__":
    main()
