"""Point-factory helpers shared across test_*.py -- e.g. quarterly() is used
by test_two_quarter_decline.py, monthly() by both test_sahm.py and
test_nber.py. Plain functions, not pytest fixtures: each test calls these
directly to build its own specific series rather than injecting a fixed one.
"""

from datetime import date

from are_we_in_a_recession_yet import DataPoint


def quarterly(*values: float) -> list[DataPoint]:
    # one point per quarter, starting 2020-01-01, in the order given
    return [
        DataPoint(date(2020 + i // 4, 3 * (i % 4) + 1, 1), v)
        for i, v in enumerate(values)
    ]


def monthly(*values: float) -> list[DataPoint]:
    # one point per month, starting 2020-01-01, in the order given
    return [
        DataPoint(date(2020 + i // 12, i % 12 + 1, 1), v) for i, v in enumerate(values)
    ]


def daily(*values: float) -> list[DataPoint]:
    # one point per day, starting 2020-01-01, in the order given
    return [DataPoint(date(2020, 1, 1 + i), v) for i, v in enumerate(values)]


def add_months(d: date, n: int) -> date:
    total_months = d.year * 12 + (d.month - 1) + n
    return date(total_months // 12, total_months % 12 + 1, 1)
