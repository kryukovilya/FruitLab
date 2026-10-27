using UnityEngine;
using Varwin;
using Varwin.Public;

namespace Varwin.Types.SpaceEnv_1245b3fa6c1d459a915fbbcf7394c1d7
{
    [VarwinComponent(English: "Space Env")]
    public class SpaceEnv : VarwinObject
    {
        private Animator animator;

        [Action("Intro")]
        public void Intro() => animator.SetTrigger("Begin");

        private void Awake() => animator = GetComponent<Animator>();
    }
}
