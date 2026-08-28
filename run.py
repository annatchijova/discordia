"""DISCORDIA v0.1 -- runner. Uso: python3 run.py [descending|ascending] [n_queries]"""
import json
import sys

from engine import run

order = sys.argv[1] if len(sys.argv) > 1 else "descending"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 200

r = run(max_queries=n, order=order)
p = r["payload"]
print(f"orden={order} steps={p['steps']} terminated={p['terminated']} "
      f"contradicciones={p['contradictions']}")
for s in p["final_state"]:
    print(f"  {s['module']} ({s['label']}): config={s['config']} "
          f"nogoods={s['nogood_count']} paralizado={s['paralyzed']}")
    print(f"     activas: {s['active_rules']}")
print(f"seal: {r['seal']}")
with open(f"historian_{order}.json", "w") as fh:
    json.dump(p, fh, indent=2, ensure_ascii=False)
