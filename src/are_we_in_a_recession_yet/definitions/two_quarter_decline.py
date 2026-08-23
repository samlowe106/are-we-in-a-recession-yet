"""The popular rule-of-thumb "technical recession" definition: a real
quarterly aggregate fell for two consecutive quarters.

Backs two of the site's cards -- real GNI and real GDP each get their own
verdict from this same function, called once per series (see
two_quarter_income_decline()'s own docstring for why they're checked
separately rather than merged into one verdict).
"""

from collections.abc import Sequence

from ..models import DataPoint, Verdict


def two_quarter_income_decline(
    real_income: Sequence[DataPoint], *, label: str = "real income"
) -> Verdict:
    """The popular rule-of-thumb definition: a real quarterly aggregate fell
    for two consecutive quarters. Framed around real income (GNI, or
    equivalently GNP -- the two are the same total by construction in the US
    national accounts, just computed via income vs. product), but the same
    two-quarter-decline shape is also the popular GDP-based "technical
    recession" definition -- pass `label` to describe whichever series
    `real_income` actually holds in the returned detail text. GDP and GNI
    aren't guaranteed to agree in practice despite being equal by
    construction (2022 Q1-Q2 is the textbook case: GDP declined both
    quarters, GNI didn't), so a caller checking both should call this twice,
    once per series, rather than average them into one verdict.

    Needs only the three most recent quarterly points: two quarter-over-
    quarter changes, both of which have to be declines. Doesn't require
    perfectly even quarterly spacing -- just the last three points in time
    order -- so a source with an occasional gap or a preliminary/revised
    duplicate for the same quarter still works as long as the three most
    recent entries really are three distinct quarters.
    """
    if len(real_income) < 3:
        raise ValueError("need at least 3 quarterly observations")
    ordered = sorted(real_income, key=lambda p: p.date)
    two_ago, one_ago, latest = ordered[-3], ordered[-2], ordered[-1]

    first_decline = one_ago.value < two_ago.value
    second_decline = latest.value < one_ago.value
    triggered = first_decline and second_decline

    def pct_change(a: DataPoint, b: DataPoint) -> float:
        return (b.value - a.value) / a.value * 100

    detail = (
        f"{label} {pct_change(two_ago, one_ago):+.1f}% then "
        f"{pct_change(one_ago, latest):+.1f}% over the last two quarters "
        f"({two_ago.date.isoformat()} → {one_ago.date.isoformat()} → {latest.date.isoformat()})"
    )
    return Verdict(triggered, latest.date, detail)
