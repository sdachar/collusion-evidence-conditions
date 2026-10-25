import json, sys, glob, os, collections
meta = json.load(open(sys.argv[2], encoding="utf-8"))
used = {r["run_id"] for r in meta}
for model in ("qwen3_32b", "gpt_oss_20b"):
    c = collections.Counter()
    for f in glob.glob(os.path.join(sys.argv[1], model, "core", "*", "run_config.json")):
        rc = json.load(open(f, encoding="utf-8"))
        tag = ("in_probe_set" if rc["run_id"] in used else "excluded") if model == "qwen3_32b" else "-"
        c[(rc["mode"], tag, "success" if rc.get("collusion_success") else "fail", "flagged" if rc.get("flagged") else "")] += 1
    print(model); [print("  ", k, v) for k, v in sorted(c.items())]
