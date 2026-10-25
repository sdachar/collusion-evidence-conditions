import json, sys, glob, os
meta = json.load(open(sys.argv[2], encoding="utf-8"))
ms = {}
for r in meta: ms.setdefault(r["run_id"], (r["seed"], r["agent_name"] if False else None))
names = {}
for r in meta: names.setdefault(r["run_id"], set()).add(r["agent_name"])
same_seed = same_names = n = 0
for f in glob.glob(os.path.join(sys.argv[1], "qwen3_32b", "core", "*", "run_config.json")):
    rc = json.load(open(f, encoding="utf-8"))
    if rc["run_id"] in ms:
        n += 1; same_seed += ms[rc["run_id"]][0] == rc["seed"]; same_names += names[rc["run_id"]] == set(rc["agents"])
print(f"probe-set runs {n}: seed matches {same_seed}, agent names match {same_names}")
