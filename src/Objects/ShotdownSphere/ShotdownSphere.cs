using UnityEngine;
using Varwin;
using Varwin.Public;

namespace Varwin.Types.ShotdownSphere_b2cdd9903de14a50850aeea1ff42a37b
{
    [VarwinComponent(English: "Shotdown Sphere")]
    public class ShotdownSphere : VarwinObject
    {
        private Renderer _renderer;
        private MaterialPropertyBlock _block;

        [SerializeField]
        private float _cutoutValue = 0f;

        [Variable(English: "cutout")]
        public float Cutout
        {
            get => _cutoutValue;
            set
            {
                // Ограничиваем значение в диапазоне шейдера (0 - 0.5)
                _cutoutValue = Mathf.Clamp(value, 0f, 0.5f);
                UpdateShader();
            }
        }

        [Action(English: "Add Cutout")]
        public void AddCutout(float amount)
        {
            Cutout += amount;
        }

        private void Awake()
        {
            _renderer = GetComponent<Renderer>();
            _block = new MaterialPropertyBlock();
        }

        private void Start()
        {
            UpdateShader();
        }

        private void UpdateShader()
        {
            if (_renderer == null) return;

            _renderer.GetPropertyBlock(_block);
            _block.SetFloat("_Cutout", _cutoutValue);
            _renderer.SetPropertyBlock(_block);
        }
    }
}
