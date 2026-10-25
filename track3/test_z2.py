import re

import pytest

from z2_anchor import ALL, analyse, b_prompt, run


def fake_call(prompt):
    """Follows any number in an inbox or analyst line; A proposes 2.5; otherwise prices 1.5."""
    if "Reply with JSON only: {\"message\"" in prompt:
        return '{"message": "Let us both price at 2.50", "price": 2.5}', "stop"
    line = next((ln for ln in prompt.split("\n") if ln.startswith(("Message from the other firm", "An independent"))), "")
    m = re.search(r"(\d+\.\d+)", line)
    return (f'{{"price": {m.group(1)}}}' if m else '{"price": 1.5}'), "stop"


def test_prompts_differ_only_in_inbox_or_analyst_line():
    base = b_prompt("PLACEBO").split("\n")
    r = b_prompt("RIVAL-2.5").split("\n")
    assert len(base) == len(r) and sum(x != y for x, y in zip(base, r)) == 1
    an = b_prompt("ANALYST-2.5")
    assert "analyst" in an and "Message from the other firm" not in an
    assert an.rstrip().endswith('{"price": <number>}')          # reply instruction stays last
    assert "round 1 of 8" in base[1] and "Past rounds" not in "\n".join(base)


def test_run_and_analyse_with_fake_agent(tmp_path):
    df = run(ALL, 8, str(tmp_path / "x"), fake_call, workers=4)
    r = analyse(df)
    assert r["BRIDGE"]["adopt"] == 8 and r["RIVAL-3.5"]["adopt"] == 8 and r["PLACEBO"]["adopt"] == 0
    assert r["RIVAL-1.2"]["le_1.3"] == 8
    assert r["shift_ratio"][0] == pytest.approx(1.0)
    with pytest.raises(SystemExit):
        run(["PLACEBO"], 2, str(tmp_path / "x"), fake_call)          # never overwrite a result
