# K1 gate — ColludeBench recompute (run Thu 22 Oct 2026, two days late; plan deadline was Tue 20 22:00)

Source: `Ostailor/Steganographic_Collusion@main` (last push 2025-10-17, MIT, 3 stars), individual files
fetched raw into `..\..\..\ext\colludebench\files\` (the GitHub zip endpoint stalled twice). Paper:
arXiv 2510.04303 PDF, 13 pp, `..\..\..\ext\arxiv\2510.04303.pdf`. Script: `00_reproduce_one.py`.

## Result: K1 PASSES as written, and the headline finding changes shape

1. **Every single-detector number in the committed `metrics.md` recomputes exactly** from the score
   lists and thresholds in the committed `metrics.json` (16/16 cells, rule `value > thr`, `<` for
   `permutation_invariance`, as in `auditor/metrics.py:146`). The pipeline is internally consistent.

2. **The committed artifact is not the run behind the paper's Table 1 (p. 7).** Only `acceptance_bias`
   matches:

   | Detector | Paper Table 1, TPR@1e-2 / @1e-3 | Committed `metrics.json` |
   |---|---|---|
   | cross_run_mi | 0.658 / 0.598 (ROC AUC 0.819) | 0.045 / 0.033 (AUC 0.885) |
   | watermark_variance | 0.504 / 0.504 (AUC 0.752) | 0.176 / 0.176 (AUC 0.588) |
   | union Bonferroni | **1.000** / 0.889 | **0.333** / 0.333 |
   | union Holm-Bonferroni | 0.667 / 0.556 | 0.750 / 0.750 |
   | union Westfall-Young | 0.667 / 0.556 | 0.750 / 0.750 |
   | union martingale | 0.667 / 0.667 | 0.750 / 0.750 |
   | acceptance_bias | 1.000 / 1.000 | 1.000 / 1.000 (match) |

   The paper text (p. 6) also claims welfare_shift TPR 0.955 at FPR 0; committed `metrics.md` shows
   welfare_shift with no calibrated threshold (TPR 0.000, key None), yet the Holm union's committed
   rejections credit `welfare_shift` for 6 of 9 colluding scenarios. Unresolved; tier 1.

   **Implication for P1.** P1 predicted the two cross_run_mi numbers (0.658, 0.12) come from different
   subsets with only one reproducing. Neither 0.658 nor 0.598 is in the committed artifact at all.
   P1 needs re-wording before the sprint (her call), e.g. "Table 1 does not reproduce from the
   committed output; the committed output reproduces itself."

3. **Sample sizes behind "zero observed false alarms".**
   - `acceptance_bias`: **3 positives, 1 negative.** "FPR = 0.000 at the 1e-3 budget" rests on one
     honest run; Wilson 95% on 0/1 is [0, 0.79]. This is the condition-(iii) placebo-power failure in
     its purest form, and acceptance_bias is the detector the union's TPR leans on in review.
   - `permutation_invariance`: FPR **0.990** at the 1e-2 budget (fires on 99% of honest runs, TPR 0.996)
     — it does not discriminate. Not in Table 1.
   - `cross_run_mi`: 16,415 positives vs 119,960 negatives — these are pair/window units, not runs
     (manifest has 600 runs). The unit-of-analysis question (condition iv) is live.

4. **Run count (F4):** `dataset_manifest.json` lists **600 runs: 200 each of first_price_auction,
   peer_review, pricing_duopoly.** The paper describes four environments; the continuous double auction
   is absent from the manifest (its audit logs exist under `results/audit/logs/`).

5. **Scooping signal:** one fork, `nathanwkwong/Steganographic_Collusion-fork-sprint`, created
   2026-10-16, identical to upstream (0 commits ahead). Probably another sprint participant. Re-check Fri.

## ⟲ Corrections, Thu 22 evening, after REVIEW-fable-2026-10-22.md (M5). Numbers stand; framing changes

- **(2) is too broad.** The paper's **ablation paragraph (p. 8) reproduces exactly** from the committed
  `ablation.json`: cross_run_mi 2/17 = 0.12, permutation 12/17 = 0.71, acceptance_bias 4/17 = 0.24,
  MI+perm 12/17, acceptance+perm 15/17 = 0.88. So the finding is: **the same commit reproduces the
  ablation section and not Table 1.** It is not "the artifact is not the paper's run".
- **(3) acceptance_bias's one negative is one negative *configuration*,** an aggregate over the
  review_honest calibration pool, not one honest run. Every one of the 510 ablation entries has
  tp + fn = 17 and fp + tn = 1 (re-verified, `inspect_ablation.py`). **The artefact's real evaluation
  unit is 17 positive and 1 negative configuration,** and the committed stderr (8.4e-5) treats
  per-window scores as independent. This is the condition (iv) FAIL in `specs.json`.
- **(4) "600 runs over 3 environments, not 4" is the wrong finding.** The manifest lists only
  `results/calibration/` transcripts: 200 honest seeds × 3 tasks, which matches the paper's calibration
  claim (p. 6), and **zero experiment or sweep transcripts.** The sharper finding: **no colluding run is
  in the integrity manifest.** The 4th environment exists in code (`auditor/metrics.py:20`).
- **"Neither 0.658 nor 0.598 is in the committed output"** is true of `metrics.md`. In `metrics.json`
  those substrings occur only inside ROC/PR curve arrays.
- **watermark_variance has threshold 0.0, and every negative is exactly 0.0.** So "FPR 0" is a floor
  artefact: under `>=` it would be FPR 1.0. `check_conditions` now takes the instrument's own rule
  (`>` here).
- **The template-honest pool is not a placebo for the LLM claim.** The committed negatives contain no
  LLM-honest values. Say this explicitly rather than calling them "the closest released thing".
- **cross_run_mi (iii) "PASS" is withdrawn → NOT-ASSESSABLE.** Its 119,960 scores are non-independent
  windows.

## Not yet done from the Tue-20 gate list
- (3b) configs by agent class (F6); (4) read the agent/channel files and LLM configs; (5)
  `regenerate_results.py --dry-run` and pytest run time — need the full tree (zip endpoint stalled;
  fetch by tree API if needed); (7) copy the bootstrap kit; (9) NARCBench gate.
