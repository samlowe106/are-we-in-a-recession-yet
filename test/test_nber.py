import pytest

from are_we_in_a_recession_yet import consecutive_decline

from .conftest import monthly


class TestConsecutiveDecline:
    def test_six_straight_declines_triggers(self):
        rates = [100, 99, 98, 97, 96, 95, 94]  # 6 consecutive drops
        verdict = consecutive_decline(monthly(*rates))
        assert verdict.triggered

    def test_five_straight_declines_does_not_trigger(self):
        rates = [100, 101, 100, 99, 98, 97, 96]  # a rise, then 5 consecutive drops
        verdict = consecutive_decline(monthly(*rates))
        assert not verdict.triggered

    def test_streak_broken_by_one_flat_month_resets(self):
        # a flat (non-declining) month in the middle breaks the streak --
        # only the trailing 3 months count as consecutive decline
        rates = [100, 99, 98, 97, 96, 95, 95, 94, 93, 92]
        verdict = consecutive_decline(monthly(*rates))
        assert not verdict.triggered

    def test_growth_does_not_trigger(self):
        verdict = consecutive_decline(monthly(100, 101, 102, 103, 104, 105, 106))
        assert not verdict.triggered

    def test_unordered_input_is_sorted_by_date(self):
        rates = [100, 99, 98, 97, 96, 95, 94]
        points = monthly(*rates)
        verdict = consecutive_decline(list(reversed(points)))
        assert verdict.triggered

    def test_custom_min_months(self):
        rates = [100, 99, 98, 97]  # 3 consecutive drops
        verdict = consecutive_decline(monthly(*rates), min_months=3)
        assert verdict.triggered

    def test_too_few_points_raises(self):
        with pytest.raises(ValueError):
            consecutive_decline(monthly(100, 99, 98), min_months=6)
