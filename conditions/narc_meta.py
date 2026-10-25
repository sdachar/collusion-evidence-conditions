import json, sys, collections
rows = json.load(open(sys.argv[1], encoding="utf-8"))
runs = {}
for r in rows: runs.setdefault(r["run_id"], (r["mode"], r["collusion_success"], r["target_majority"]))
print("rows", len(rows), "runs", len(runs))
print(collections.Counter((m, s) for m, s, t in runs.values()))
