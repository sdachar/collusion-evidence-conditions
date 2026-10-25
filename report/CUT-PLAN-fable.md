# CUT-PLAN-fable — ~600 words off the body of `overleaf/main.tex`

Source: `sprint\report\overleaf\main.tex` as of Sun 25 Oct (505 lines). Line numbers below refer to
that file. Mirror every change in `SUBMISSION.md`. Counts are from a rough de-TeX (`$…$` collapses to
one token; `\cite`/`\code` arguments kept), so treat per-item savings as ±10%.

## 0. Strategy in five lines

1. A judge reads, in order: Abstract → Contributions → conditions table → Table 1 verdicts → figures
   → Limitations → Conclusion. Those carry Impact, Novelty and Rigour; none is touched.
2. Clarity is where this audience docks (R3 on the prior paper: "quite dense… move secondary details
   to the appendix"). Cuts come from narration, restatement and secondary numbers, not from
   evidence sentences (anything with a CI, a count, a pre-registered outcome or a placebo).
3. Redundancy map: Conclusion ≈ Abstract ≈ Discussion lead; Related Work §1 ≈ Intro para 1 ≈ §4.1
   openers; §3.2 Audit procedure ≈ §4.1 openers; "What did not work" ≈ Appendix B (A1, P4) ≈
   Appendix A item 5; Limitations bullet 4 ≈ M-S paragraph; Worked-case para 2 restates para 1.
4. Prefer MOVE to an appendix (free) over DELETE wherever a judge might want the number.
5. 4 pages is not reachable with three figures and three tables kept; the realistic landing is ~6
   template pages (within Apart's 4–8 norm). Non-word levers at the end (§6) buy another ~0.5 page.

## 1. Word count per body section, now → target

| Section | Prose now | Prose + floats | Cut | Target | Template budget |
|---|---|---|---|---|---|
| Abstract | 141 (150 by whitespace) | 141 | 0 | 141 | fixed |
| 1 Introduction | 272 | 272 | −24 | 248 | Intro+RW 1 page (~450) |
| 2 Related Work | 221 | 221 | −51 | 170 | ↑ (418 together: fits) |
| 3 Methods | 400 | 526 | −117 | 283 | Methods+Results 2.5 pages |
| 4 Results | 980 | 1392 | −251 | 729 | ↑ (1012 prose + floats ≈ 3.5 pp) |
| 5 Discussion & Limitations | 297 | 297 | −119 | 178 | 0.5 page (~250) |
| 6 Conclusion | 87 | 87 | −11 | 76 | ↑ (254 together: fits) |
| Table 2 caption (on page) | 95 | — | −30 | 65 | — |
| **Body total** | **2398** | **2936** | **−603** | **1795 / ~2300 with floats** | |

Raw token count including all table cells and math: 2917 → ~2300.

## 2. Ranked cut list (score-safety × size)

Format: **[id] location — ACTION — saves N**. Exact text in `code`. Why it is safe in italics.

### A. Discussion / Conclusion (−130)

**[D1] §5 Discussion lead, lines 328–333 — REPLACE — saves 46.**
Current: `\textbf{Discussion.} Collusion evidence should be judged on whether it is about collusion, not only on its headline. … and can be produced by plain compliance.` (95 w)
Replace with:
```latex
\textbf{Discussion.} Across three instrument kinds the failures share a cause: the positive class,
the null or the honest baseline is defined by the experimenter's construction, not by the agents'
behaviour. When the auditor controls the generator the remedy is cheap: randomise a private variable
and test whether it moves.
```
*Sentence 1 ("judged on whether it is about collusion") is the Conclusion's first sentence; the last
sentence (measure-dependence, compliance) is stated with numbers in §4.2 "Measure choice" and in the
§4.3 title. The two ideas that exist nowhere else — shared cause, cheap remedy — are kept.*

**[D2] §5 Limitations bullet 4, lines 346–347 — MOVE to Appendix A item 6 (Scope) — saves 26.**
Current: `\item \textbf{The price-level comparison (M vs P-0) confounds the channel with prompt framing.} M-S was added for this, and cannot separate exposure from framing.`
Append to App. A item 6: `The M vs P-0 price comparison confounds the channel with prompt framing; M-S was added for this and cannot separate exposure from framing.`
*Verbatim duplicate of the M-S paragraph's "M-S cannot separate exposure from framing", which stays in §4.2 ([R7]).*

**[D3] §5 Limitations bullet 2, lines 340–342 — REPLACE — saves 16.**
Current: `\item \textbf{We ran one instrument ourselves.} The three audits use released files. Several verdicts are NA because per-unit data is not released: a statement about releases, not a proof that the instruments fail.`
Replace with: `\item \textbf{The three audits use released files only.} NA verdicts are statements about what is released, not proof that the instruments fail.`
*Keeps the hedge that protects headline B from "you proved nothing"; drops two filler sentences.*

**[D4] §5 Future work, lines 352–355 — REPLACE — saves 23.**
Replace with:
```latex
\textbf{Future work.} Antitrust price screens (coefficient of variation, relative distance) ported
to LLM pricing logs, and leniency for AI cartels: B adopts A's explicit price proposals in 83--98\%
of rounds, a reportable agreement. Both held to the same four conditions.
```
*Future work does not score; the leniency hook (Impact) is kept in one clause.*

**[D5] §5 Limitations bullet 5, lines 348–349 — REPLACE — saves 8.**
Replace with: `\item \textbf{Five claims made during the sprint were retracted} after independent review (Appendix~\ref{app:corrections}).`
*Keeps the pointer (R3 praised exactly this); drops the frame.*

**[D6] §6 Conclusion, third sentence, lines 361–364 — REPLACE — saves 11.**
Keep sentences 1–2 verbatim (headline B wording is settled). Replace from `A randomised test built to the standard passes all four, and on LLM pricing agents it separates…` to end with:
`A randomised test built to the standard passes all four; on LLM pricing agents it finds prices past monopoly with no profit gain, no detectable cost leak, and a follower whose lockstep is compliance with whatever number it is shown.`
*Same content, fewer connectives; "separates price coordination from information flow" is the Abstract's job.*

Running total: **130**.

### B. Results (−251)

**[R1] §4.2 M-S paragraph, lines 284–290 — REPLACE, details MOVE to Appendix B (A6) — saves 63.**
Current: `\textbf{Does the rise need a live partner?} M-S's primary estimate is $R=…$ … and its CI contains 0 ($+0.003$ [$-0.212$, $+0.218$]).` (98 w)
Replace with:
```latex
\textbf{Does the rise need a live partner?} No. M-S, where B reads a stored M message from a
different run, reproduces $R=0.96$ [0.68, 1.40] of M's rise over P-0 (M-S $-$ M $=-0.045$ [$-0.448$,
$+0.338$]); a CI below 0.5 would have indicated within-pair coordination. Exposure to any price
proposal, or the shared framing, produces it, and M-S cannot separate the two. Because its inbox is
independent of $c_A$, M-S is also a channel-open placebo, and its canary CI contains 0
(Table~\ref{tab:canary}).
```
Append to Appendix B after `\textbf{A6} M-S, post hoc;`: `(primary estimate $R=(\text{M-S}-\text{P-0})/(\text{M}-\text{P-0})$, pre-set threshold 0.5; M-S $-$ P-0 $=+1.060$ [$+0.737$, $+1.360$])`.
*The level difference and the M-S canary CI are both already cells in Table 2; the R definition is a
footnote-grade detail. The placebo sentence and the "cannot separate" hedge stay. The user flagged
"M-S details" as the redundancy to target.*

**[R2] §4.2 "Measure choice decides the verdict", lines 274–282 — REPLACE — saves 36.**
Replace with:
```latex
\textbf{Measure choice decides the verdict.} With a channel, prices rise by $+1.1$ (M) and $+1.4$
(M+P) over the placebo (Figure~\ref{fig:canary}b); the median $p_B$ is 2.5 in both (P-0: 1.45),
above the monopoly price of 1.93. Profits do not rise: $\Delta$ is negative in every open arm and not
detectably higher than the placebo's (M $-0.54$, M+P $-0.77$, P-0 $-0.61$); only POS, whose proposal
is cost $+1$, approaches monopoly profit ($+0.84$). A price-level detector would flag M and M+P as
collusive; a profit index would not; the information-flow test answers a third question, and finds
no private cost moving at a detectable size.
```
*Drops "past the joint-profit optimum" (restates "above monopoly"; Fig 2 caption says it) and the
narration sentence "coordinate explicitly on price, but on prices that harm consumers and the firms
alike…" — its content is the three-measure sentence that follows. Every number survives.*

**[R3] §4.1 NARCBench, lines 232–235 — REPLACE, caveat MOVE to Appendix B (P8) — saves 23.**
Current: `\emph{Caveat:} the paper's selection may rest on a transcript judgment that is not shipped, so we state that the shipped flag disagrees with the label, not that the label is wrong. No Verdict tier is released, so the pre-registered scenario-level interval (P8) cannot be computed.` (48 w)
Replace with: `The paper's selection may rest on an unshipped transcript judgment (caveat in Appendix~\ref{app:prereg}), so the claim is that the shipped flag disagrees with the label, not that the label is wrong; no per-scenario tier is released, so (iv) is NA (P8).`
Append to Appendix B "Other instruments" P8: `Caveat on (i): NARCBench's selection may rest on a transcript judgment that is not shipped; we state only that the shipped \code{collusion\_success} flag disagrees with the released label.`
*The hedge stays in the body in short form (tone matters: "about an instrument, never an author");
the P8 sentence was verbatim in Appendix B already.*

**[R4] §4.1 ColludeBench, lines 197–201 — REPLACE, numbers MOVE to Appendix B (P1) — saves 22.**
Current: `All 16 single-detector cells in the committed \code{metrics.md} recompute exactly from \code{metrics.json}, and the paper's ablation paragraph (p.~8) reproduces exactly from \code{ablation.json}. The paper's Table~1 (p.~7) does not: only \code{acceptance\_bias} matches; \code{cross\_run\_mi} reads 0.658/0.598 in the paper vs 0.045/0.033 committed, and the Bonferroni union reads 1.000 vs 0.333.` (49 w)
Replace with: `All 16 single-detector cells in the committed \code{metrics.md} and the paper's ablation paragraph (p.~8) recompute exactly from the committed JSON; ColludeBench's Table~1 (p.~7) does not (Appendix~\ref{app:prereg}, P1).`
Append to Appendix B P1: `Only \code{acceptance\_bias} matches; \code{cross\_run\_mi} reads 0.658/0.598 in the paper vs 0.045/0.033 committed, and the Bonferroni union 1.000 vs 0.333.`
*Also fixes review item S1 ("Table 1" ambiguity) by naming the owner. The non-reproduction is a
finding about the release, not about the four conditions — appendix-grade.*

**[R5] §4.1 Riemer, lines 221–225 — REPLACE — saves 20.**
Current from `Their Table~3 correlations (PDF p.~9) are over…` to `…not evidence that CoT monitoring works.` (65 w)
Replace with:
```latex
Their Table~3 correlations (PDF p.~9) are over \textbf{$n=7$ steering magnitudes}, recovered from the
$r$/$p$ pairs on four cells; the headline $r=0.194$ then has a 95\% CI of \textbf{$[-0.65,+0.83]$},
which includes the same table's $r=0.771$ (``will this agent raise its price?''). A null needs a CI
that rules out a strong effect; this one is uninformative, which is not evidence that CoT monitoring
works.
```
*Same four facts (n=7, how recovered, CI, contains 0.771), one fewer sentence.*

**[R6] §4.3 Worked case para 1, lines 305–307 — MOVE to Appendix B (Canary) — saves 20.**
Current: `B's prices are multiples of 0.5 in 66\% (M) and 78\% (M+P) of rounds, against 24\% in P-0.`
Append to Appendix B Canary paragraph: `Round numbers: B's prices are multiples of 0.5 in 66\% (M), 78\% (M+P) and 24\% (P-0) of rounds.`
*A third compliance statistic after round-1 adoption and forgone profit; the first two make the point.*

**[R7] §4.3 Worked case para 2, lines 313–314 — DELETE — saves 17.**
Current: `Lockstep here is obedience to whichever number is in the prompt, not a strategy sustained by incentives.`
Keep the following sentence, reworded to stand alone: `A claim of collusion therefore has to show that the coordination is sustained by incentives, not only that prices move together.`
*Para 1 already closes with "A colluder holds a high price because deviating is punished later; this
follower gives up profit with nothing to fear." The section title says "compliance, not collusion".*

**[R8] §4.1 ColludeBench, lines 208–209 — MOVE to Appendix B (after P2) — saves 18.**
Current: `\code{watermark\_variance}'s ``FPR 0'' is a floor effect (threshold 0.0; every honest score is exactly 0.0).`
*A second statistic's FPR artefact; the (ii) finding rests on `permutation_invariance`, which stays in full.*

**[R9] §4.1 ColludeBench, lines 210–211 — REPLACE — saves 12.**
Current: `The honest pool is template-generated, so it is not a placebo for a claim about LLM agents, and the integrity manifest lists 600 honest calibration runs and no colluding run.`
Replace with: `The honest pool is template-generated (600 calibration runs, no colluding run), so it is not a placebo for a claim about LLM agents.`
*Placebo point kept verbatim in substance; the manifest detail becomes a parenthesis.*

**[R10] §4.1 NARCBench, lines 228–232 — REPLACE — saves 8.**
Replace `By the authors' own \code{collusion\_success} flag (both colluders voted for the target), 8 of the 31 positives did not coordinate; in 6, no colluder voted for the target. Only 2 of 31 swung the vote (\code{target\_majority}). On these behavioural labels (i) passes…` with
`By the authors' own \code{collusion\_success} flag, 8 of the 31 positives did not coordinate (in 6, no colluder voted for the target) and only 2 swung the vote (\code{target\_majority}); on these behavioural labels (i) passes…`

**[R11] §4.3 Worked case para 1, lines 304–306 — REPLACE — saves 6.**
`Following costs B 29.7 profit per round in M [24.1, 35.5] and 31.5 in M+P [24.5, 38.4] against a best response to A's actual price: more than a full round of Nash profit (22.2); P-0 shows 7.9 [5.3, 11.0].` →
`Following costs B 29.7 [24.1, 35.5] (M) and 31.5 [24.5, 38.4] (M+P) profit per round against a best response to A's actual price, more than a round of Nash profit (22.2); P-0: 7.9 [5.3, 11.0].`

**[R12] §4.3 Worked case para 2, lines 310–313 — REPLACE — saves 6.**
`In Z2, B priced at the rival's proposed 1.20, 1.50, 2.50 and 3.50 in 39, 40, 40 and 40 of 40 calls, downward as readily as upward and below the Nash price at 1.20 (Figure~\ref{fig:compliance}); it followed an ``independent analyst's'' number almost as closely (shift ratio 0.97 [0.91, 1.00]) and a live A's real message in 36 of 40.`

Running total: **130 + 251 = 381**.

### C. Methods (−117)

**[M1] §3.2 Audit procedure, lines 132–139 — MOVE to Appendix C, retitled "Audit procedure and reproduction" — saves 74 (94 moved, ~20 pointer added).**
Replace the subsection with one sentence appended to the §3.1 paragraph at line 127:
`The per-instrument procedure (recompute from the committed JSON and leave-one-statistic-out over the 255 subsets for ColludeBench; $n$ recovered from the published $r$/$p$ pairs and Fisher-$z$ intervals for Riemer et al.; a 62/62 metadata join for NARCBench) is in Appendix~\ref{app:repro}.`
*Each §4.1 paragraph opens by stating what was computed ("recompute exactly", "inverting the r/p
pairs recovers n=7", "released label equals the assigned mode"), so the body already carries the
method; the subsection is the one block that Results restates sentence for sentence. Appendix C is
the natural home: it already lists the commands and source files. The pointer keeps the three rigour
tokens (255 subsets, Fisher-z, 62/62). Risk: lowest-ranked of the large items because a Rigour judge
skimming Methods sees one sentence instead of a subsection — if page count allows, skip this one
and take the §6 non-word levers instead.*

**[M2] §3.1 line 129–130 — DELETE — saves 20.**
Current: `Every downloaded file was treated as untrusted data and read with Python in isolated mode; no third-party code was executed.`
*Verbatim in Appendix A item 5 ("Untrusted inputs"). The P4 reason survives in [M3].*

**[M3] §3.3 "What did not work", lines 167–169 — DELETE, fold A1 and P4 — net saves 11.**
Delete the paragraph (42 w). Append to the Inference bullet (line 153–154): `A within-run permutation test, invalid on the same scripted agents, was replaced by this estimator (A1).` (+16). Append to the §3.1 pointer sentence from [M1] (or, if [M1] is skipped, to the ColludeBench item of §3.2): `A \code{grep} baseline (P4) was not run: it needs regenerated transcripts, hence third-party code.` (+15).
*Both negatives stay in the body; both are already in Appendix B (A1, P4) and the P4 reason in
Appendix A item 5. What goes is a heading and the duplication.*

**[M4] §3.1 line 127–128 — REPLACE — saves 6.**
`\code{build\_specs.py} builds a JSON spec per instrument from its released files; \code{check\_conditions.py} emits the verdict card (Table~\ref{tab:verdicts}).`

**[M5] §3.3 bullet 3 header, line 149 — REPLACE — saves 6.**
`\textbf{Why no model of the agents is needed:}` → `\textbf{Identification:}`
*The bullet's content makes the point; the long header is a label.*

Running total: **381 + 117 = 498**.

### D. Related Work (−51)

**[W1] §2 "Detecting AI collusion" + "Gap", lines 83–89 and 102–104 — REPLACE (merge) — saves 37.**
```latex
\textbf{Detecting AI collusion.} Motwani et al.\ \cite{motwani} define secret collusion via
steganography and bound black-box detection; Lange et al.\ \cite{lange} show that a trained
stegosystem evades a text classifier but not a logit classifier. The three instruments we audit
\cite{tailor,riemer,narc} each propose or test a detector (\S3). We found no shared standard for
when such an instrument's output counts as evidence, and no audit that applies one standard across
statistical, judge-based and activation-based instruments; we ask what the evidence must satisfy,
and score them on it.
```
*The one-line descriptions of ColludeBench, Riemer and NARCBench are repeated in the Contributions
list and again as the first sentence of each §4.1 paragraph. The novelty claim ("Gap") is kept.*

**[W2] §2 "Algorithmic collusion in economics", lines 91–95 — REPLACE — saves 14.**
```latex
\textbf{Algorithmic collusion in economics.} Calvano et al.\ \cite{calvano} show that Q-learning
pricing agents reach supra-competitive prices; we use their profit index $\Delta$. Athey and Bagwell
\cite{athey} show that efficient collusion under private costs requires cost communication, the leak
our canary tests for with LLM agents; Dechenaux and Mago \cite{dechenaux} ran that setting with
human subjects.
```
Antitrust paragraph (lines 97–100): keep unchanged — it is the Impact bridge and the only `\cite{textmsg}`.

Running total: **498 + 51 = 549**.

### E. Introduction (−24)

**[I1] §1 para 1 last sentence + para 2, lines 57 and 59–62 — REPLACE (merge) — saves 13.**
Delete `We answer with a standard, not a new detector.` from para 1. Replace para 2 with:
```latex
We answer with a standard, not a new detector, and the choice is deliberate: black-box optimisation
against steganographic collusion is intractable \cite[Thm.~2]{motwani}, so a detector cannot be
validated by an optimiser's failure to beat it. What can be checked is whether the evidence it
produces is about collusion rather than about its own construction.
```

**[I2] §1 Contribution 3, lines 75–77 — REPLACE — saves 11.**
`\item \textbf{A randomised canary test}, pre-registered and hashed before any LLM call, that passes all four and finds explicit price coordination without detectable private-information flow.`

Running total: **549 + 24 = 573**.

### F. Captions (on-page words; −30)

**[T1] Table 2 caption, lines 241–246 — REPLACE — saves 30.**
```latex
\caption{Canary results (\code{canary/report.py} $\to$ \code{prereg/report.json}); effects in price
units, 95\% CI. MDE = minimum detectable effect ($2.8\times$SE). Emission = share of A's messages
containing A's true cost. $\Delta=(\pi-\pi_{\text{Nash}})/(\pi_{\text{mon}}-\pi_{\text{Nash}})$
\cite{calvano,riemer}, per firm per round, run-level bootstrap CI. $\ddagger$ M-S: B's inbox holds
another run's M message; 62\% is adoption of that message; A's own message (5\% emission) is never
delivered.}
```

**Running total: 573 + 30 = 603.** Target met with every item above.

### G. Buffer (take if the PDF still overshoots; not in the total)

| id | Item | Saves | Cost |
|---|---|---|---|
| B1 | §5 Future work → MOVE whole paragraph to the end of Appendix A as item 7 "Next steps" | +33 over [D4] | loses the leniency hook from the body |
| B2 | [D1] lead to one sentence (shared cause only); fold "cheap remedy" into Conclusion sentence 3 | +15 | Conclusion gets a clause longer |
| B3 | Fig 2 caption last sentence `Prices above the monopoly price lower joint profit (Table~2, $\Delta$).` → DELETE | +10 | caption less self-contained |
| B4 | §4.3 para 1 opener `Here it is something else.` → DELETE | +5 | loses a beat |

With all buffer items: ~666.

## 3. Running total

| Block | Items | Saves | Cumulative |
|---|---|---|---|
| Discussion/Conclusion | D1–D6 | 130 | 130 |
| Results | R1–R12 | 251 | 381 |
| Methods | M1–M5 | 117 | 498 |
| Related Work | W1–W2 | 51 | 549 |
| Introduction | I1–I2 | 24 | 573 |
| Table 2 caption | T1 | 30 | **603** |
| Buffer | B1–B4 | +63 | 666 |

If [M1] is skipped for Rigour optics: 529 + B1 + B2 + B3 = 587 — then take B4 and the §6 levers.

## 4. Considered and rejected

| Candidate | Why rejected |
|---|---|
| §4.2 "Pre-registered predictions" (76 w) | Protected negatives (P3 null, P4 M+P failure); review §5 says do not soften. |
| §4.2 "Emission vs inference" incl. `B's price equals A's same-round price in 82%/99%/16%` | Protected (emission-vs-inference); the same-round statistic is the lockstep measure §4.3 opens on. |
| ColludeBench credit sentence (line 195–197) | Tone; review §5: "do not sharpen". Compressing saved 4 words. |
| ColludeBench 99% / 510-entries / "17 positive, 1 negative" sentence | It is the (ii)+(iv) evidence and the Abstract's "fires on 99% of honest windows" rests on it. |
| Contribution 2 wording (lines 70–74) | Headline B exact wording is settled; this is the only place the NARCBench-(i)-passes-on-behavioural-labels poke is pre-empted ("on at least one of them"). |
| Intro para 1 three-way list and "headline number" parallel | Sets up Table 1's columns and the three-kinds claim; 68 words that earn their place. |
| Canary bullets (Market, Each round, Identification, Inference, Model) and Arms paragraph | The identification argument is the Rigour core; arms define Table 2's rows; "added after seeing M; labelled post hoc" is a reported negative. |
| Z2 methods paragraph (line 163–165) | Figure 3 and §4.3 para 2 depend on it. |
| Worked case: round-1 adoption 34/40, 38/40 and forgone-profit sentence | The "not collusion" evidence; only tightened ([R11]). |
| Limitations bullets 1 and 3 | Bullet 1 is the necessary-not-sufficient hedge; bullet 3 carries MDE and the "one prompt per arm" clustering point (R3's critique, S5). |
| Antitrust Related-Work paragraph | Impact bridge; sole `\cite{textmsg}`. |
| Compressing §3.2 in place instead of moving it | Tried: the subsection is already terse; a rewrite saved 6 words. Only the move ([M1]) yields anything. |
| Table 1 caption † note | Explains the Lange row, which is the "card can return a pass" evidence. |
| Riemer first sentence (flat 32–34%) | Becomes the only statement of the instrument once [W1] removes it from Related Work. |
| Any figure, table, column, or the Limitations & Dual-Use appendix | Protected. |
| Abstract | Fixed at 150. |

## 5. Risk check — what the cuts touch elsewhere

**Labels and `\ref`s.**
- `fig:canary`: referenced only in "Measure choice" → [R2] replacement keeps `Figure~\ref{fig:canary}b`. ✔
- `fig:union`: referenced at line 203 (kept). ✔  `fig:compliance`: referenced in [R12] replacement. ✔
- `tab:canary`: referenced in Fig 2 caption; [R1] adds a second reference. ✔
- `tab:verdicts`: referenced in [M4]. ✔  `tab:conditions`: has a label but is never `\ref`'d today (pre-existing); optionally write `(Table~\ref{tab:conditions})` in [M4].
- `app:prereg`: line 143 (kept) + new pointers in [R3], [R4]. ✔  `app:corrections`: [D5] and LLM statement. ✔  `app:repro`: Code and Data + new [M1] pointer. ✔  `app:dualuse`: Code and Data. ✔
- No `\ref` points at the "What did not work" paragraph or §3.2 heading. ✔
- `(\S3)` in [W1] is a literal, no label needed.

**Citations.** After [W1]/[W2] every `\bibitem` is still cited in the body: motwani (§1, §2), tailor/riemer/narc (§1, §2, §3, Table 1), lange (§2, Table 1), textmsg (§2), athey, dechenaux, calvano (§2; calvano also Table 2 caption). ✔

**Numbers that move (and their new home).**
- 0.658/0.598 vs 0.045/0.033, Bonferroni 1.000 vs 0.333 → Appendix B P1 ([R4]). P1 already says "0.658 does not appear in `metrics.md`" — consistent. Also write "ColludeBench's Table 1" there (review S1).
- `watermark_variance` floor effect → Appendix B after P2 ([R8]).
- Multiples-of-0.5 66/78/24% → Appendix B Canary ([R6]).
- R definition, threshold 0.5, M-S − P-0 = +1.060 [+0.737, +1.360] → Appendix B A6 ([R1]). +1.060 is also a Table 2 cell. ✔
- NARCBench caveat → Appendix B P8 ([R3]); short form stays in body.
- Limitations bullet 4 → Appendix A item 6 ([D2]); "cannot separate" also stays in [R1]. ✔
- §3.2 → Appendix C ([M1]); A1 → Inference bullet; P4 → §3.1 pointer ([M3]). Appendix A item 5 still says "This is why ColludeBench's transcripts were not regenerated (P4)". ✔

**Claims the Abstract relies on, all still in the body:** 15/17 → 7/17 (line 202–203), 99% of honest windows (line 205), n = 7 (R5), AUROC 1.00 (line 228), prices past monopoly / no profit gain / no detectable leak ([R2]), "copies any proposed number, low or high, from any speaker" ([R12]). ✔

**Headline B wording:** untouched in §1 (Contribution 2) and §6 (sentences 1–2). ✔

**Appendix D rows:** row 2 ("explicit price flow") still supported by [R2]'s "price-level detector would flag"; row 5 by [D3]. ✔

**Twin file:** every item must be mirrored in `SUBMISSION.md`; the markdown uses the same paragraph text, so the `old_str`s above locate there too (minus LaTeX).

**Counting caveat:** the de-TeX collapses each `$…$` to one token, so Results items with maths ([R1], [R2], [R5]) may save 5–10% more than listed in the rendered PDF, and Table 2's caption likewise. Re-run a page count after applying A–F before touching G.

## 6. Non-word levers (page space only; outside the brief but cheap)

- Figure widths: `fig2_union` 0.78 → 0.6 `\textwidth`; `fig3_compliance` 0.7 → 0.55. ≈ 0.4 page.
- Tables 1 and 2 are already `\small`/`resizebox`; the conditions table could take `\footnotesize` without losing legibility. ≈ 0.1 page.
- `[H]` floats force page breaks around every float; `[t]` lets LaTeX pack them. ≈ 0.3 page, at the cost of figures drifting from their first mention.
- `\setlist{nosep}` is already on; `\captionsetup{font=small}` is on. Nothing further here.

Expected landing after A–F: ~2,300 on-page words + 6 floats ≈ 6 template pages; with §6 ≈ 5.5.
