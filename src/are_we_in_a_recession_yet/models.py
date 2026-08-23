"""Shared data types for recession definitions.

A DataPoint is one observation of an economic series on one date (e.g. real
GNP for a given quarter, or the unemployment rate for a given month). A
Verdict is one definition's answer for whether that series currently shows a
recession, plus enough of the underlying numbers to explain why.

Deliberately just data, no I/O: nothing here knows about FRED, HTTP, or file
formats. That's the caller's job (e.g. a site's own fetch script) -- this
package only answers "given these numbers, does this definition trigger?"
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DataPoint:
    date: date
    value: float


@dataclass(frozen=True)
class Verdict:
    """One definition's read on the data as of `as_of`.

    `detail` is a short human-readable explanation of the numbers behind
    `triggered` (e.g. "3-month avg unemployment 4.10% vs. 3.90% low in the
    past 12 months (+0.20pp)"), meant to be shown next to the verdict, not
    parsed.
    """

    triggered: bool
    as_of: date
    detail: str


# The shared shape every card/indicator in are_we_in_a_recession_yet.definitions
# conforms to: feed it a series, get back a verdict. A function can still take
# extra optional keywords beyond `points` (two_quarter_income_decline's `label`,
# consecutive_decline's `min_months`) and satisfy this -- those are real
# per-indicator tuning, not something a caller needs to know about to treat
# every indicator uniformly (e.g. a future registry/loop over all of them).
Indicator = Callable[[Sequence[DataPoint]], Verdict]
