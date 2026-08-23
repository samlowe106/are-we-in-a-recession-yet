"""The 10-year/3-month Treasury yield curve: a leading, not coincident,
recession indicator.
"""

from collections.abc import Sequence

from ..models import DataPoint, Verdict


def yield_curve_inversion(spread: Sequence[DataPoint]) -> Verdict:
    """The 10-year/3-month Treasury yield curve: triggers when short-term
    yields exceed long-term ones (the spread goes negative), historically a
    leading indicator that has preceded every US recession since the 1960s
    by roughly 6-18 months -- unlike the other two definitions here, this
    one isn't a coincident/real-time read, it's a warning about the future.

    Reads the single latest observation, not a moving average: daily
    Treasury yield data is materially less noisy day-to-day than monthly
    unemployment, so there's no analogous case for smoothing before judging
    "inverted right now or not."
    """
    if not spread:
        raise ValueError("need at least 1 observation")
    latest = max(spread, key=lambda p: p.date)
    triggered = latest.value < 0
    detail = (
        f"10-year minus 3-month Treasury spread at {latest.value:+.2f}pp as of "
        f"{latest.date.isoformat()}" + (" (inverted)" if triggered else "")
    )
    return Verdict(triggered, latest.date, detail)
