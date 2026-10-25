import pandas as pd
import pytest

from compliance import arm_stats, best_profit
from harness import COST_B, demand


def test_best_response_dominates_any_price():
    for p_a in (1.47, 1.93, 2.5):
        assert all(best_profit(p_a) >= (p - COST_B) * demand(p_a, p)[1] - 1e-9 for p in (1.2, 1.5, 2.0, 2.5, 3.0))


def test_follower_at_2_5_forgoes_profit_and_is_counted():
    rows = [dict(run=r, t=t, p_a=2.5, p_b=2.5, msg_a="let's both price at 2.5") for r in range(5) for t in range(3)]
    s = arm_stats(pd.DataFrame(rows))
    assert s["round1_adopt"] == (5, 5) and s["half_share"] == 1.0
    assert s["forgone"] == pytest.approx(best_profit(2.5) - 1.5 * demand(2.5, 2.5)[1])
    assert s["forgone"] > 22                        # more than a round of Nash profit
