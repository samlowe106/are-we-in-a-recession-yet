"""A generic N-consecutive-months-of-decline check, generalized so it can be
applied to any one of NBER's Business Cycle Dating Committee's own coincident
indicators (nonfarm payrolls, real personal income less transfers, real
personal consumption expenditures, industrial production) -- one call per
series, each its own card/verdict on the site, all sharing this one function.
"""

from collections.abc import Sequence

from ..models import DataPoint, Verdict


def consecutive_decline(points: Sequence[DataPoint], *, min_months: int = 6) -> Verdict:
    """Triggers when a monthly series has fallen for at least `min_months`
    consecutive months -- the same "N periods of straight decline" shape as
    two_quarter_income_decline(), generalized to a monthly cadence so it can
    be applied to any of the individual series NBER's Business Cycle Dating
    Committee actually looks at (nonfarm payrolls, real personal income less
    transfers, real personal consumption expenditures, industrial
    production), one call per series.

    Deliberately does NOT combine multiple series into one verdict -- NBER's
    real process is a holistic judgment call across several indicators at
    once ("deep, pervasive, and persistent" declines), but approximating
    that by requiring several series to agree, or averaging them into one
    number, would mean bending each series's own honest reading to fit a
    consensus. A caller that wants several of these side by side (see the
    site's own fetch script) should call this once per series and show each
    result independently, not merge them here.
    """
    if len(points) < min_months + 1:
        raise ValueError(f"need at least {min_months + 1} monthly observations")
    ordered = sorted(points, key=lambda p: p.date)

    streak = 0
    for i in range(len(ordered) - 1, 0, -1):
        if ordered[i].value < ordered[i - 1].value:
            streak += 1
        else:
            break

    triggered = streak >= min_months
    latest = ordered[-1]
    detail = f"{streak} consecutive month{'s' if streak != 1 else ''} of decline (needs {min_months}+ to trigger)"
    return Verdict(triggered, latest.date, detail)
