# SUBMIT: everything, in order (about 40 min)

**Deadline:** 25 Oct 23:59 AoE = **Mon 26 Oct 17:29 IST**. Aim for Sunday evening.
Nothing here has been submitted, pushed or shared. Every outward step below is yours.

## Step 1 (10 min): decisions in `SUBMISSION.md`
- [ ] Read the **DECISIONS box** at the top:
  - headline (A) or (B);
  - P1 wording;
  - keep or drop the Lange † row;
  - M-S status.
- [ ] Then **delete the box.**
- [ ] Replace `«GITHUB URL»` in §7 (after Step 2).

## Step 2 (10 min): make the repo public
Publish **`ai-collusion\sprint\`** as the repository root. Exclude `__pycache__\`, `.pytest_cache\`,
`canary\prereg\failed-POS-attempt1\` (optional: it's archived and unanalysed) and `track3\` (the
other session's).

```powershell
cd C:\Users\shubha.achar\personal\ai-collusion\sprint
@"
__pycache__/
.pytest_cache/
track3/*
!track3/PREREG-Z2-anchor.md
!track3/z2_anchor.py
!track3/test_z2.py
!track3/z2/
!track3/analyze_t3.py
!track3/leniency.py
LINEAGE-2.3-submission.md
"@ | Set-Content .gitignore
git init
git add .
git commit -m "Apart AI Collusion Sprint, Track 2.3: four conditions for collusion evidence"
# create an empty PUBLIC repo on github.com, then:
git remote add origin https://github.com/sdachar/collusion-evidence-conditions.git
git branch -M main
git push -u origin main
```

- A secret scan was already run on `sprint\`: no API keys are in any file. The Groq key lives
  outside the folder, in `~\.groq_key`.
- **Before pushing, check `git status`.** Confirm no `*.key`, `.env` or `ext\` files are staged:
  third-party data is not redistributed.
- **Open the URL in a private window** to confirm the repo is public.

## Step 3 (15 min): the PDF
1. Open the official template:
   https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/copy?usp=sharing
2. Paste `SUBMISSION.md`, from the title down.
3. **Insert the figures by hand.** Markdown image lines don't render when pasted.
   - `report\fig1_canary.png` goes where `![Figure 1]` is, in §4.
   - `report\fig2_union.png` goes where `![Figure 2]` is, in §3.
   - Keep the captions.
4. Optional: put `CARD.md` as a one-page box before the appendices.
5. Check the abstract is ≤ 150 words (the draft has exactly 150 as of Sat 24 Oct; re-count after any
   edit, including M-S).
6. Insert all three figures: fig1_canary.png, fig2_union.png, fig3_compliance.png.
6. **Over length?** Cut in this order:
   1. §3's NARCBench caveat sentence (move it to Appendix D);
   2. §4's "This is the Athey–Bagwell setting…" paragraph, down to one sentence;
   3. §5's bullets 4–5 (move them to Appendix A).

   Never cut Table 1, Table 2, either figure, or Appendix A.
7. File → Download → PDF.

## Step 4 (10 min): the form
- **Project title:** `What Should Count as Evidence of AI Collusion? Four Conditions, Three Published Instruments, and a Randomised Test`
- **Project summary:** paste the abstract.
- **PDF:** from Step 3.
- **Track:** **Track 2 (Detection & Audit)**, question 2.3. Pick by name, not number.
- **Project code:** the GitHub URL.
- **Project image:** `report\fig2_union.png`, or `fig1_canary.png`.
- **Interested in publishing?** Yes.
- **Team:**
  - your name;
  - your city;
  - email `shubhaacharya098@gmail.com`;
  - your Discord handle.

## Step 5 (2 min): before you hit submit
- [ ] The PDF opens, and both figures are legible.
- [ ] No `«…»` placeholder and no DECISIONS box is left anywhere.
- [ ] The GitHub URL opens in a private window.
- [ ] The required appendix, "Limitations and Dual-Use", is present (Appendix A).

## After the sprint
- [ ] **Rotate the Gemini API key.** It was pasted into a chat transcript on 19 Oct.
- [ ] Optional, Tue 27 Oct: email Om Tailor (ColludeBench) the findings with the repo link.
