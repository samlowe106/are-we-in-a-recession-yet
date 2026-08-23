"""Claudia Sahm's real-time recession indicator, plus the calendar-based
windowing helpers it (and the site's own chart renderer, which needs to show
the same trailing-12-month floor the rule actually used) share.
"""

from collections.abc import Sequence
from datetime import date

from ..models import DataPoint, Verdict

_SAHM_THRESHOLD_POINTS = 0.50

# The Sahm rule's trailing-12-month floor tolerates a data source having a
# gap (a delayed/missing monthly release) without falling over, but not a
# window that's mostly gaps -- see sahm_floor()'s own comment for why this
# is calendar-based rather than "however many list entries happen to fall in
# it," which is also why this can be less than 12 even on a clean source.
_MIN_TRAILING_MONTHS = 9


def _three_month_averages(ordered: Sequence[DataPoint]) -> list[DataPoint]:
    # moving_averages[i] is the 3-month average ending at ordered[i]; the
    # first two months don't have two prior months yet, so they're skipped
    # rather than producing a 1- or 2-month "average."
    return [
        DataPoint(ordered[i].date, sum(p.value for p in ordered[i - 2 : i + 1]) / 3)
        for i in range(2, len(ordered))
    ]


def _months_before(d: date, months: int) -> date:
    total_months = d.year * 12 + (d.month - 1) - months
    return date(total_months // 12, total_months % 12 + 1, 1)


def sahm_window_start(unemployment_rate: Sequence[DataPoint]) -> date:
    """The first calendar date included in sahm_floor()'s trailing-12-month
    lookback. Exposed on its own so a caller that wants to *show* which part
    of a longer displayed series the floor actually came from (e.g. a chart
    marking its own extra historical context as just that -- context, not
    part of the calculation) doesn't have to reimplement this windowing
    itself and risk it drifting out of sync with what the rule actually
    uses -- see sahm_floor()'s own comment for why this is calendar-based,
    not "the 12 previous list entries."
    """
    ordered = sorted(unemployment_rate, key=lambda p: p.date)
    ma3 = _three_month_averages(ordered)
    if len(ma3) < 2:
        raise ValueError(
            "need at least 2 valid 3-month averages (one prior month plus the latest)"
        )
    return _months_before(ma3[-1].date, 12)


def sahm_floor(unemployment_rate: Sequence[DataPoint]) -> DataPoint:
    """The lowest 3-month average unemployment rate in the 12 calendar
    months immediately before the latest observation -- the reference point
    sahm_rule() compares the latest average against.

    Calendar-month based, not "the 12 previous list entries": a monthly data
    source can have a gap (a delayed/missing release -- FRED's UNRATE has
    one for 2025-10, a government-shutdown delay), and counting list entries
    instead of elapsed calendar time would silently stretch the lookback
    window further back to make up for the missing month instead of just
    working with fewer real observations, which is what a missing release
    actually means. (This was a real bug here, caught by inspection: the
    12th-list-entries version pulled in an extra, lower-than-it-should-be
    month from outside the true trailing year, understating the floor.)
    """
    ordered = sorted(unemployment_rate, key=lambda p: p.date)
    ma3 = _three_month_averages(ordered)
    if len(ma3) < 2:
        raise ValueError(
            "need at least 2 valid 3-month averages (one prior month plus the latest)"
        )

    *history, latest = ma3
    window_start = sahm_window_start(unemployment_rate)
    trailing_year = [p for p in history if window_start <= p.date < latest.date]
    if len(trailing_year) < _MIN_TRAILING_MONTHS:
        raise ValueError(
            f"need at least {_MIN_TRAILING_MONTHS} 3-month averages in the trailing 12 months, "
            f"got {len(trailing_year)}"
        )
    return min(trailing_year, key=lambda p: p.value)


def sahm_rule(unemployment_rate: Sequence[DataPoint]) -> Verdict:
    """Claudia Sahm's real-time recession indicator: triggers when the
    3-month moving average of the (U-3) unemployment rate rises 0.50
    percentage points or more above its own low point over the preceding 12
    months.
    """
    ordered = sorted(unemployment_rate, key=lambda p: p.date)
    ma3 = _three_month_averages(ordered)
    if len(ma3) < 2:
        raise ValueError(
            "need at least 2 valid 3-month averages (one prior month plus the latest)"
        )
    latest = ma3[-1]

    floor = sahm_floor(unemployment_rate)
    delta = latest.value - floor.value
    triggered = delta >= _SAHM_THRESHOLD_POINTS

    detail = (
        f"3-month avg unemployment {latest.value:.2f}% vs. {floor.value:.2f}% low "
        f"in the past 12 months (as of {floor.date.isoformat()}), a change of {delta:+.2f}pp"
    )
    return Verdict(triggered, latest.date, detail)
