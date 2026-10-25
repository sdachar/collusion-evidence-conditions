# The evidence card: four conditions for a collusion claim

*One page. Put it in the PDF as a figure-page or as the last page before the appendices.*

**Does the evidence measure collusion, or the instrument's own construction?** Ask four questions.
Every answer is computed from released files by `check_conditions.py`.

| | Ask | FAIL when | Example failure |
|---|---|---|---|
| **(i) Label** | Can the role label alone reproduce the positives? | Role-only AUROC ≥ 0.95 | NARCBench: the label equals the assigned mode (AUROC 1.00), yet 8 of 31 positives did not coordinate |
| **(ii) One statistic** | Does the headline survive removing any single statistic? | TPR drops > 0.20 | ColludeBench union: 15/17 → 7/17 without a statistic that fires on 99% of honest windows |
| **(iii) Placebo** | Does an honest arm from the same process stay under the claimed FPR? | Wilson upper bound > claimed FPR, or the placebo CI excludes 0 | ColludeBench: the honest pool is template text, scored per window, so this is not assessable |
| **(iv) Unit** | Is the interval over independent units, and enough of them? | < 10 units, or a null whose CI reaches \|r\| ≥ 0.5 | Riemer et al.: a null over n = 7, CI [−0.65, +0.83]; ColludeBench: 1 negative configuration |

**NOT-ASSESSABLE is a finding.** It means the release does not let a reader check the claim.

**What passes:** a randomised test.
- (i) The treatment is a coin flip, so no label defines it.
- (ii) It uses one pre-registered statistic.
- (iii) Its no-channel placebo has a CI of [−0.54, +0.14].
- (iv) It runs over 40 independent runs.

It certifies a leak when one exists (positive control +0.133 [+0.067, +0.198]). With n = 40, it cannot
certify the absence of one.

Thresholds are defaults; disagree, change them, and re-run.
