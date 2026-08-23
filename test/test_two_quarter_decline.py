from datetime import date

import pytest

from are_we_in_a_recession_yet import two_quarter_income_decline

from .conftest import quarterly


class TestTwoQuarterIncomeDecline:
    def test_two_consecutive_declines_triggers(self):
        verdict = two_quarter_income_decline(quarterly(100, 99, 98))
        assert verdict.triggered
        assert verdict.as_of == date(2020, 7, 1)

    def test_growth_does_not_trigger(self):
        verdict = two_quarter_income_decline(quarterly(100, 101, 102))
        assert not verdict.triggered

    def test_one_decline_then_recovery_does_not_trigger(self):
        # a single bad quarter followed by a rebound isn't this definition
        verdict = two_quarter_income_decline(quarterly(100, 98, 99))
        assert not verdict.triggered

    def test_decline_then_flat_does_not_trigger(self):
        # the second quarter has to be a decline too, not just non-growth
        verdict = two_quarter_income_decline(quarterly(100, 98, 98))
        assert not verdict.triggered

    def test_only_uses_the_most_recent_three_quarters(self):
        # an earlier two-quarter decline shouldn't matter once growth resumes
        verdict = two_quarter_income_decline(quarterly(100, 90, 80, 85, 90))
        assert not verdict.triggered

    def test_unordered_input_is_sorted_by_date(self):
        points = quarterly(100, 99, 98)
        verdict = two_quarter_income_decline(list(reversed(points)))
        assert verdict.triggered

    def test_too_few_points_raises(self):
        with pytest.raises(ValueError):
            two_quarter_income_decline(quarterly(100, 99))
