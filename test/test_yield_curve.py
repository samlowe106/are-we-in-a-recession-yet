import pytest

from are_we_in_a_recession_yet import yield_curve_inversion

from .conftest import daily


class TestYieldCurveInversion:
    def test_positive_spread_does_not_trigger(self):
        verdict = yield_curve_inversion(daily(1.2, 1.3, 1.1))
        assert not verdict.triggered

    def test_negative_spread_triggers(self):
        verdict = yield_curve_inversion(daily(0.3, 0.1, -0.2))
        assert verdict.triggered

    def test_exactly_zero_does_not_trigger(self):
        # a flat curve isn't an inverted one
        verdict = yield_curve_inversion(daily(0.5, 0.2, 0.0))
        assert not verdict.triggered

    def test_only_the_latest_observation_matters(self):
        # an earlier inversion that's since recovered shouldn't still trigger
        verdict = yield_curve_inversion(daily(-0.5, -0.3, 0.4))
        assert not verdict.triggered

    def test_unordered_input_is_sorted_by_date(self):
        points = daily(0.3, 0.1, -0.2)
        verdict = yield_curve_inversion(list(reversed(points)))
        assert verdict.triggered
        assert verdict.as_of == points[-1].date

    def test_single_point_is_enough(self):
        verdict = yield_curve_inversion(daily(-0.1))
        assert verdict.triggered

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            yield_curve_inversion([])
