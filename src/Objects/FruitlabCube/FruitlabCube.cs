using UnityEngine;
using Varwin;
using Varwin.Public;

namespace Varwin.Types.FruitlabCube_45ba572919d04157844bad6fe78af7c8
{
    [VarwinComponent(English: "Fruitlab Cube")]
    public class FruitlabCube : VarwinObject
    {
        public delegate void CubeEvanteHandler();
        [LogicEvent(English: "onDestroy")]
        public event CubeEvanteHandler Destroy;

        [LogicEvent(English: "onDrop")]
        public event CubeEvanteHandler OnDrop;
        private Vector3 spawnPoint = Vector3.zero;
        private Animator animator;

        [SerializeField]
        private int _index = 0;
        public int Index
        {
            get => _index;
            set
            {
                if (spawnPoint == Vector3.zero)
                    spawnPoint = transform.position;

                _index = value;
                Refresh();
            }
        }

        private bool inZone = false;
        private bool isDestroying = false;
        private MaterialPropertyBlock block;
        private Renderer rend;
        private Rigidbody rb;

        public void Refresh()
        {
            if (rb == null || rend == null) return;

            isDestroying = false;

            animator.SetTrigger("Show");
            rb.position = spawnPoint;
            transform.position = spawnPoint;

            inZone = false;

            rb.isKinematic = true;
            rb.velocity = Vector3.zero;
            rb.angularVelocity = Vector3.zero;

            transform.rotation = Quaternion.Euler(0f, 0f, 0f);

            rend.GetPropertyBlock(block);
            block.SetInt("_TextureIndex", Index);
            rend.SetPropertyBlock(block);
        }

        private void Awake()
        {
            rb = GetComponent<Rigidbody>();
            rend = GetComponent<Renderer>();
            animator = GetComponent<Animator>();
            block = new MaterialPropertyBlock();
        }
        [Action("Hide")]
        public void hide() => rend.material.SetFloat("_Cutout", 0f);

        private void OnTriggerEnter(Collider other)
        {
            var varwinObj = other.GetComponentInParent<VarwinObject>();

            if (varwinObj != null && varwinObj.GetType().Name == "ExporpriationCamera")
            {
                inZone = true;
            }
        }

        private void OnTriggerExit(Collider other)
        {
            var varwinObj = other.GetComponentInParent<VarwinObject>();

            if (varwinObj != null && varwinObj.GetType().Name == "ExporpriationCamera")
            {
                inZone = false;
            }
        }

        private void OnCollisionStay(Collision collision)
        {
            if (!collision.collider.TryGetComponent<FruitlabCube>(out var other))
                return;

            if (this.isDestroying || other.isDestroying)
                return;

            if (!this.inZone || !other.inZone)
                return;

            if (this.Index != other.Index)
                return;

            if (!gameObject.activeSelf || !other.gameObject.activeSelf)
                return;

            this.isDestroying = true;
            other.isDestroying = true;
            Destroy?.Invoke();

            animator.SetTrigger("Destroy");
            other.animator.SetTrigger("Destroy");
        }

        public void DisableThis() => gameObject.SetActive(false);
        public void Drop() => OnDrop?.Invoke();
    }
}
