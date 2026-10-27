using UnityEngine;
using Varwin;
using Varwin.Public;

namespace Varwin.Types.Sphere_668a7b45f7a3449795d3d5bf9fe5bd6b
{
    [VarwinComponent(English: "Sphere")]
    public class Sphere : VarwinObject
    {
        private Animator animator;
        private void Awake()
        {
            animator = GetComponent<Animator>();
        }

        [Action("Open")]
        [Locale(SystemLanguage.English, "Open")]
        public void Open()
        {
            animator.SetTrigger("Open");
        }

        [Action("Red")]
        [Locale(SystemLanguage.English, "Red")]
        public void Red()
        {
            animator.SetTrigger("Red");
        }
    }
}
