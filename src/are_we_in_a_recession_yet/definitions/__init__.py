"""Four ways of answering "are we in a recession?" from raw time series.

All take already-fetched observations (see models.DataPoint) and return a
Verdict (models.Indicator is the shared shape) -- none of them fetches data
itself or knows what source it came from.

One file per distinct methodology, not one per card: the site actually shows
eight cards, but two_quarter_decline.py backs both the GNI and GDP cards, and
nber.py backs all four NBER coincident-indicator cards, since each group
really is the same function read against different data, not four/two
independent definitions.
"""

from .nber import consecutive_decline
from .sahm import sahm_floor, sahm_rule, sahm_window_start
from .two_quarter_decline import two_quarter_income_decline
from .yield_curve import yield_curve_inversion

__all__ = [
    "consecutive_decline",
    "sahm_floor",
    "sahm_rule",
    "sahm_window_start",
    "two_quarter_income_decline",
    "yield_curve_inversion",
]
