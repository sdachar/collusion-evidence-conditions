"""Build specs.json for check_conditions.py from verified numbers only.

Anything not yet verified from released data is left out, so its condition reads NOT-ASSESSABLE.
Revised 22 Oct after REVIEW-fable-2026-10-22.md (C3, C4, M5e, M6).
  python -I build_specs.py <ColludeBench metrics.json> [<NARCBench scenarios dir> <qwen3_32b core metadata_gen.json>
                           [<ColludeBench ablation.json> [<canary prereg/report.json>]]]
Revised 24 Oct: (ii) for the ColludeBench union from ablation.json; the canary as its own row.
"""
import glob
import json
import os
import sys

ALPHA = "0.001"  # ColludeBench's headline budget, FPR 1e-3
# ablation.json, all 510 entries: tp+fn = 17 positive and fp+tn = 1 negative evaluation configurations
CB_UNITS = {"n_units": 1, "unit_note": "ablation.json: 17 positive, 1 negative configuration; the reported "
                                       "stderr treats per-window scores as independent"}


def main(metrics_path, narc_scen=None, narc_meta=None, ablation=None, canary_report=None):
    dets = json.load(open(metrics_path, encoding="utf-8"))["detectors"]
    specs = {}
    # The negatives are per-window scores from the honest *template* calibration pools (no LLM-honest runs),
    # so they are neither independent units nor a placebo for the LLM claim.
    specs["ColludeBench / acceptance_bias"] = {
        "placebo_scores": dets["acceptance_bias"]["negatives"],
        "threshold": dets["acceptance_bias"]["alphas"][ALPHA]["threshold"], "claimed_fpr": float(ALPHA),
        "rule": ">", "placebo_independent": False,
        "placebo_unit_note": "1 score = an aggregate over the review_honest calibration pool", **CB_UNITS}
    specs["ColludeBench / cross_run_mi"] = {
        "placebo_scores": dets["cross_run_mi"]["negatives"],
        "threshold": dets["cross_run_mi"]["alphas"][ALPHA]["threshold"], "claimed_fpr": float(ALPHA),
        "rule": ">", "placebo_independent": False,
        "placebo_unit_note": "119,960 per-pair/window MI values from 600 honest template runs", **CB_UNITS}
    # Riemer et al. 2608.18078, Table 3 (PDF p. 9): CoT Collusion vs steering magnitude, layer 18,
    # r = 0.194, p = 0.677; n = 7 recovered from (r, p) and confirmed by Table 5's seven columns.
    # The paper's claim is a null; the CI must rule out a strong effect (the same table's 0.771 cell).
    specs["2608.18078 / CoT-judge null"] = {"r": 0.194, "n": 7, "claim_is_null": True, "min_effect": 0.5}
    if narc_scen and narc_meta:
        specs.update(narc_specs(narc_scen, narc_meta))
    else:
        specs["NARCBench / Core probe"] = {}
    if ablation:
        specs["ColludeBench / detector union (ablation, FPR 1e-2)"] = union_spec(ablation)
    if canary_report:
        specs["Canary (ours) / randomised cost test"] = canary_spec(canary_report)
    json.dump(specs, sys.stdout)


def union_spec(path, alpha="alpha_1e-02"):
    """(ii) from ablation.json, at the budget the paper's ablation paragraph (p. 8) reports: the full union of
    the 8 statistics vs the union with each removed. (iv) as for the other ColludeBench rows."""
    a = json.load(open(path, encoding="utf-8"))
    full_key = max(a, key=lambda k: len(k.split(",")))
    dets = full_key.split(",")
    tp = lambda key: [a[key][alpha]["tp"], a[key][alpha]["tp"] + a[key][alpha]["fn"]]
    return {"union_full": tp(full_key),
            "union_minus": {d: tp(",".join(x for x in dets if x != d)) for d in dets},
            "union_note": "ablation.json; TPRs are k/17", **CB_UNITS}


def canary_spec(path):
    """Our own instrument, from canary/prereg/report.json: P-0 is its same-process placebo."""
    r = json.load(open(path, encoding="utf-8"))
    return {"label_by_design": "A's cost is a fresh coin flip each round; no role or arm label defines it",
            "single_statistic": "z_t, B's price change times A's centred cost",
            "placebo_ci": r["P-0"]["ci_raw"],
            "placebo_unit_note": "P-0 arm, no channel, 40 runs, price units",
            "n_units": r["POS"]["n_runs"], "unit_note": "independent runs; t-interval over run means"}


def narc_specs(scen_dir, meta_path):
    """(i) on the 62 Qwen Core runs that carry activations, one unit per run, role = assigned mode, under
    three labels. The released label equals the mode by construction, so its AUROC of 1.0 is arithmetic,
    not evidence; the two behavioural labels shipped in run_config.json are the informative rows."""
    in_probe = {}
    for r in json.load(open(meta_path, encoding="utf-8")):
        in_probe.setdefault(r["run_id"], int(bool(r["collusion_success"])))
    rc = {}
    for f in glob.glob(os.path.join(scen_dir, "qwen3_32b", "core", "*", "run_config.json")):
        c = json.load(open(f, encoding="utf-8"))
        if c["run_id"] in in_probe:
            rc[c["run_id"]] = c
    ids = sorted(in_probe)
    roles = [rc[i]["mode"] for i in ids]
    out = {"NARCBench / released label (= assignment)": {"roles": roles, "labels": [in_probe[i] for i in ids]},
           # collusion_success == (colluder_voted_target == len(coalition)): both colluders voted the target
           "NARCBench / shipped flag: coordinated": {"roles": roles,
                                                    "labels": [int(bool(rc[i]["collusion_success"])) for i in ids]},
           "NARCBench / shipped flag: target won": {"roles": roles,
                                                   "labels": [int(bool(rc[i]["target_majority"])) for i in ids]}}
    return out


if __name__ == "__main__":
    main(*sys.argv[1:6])
