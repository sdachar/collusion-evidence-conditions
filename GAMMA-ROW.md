# Draft §2 row: Bonjour et al.'s Γ, a fourth instrument of a fourth kind (information-theoretic)

**Draft by Claude, 19 Oct. Rewrite it in your own words before it goes in the paper.** Every number
comes from `SURVEY.md` §4.9b, which read it from Bonjour et al. (UAI 2022) Table 3 and the supplement.
Items marked `[derived]` are our arithmetic, not the paper's.

The instrument: pairwise net influence Γ(i;j) = γ(i;j) − max_k γ(k;j), with plug-in conditional
mutual information over actions. It flags collusion when Γ exceeds α = 0.05 in both directions. It is
the sprint's own 1.4 pointer, and no public implementation exists.

| Condition | Verdict | Evidence, all from its own tables |
|---|---|---|
| (i) Positives not defined by the role assignment | **FAIL** | The positives are self-implemented colluders in two hand-built synthetic environments, each programmed to condition its action on its partner's. There is no emergent or real-data positive. |
| (ii) Headline not carried by one statistic or the manipulated variable | **FAIL** `[derived]` | γ(i;j) measures the dependence the colluder was coded to create, so detection is by construction. And the threshold sits on the estimator's own plug-in bias floor: bias ≈ 54/N nats, which equals α at N ≈ 1,080, the sample size where the detection curve saturates. |
| (iii) Same-process placebo under the claimed FPR | **FAIL** | No FPR is reported anywhere. Its own non-colluding Table 3 rows score Γ = 0.0425 / 0.0424 bidirectionally (row 2, 15% under α) and 0.0761 one-directionally (row 3, 1.5× α). Any α that catches weak collusion (CP = 0.1) fires on independent random agents. |
| (iv) Uncertainty over the right unit | **FAIL** | There are no intervals and no significance test; the magic threshold is anti-conservative at the paper's own N `[derived]`. The calibrated χ² threshold is ≈ 0.067 nats at N = 1,000 against α = 0.05. |

**The one-line fix, which the paper never applies:** a permutation test that shuffles agent j's
actions within state strata. It is exact and takes about 1 s in numpy, so this row fails on reporting,
not on an impossible ask.

**Cost:** about 1 h to rewrite and fit into the table. The optional measured version, running Γ
against a scripted null, is about 5 h and is not in the plan.
