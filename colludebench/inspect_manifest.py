import json, sys, collections
m = json.load(open(sys.argv[1], encoding="utf-8"))
print(type(m).__name__, list(m)[:10] if isinstance(m, dict) else len(m))
runs = m.get("runs") if isinstance(m, dict) else m
if isinstance(runs, list):
    print("n runs", len(runs)); print("keys", list(runs[0])[:15])
    for k in ("label", "scenario", "environment", "agent_class", "colluding", "split"):
        if k in runs[0]: print(k, collections.Counter(str(r.get(k)) for r in runs).most_common(25))
