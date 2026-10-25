import json, sys, glob, os
meta = json.load(open(sys.argv[2], encoding="utf-8"))
m = {}
for r in meta: m.setdefault(r["run_id"], (r["collusion_success"], r["target_majority"]))
for f in sorted(glob.glob(os.path.join(sys.argv[1], "qwen3_32b", "core", "*__collusion", "run_config.json"))):
    rc = json.load(open(f, encoding="utf-8"))
    if rc["run_id"] in m and m[rc["run_id"]][0] != rc["collusion_success"]:
        print(rc["run_id"], "meta", m[rc["run_id"]], "run_config", rc["collusion_success"], rc["target_majority"], rc["colluder_voted_target"], rc["target_vote_count"], len(rc["agents"]))
