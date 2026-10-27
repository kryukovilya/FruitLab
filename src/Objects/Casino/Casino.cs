using UnityEngine;
using Varwin;
using Varwin.Public;
using System.Linq;
using System;

namespace Varwin.Types.Casino_7012c06f360949289d5099021de3fae9
{
    [VarwinComponent(English: "Casino")]
    public class Casino : VarwinObject
    {
        public int id = 1;
        public bool isOn = false;

        private Renderer rend;
        private MaterialPropertyBlock propBlock;

        private static readonly int OnID = Shader.PropertyToID("_On");
        private static readonly int SpinID = Shader.PropertyToID("_Spin");
        private static readonly int TextureIndexID = Shader.PropertyToID("_TextureIndex");

        [Action("StartSpin")]
        public void StartSpin()
        {
            SetFloat(OnID, 1);
            SetFloat(SpinID, 1);
        }

        [Action("On")]
        public void On()
        {
            SetFloat(OnID, 1);
        }

        [Action("Off")]
        public void Off()
        {
            SetFloat(OnID, 0);
        }

        [Action("Win")]
        public void win()
        {
            id = UnityEngine.Random.Range(1, 5);

            SetFloat(TextureIndexID, id);
            SetFloat(SpinID, 0);

            Explode(id);
        }

        private void SetFloat(int property, float value)
        {
            rend.GetPropertyBlock(propBlock);
            propBlock.SetFloat(property, value);
            rend.SetPropertyBlock(propBlock);
        }

        public void Explode(int idToExplode)
        {
            var cubes = FindObjectsOfType<Component>(true)
                .Where(c => c.GetType().Name == "FruitlabCube")
                .ToList();

            foreach (var comp in cubes)
            {
                var idProperty = comp.GetType().GetProperty("Index");
                if (idProperty == null) continue;

                float id = Convert.ToSingle(idProperty.GetValue(comp));

                if (id == idToExplode)
                {
                    Animator anim = comp.GetComponent<Animator>();
                    if (anim != null)
                        anim.SetTrigger("Destroy");
                }
            }
        }

        private void Awake()
        {
            rend = GetComponent<Renderer>();
            propBlock = new MaterialPropertyBlock();
        }
    }
}
