using UnityEngine;
using Varwin;
using Varwin.Public;
using System.Collections.Generic;
using System.Linq;

namespace Varwin.Types.ExporpriationCamera_8cff834d374f4ff58ded885177226e71
{
    [VarwinComponent(English: "Exporpriation Camera")]
    public class ExporpriationCamera : VarwinObject
    {
        private List<Component> fruitCubes = new List<Component>();
        public List<GameObject> inZone = new List<GameObject>();

        private float _loseTimer = 0f;
        private const float LoseDelay = 3f;

        private bool _isWinTriggered = false;
        private bool _isLoseTriggered = false;

        public delegate void WinEvanteHandler();
        [LogicEvent(English: "win")]
        public event WinEvanteHandler Win;

        public delegate void LoseEvanteHandler();
        [LogicEvent(English: "lose")]
        public event LoseEvanteHandler Lose;

        [Action("Refresh")]
        public void Refresh()
        {
            fruitCubes = FindObjectsOfType<Component>(true).Where(c => c.GetType().Name == "FruitlabCube").ToList();

            inZone.Clear();
            _loseTimer = 0f;

            _isWinTriggered = false;
            _isLoseTriggered = false;

            int count = fruitCubes.Count;
            if (count == 0) return;

            List<int> guaranteedIds = new List<int>();
            for (int i = 0; i < count; i++) guaranteedIds.Add((i / 2) % 4);

            var shuffledIds = guaranteedIds.OrderBy(x => System.Guid.NewGuid()).ToList();

            for (int i = 0; i < count; i++)
            {
                var comp = fruitCubes[i];
                comp.gameObject.SetActive(true);

                var idProperty = comp.GetType().GetProperty("Index");
                if (idProperty != null)
                    idProperty.SetValue(comp, shuffledIds[i]);
            }
        }

        private void OnTriggerEnter(Collider foreignCollider)
        {
            GameObject go = foreignCollider.gameObject;
            if (!inZone.Contains(go))
            {
                inZone.Add(go);
            }
        }

        private void OnTriggerExit(Collider foreignCollider)
        {
            GameObject go = foreignCollider.gameObject;
            if (inZone.Contains(go))
            {
                inZone.Remove(go);
            }
        }

        private void Update()
        {
            if (!_isWinTriggered && fruitCubes.Count > 0 && fruitCubes.All(c => c != null && !c.gameObject.activeInHierarchy))
            {
                _isWinTriggered = true;
                Win?.Invoke();
                return;
            }

            inZone.RemoveAll(item => item == null);
            int activeCount = inZone.Count(go => go.activeInHierarchy);

            if (!_isLoseTriggered && activeCount >= 4)
            {
                _loseTimer += Time.deltaTime;
                if (_loseTimer >= LoseDelay)
                {
                    _isLoseTriggered = true;
                    Lose?.Invoke();
                    _loseTimer = 0f;
                }
            }
            else
            {
                _loseTimer = 0f;
            }
        }
    }
}
