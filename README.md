# are-we-in-a-recession-yet

Four well-known recession definitions, implemented as pure functions over plain time series data:

- **Two-quarter decline** (`two_quarter_income_decline`) — real income (GNI, or equivalently GNP) must fall for two consecutive quarters. The same shape, applied to GDP instead, is the "technical recession" definition most people actually mean by the phrase — pass `label="real GDP"` for that case. GDP and GNI are the same total by construction, but the two independent surveys behind them can still disagree: in 2022 Q1-Q2, GDP fell both quarters and GNI didn't.
- **The Sahm rule** (`sahm_rule`) — a real time indicator developed by [Claudia Sahm](https://en.wikipedia.org/wiki/Claudia_Sahm). The 3-month average unemployment rate must rise 0.50 percentage points or more above its own low point over the preceding year. `sahm_floor` and `sahm_window_start` are also exposed, for a caller (e.g. a chart) that wants to show exactly which part of a longer series the rule's own trailing-12-month floor came from, without reimplementing that windowing.
- **Yield curve inversion** (`yield_curve_inversion`) — a consistent early indicator of **upcoming** depressions in the United States since the 1960s. The 10-year Treasury yield must drop below the 3-month yield.
- **NBER coincident indicators** (`consecutive_decline`) — NBER's Business Cycle Dating Committee prefers a holistic examination of several monthly series for declines that are deep, pervasive, and persistent, rather than a specific formula. Four of those series (nonfarm payrolls, real personal income less transfers, real consumer spending, industrial production) each get their own verdict here, defining a recession as six or more consecutive months of decline.

Each function is pure, taking a sequence of `DataPoint(date, value)` observations and returns a `Verdict(triggered, as_of, detail)`. How real data (e.g. from [FRED](https://fred.stlouisfed.org/)) gets fetched is up to you; see [`.github/workflows/example-scheduled-refresh.yml`](.github/workflows/example-scheduled-refresh.yml) for the general shape of doing it on a schedule, or [samlowe.dev/tools/recession](https://samlowe.dev/tools/recession/) for a dashboard built on top of this package that updates weekly.

Every definition above shares the same shape (`Indicator = Callable[[Sequence[DataPoint]], Verdict]`) even though a couple take extra optional tuning keywords (`label`, `min_months`) beyond that. That's real per-indicator configuration, not something a caller needs to know about to treat every indicator uniformly (e.g. a registry or a loop that calls all of them the same way).

## Usage

```python
from datetime import date
from are_we_in_a_recession_yet import (
    DataPoint,
    two_quarter_income_decline,
    sahm_rule,
    yield_curve_inversion,
    consecutive_decline,
)

real_gni = [
    DataPoint(date(2026, 1, 1), 24173.7),
    DataPoint(date(2026, 4, 1), 24246.7),
    DataPoint(date(2026, 7, 1), 24310.2),
]
verdict = two_quarter_income_decline(real_gni)
print(verdict.triggered, verdict.detail)

real_gdp = [...]  # same shape, a different series
gdp_verdict = two_quarter_income_decline(real_gdp, label="real GDP")

unemployment_rate = [
    DataPoint(date(2025, m, 1), rate)
    for m, rate in enumerate(some_monthly_rates, start=1)
]
print(sahm_rule(unemployment_rate).triggered)

treasury_spread = [...]  # 10-year minus 3-month yield, daily
print(yield_curve_inversion(treasury_spread).triggered)

nonfarm_payrolls = [...]  # monthly
print(consecutive_decline(nonfarm_payrolls, min_months=6).triggered)
```

## Development

Uses [uv](https://docs.astral.sh/uv/) — no separate venv/pip setup needed.

```bash
uv run --group dev pytest --verbose
```

[pre-commit](https://pre-commit.com/) runs ruff (lint + import order), black, and [ty](https://github.com/astral-sh/ty) (type checking) on every commit:

```bash
uv run pre-commit install   # once, per checkout
uv run pre-commit run --all-files
```

## License

[GNU AGPLv3](LICENSE).
