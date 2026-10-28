"""Quick demo: run this file (python run_demo.py). Needs fic_sim.py in the same folder."""
from fic_sim import evaluate

settings = [
    ("Easy case: foundations strongly cited", dict(obl=1.0, fitness=3.0)),
    ("Hard case: foundations not boosted, high obliteration", dict(obl=2.0, fitness=1.0)),
]
for label, kw in settings:
    print(f"\n== {label} | 40-year field, 20 references, 5-year window ==")
    res = evaluate(40, reps=100, seed=1, **kw)
    print(f"{'Rule':18s}{'Lineage recovered':>20s}{'Share recent':>15s}")
    for rule, d in res.items():
        print(f"{rule:18s}{d['cov'][0]:>20.2f}{d['cur'][0]:>15.2f}")
print("\nDone.")
