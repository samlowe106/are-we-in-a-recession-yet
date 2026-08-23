from datetime import date

import pytest

from are_we_in_a_recession_yet import DataPoint, sahm_floor, sahm_rule

from .conftest import add_months, monthly


class TestSahmRule:
    def test_stable_unemployment_does_not_trigger(self):
        verdict = sahm_rule(monthly(*([4.0] * 15)))
        assert not verdict.triggered

    def test_sharp_rise_triggers(self):
        # a low, stable run, then a sharp jump in the last few months
        rates = [4.0] * 12 + [4.3, 4.8, 5.2]
        verdict = sahm_rule(monthly(*rates))
        assert verdict.triggered

    def test_gradual_rise_under_threshold_does_not_trigger(self):
        # +0.4pp over the window, just under the 0.50pp threshold
        rates = [4.0] * 12 + [4.1, 4.2, 4.4]
        verdict = sahm_rule(monthly(*rates))
        assert not verdict.triggered

    def test_exactly_at_threshold_triggers(self):
        # rule is stated as ">= 0.50pp", not "> 0.50pp": latest 3-month avg
        # lands at exactly 4.50 against a 4.00 floor, delta == 0.50 exactly.
        rates = [4.0] * 12 + [4.5, 4.5, 4.5]
        verdict = sahm_rule(monthly(*rates))
        assert verdict.triggered

    def test_too_few_points_raises(self):
        # 11 months -> only 8 3-month averages fall in the trailing-12-month
        # window, under MIN_TRAILING_MONTHS (9).
        with pytest.raises(ValueError):
            sahm_rule(monthly(*([4.0] * 11)))

    def test_gap_does_not_extend_lookback_past_12_calendar_months(self):
        # Regression test for a real bug: a data source with one missing
        # monthly release (see fetch-recession-data.py's own comment on
        # FRED's 2025-10 UNRATE gap) used to make the trailing-12-month
        # floor silently reach back 13 calendar months instead of 12, to
        # make up for the missing entry -- "last 12 list items" instead of
        # "everything in the last 12 months." That could pull in data from
        # well outside the true window.
        #
        # Flat 4.0% throughout, except a dip at months 0-2 (comfortably
        # outside where the 12-month window should reach -- its 3-month-
        # average influence fades out by month 4, before the window even
        # starts) and a rise in the final 3 months. Month 10 is deleted to
        # simulate a missing release in the middle of the window.
        start = date(2020, 1, 1)
        rates = {add_months(start, i): 4.0 for i in range(18)}
        for i in (0, 1, 2):
            rates[add_months(start, i)] = 2.0
        for i in (15, 16, 17):
            rates[add_months(start, i)] = 5.0
        del rates[add_months(start, 10)]

        points = [DataPoint(d, v) for d, v in sorted(rates.items())]
        floor = sahm_floor(points)

        # The dip must NOT be picked up -- if it were (the bug), the floor
        # would read close to 2.0-3.3 instead of the true window's 4.0.
        assert floor.value == pytest.approx(4.0)
        assert floor.date == add_months(start, 5)
