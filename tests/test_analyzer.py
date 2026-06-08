from __future__ import annotations

import numpy as np
import pandas as pd

from src.analyzer import AnalysisResult, TrendAnalyzer
from src.mock_data import MockDataGenerator
from src.models import Location, TrendResult


def _hand_built_frame() -> pd.DataFrame:
    rows = [
        ("2000-06-15", 10.0, "A"),
        ("2001-06-15", 12.0, "A"),
        ("2002-06-15", 14.0, "A"),
        ("2000-06-15", 20.0, "B"),
        ("2001-06-15", 22.0, "B"),
        ("2002-06-15", 24.0, "B"),
    ]
    return pd.DataFrame(
        {
            "time": [r[0] for r in rows],
            "temperature_2m_mean": [r[1] for r in rows],
            "location": [r[2] for r in rows],
            "lat": 0.0,
            "lon": 0.0,
        },
    )


def test_yearly_anomalies_exact() -> None:
    yearly = TrendAnalyzer().yearly_anomalies(_hand_built_frame())
    assert yearly["year"].tolist() == [2000, 2001, 2002]
    np.testing.assert_allclose(yearly["mean_anomaly"].to_numpy(), [-2.0, 0.0, 2.0])
    np.testing.assert_allclose(yearly["std"].to_numpy(), [0.0, 0.0, 0.0])
    assert yearly["n"].tolist() == [2, 2, 2]
    np.testing.assert_allclose(yearly["ci95"].to_numpy(), [0.0, 0.0, 0.0])


def test_columns_match_contract() -> None:
    yearly = TrendAnalyzer().yearly_anomalies(_hand_built_frame())
    assert list(yearly.columns) == ["year", "mean_anomaly", "std", "n", "se", "ci95"]


def test_trend_perfect_line() -> None:
    analyzer = TrendAnalyzer()
    yearly = analyzer.yearly_anomalies(_hand_built_frame())
    trend = analyzer.trend(yearly)
    assert isinstance(trend, TrendResult)
    np.testing.assert_allclose(trend.slope, 2.0)
    np.testing.assert_allclose(trend.r_squared, 1.0)
    assert trend.slope_unit == "degC/year"


def test_trend_recovers_planted_slope() -> None:
    planted = 0.03
    gen = MockDataGenerator(
        start_date="1980-01-01",
        end_date="2019-12-31",
        trend_c_per_year=planted,
        daily_noise_std=0.3,
        ar1_phi=0.0,
        residual_loc_std=0.0,
        seed=11,
    )
    raw = gen.generate(
        [
            Location(name="Quito", lat=-0.18, lon=-78.47),
            Location(name="Reykjavik", lat=64.13, lon=-21.95),
        ],
    )
    result = TrendAnalyzer().analyze(raw)
    np.testing.assert_allclose(result.trend.slope, planted, atol=0.01)


def test_single_location_year_has_zero_spread() -> None:
    frame = pd.DataFrame(
        {
            "time": ["2000-06-15", "2000-06-15", "2001-06-15"],
            "temperature_2m_mean": [10.0, 20.0, 15.0],
            "location": ["A", "B", "A"],
            "lat": 0.0,
            "lon": 0.0,
        },
    )
    yearly = TrendAnalyzer().yearly_anomalies(frame)
    row = yearly[yearly["year"] == 2001].iloc[0]
    assert int(row["n"]) == 1
    assert row["std"] == 0.0
    assert row["se"] == 0.0
    assert row["ci95"] == 0.0


def test_decade_averages() -> None:
    yearly = pd.DataFrame(
        {
            "year": [2000, 2005, 2011, 2019],
            "mean_anomaly": [0.0, 1.0, 2.0, 4.0],
            "std": [0.0, 0.0, 0.0, 0.0],
            "n": [2, 2, 2, 2],
            "se": [0.0, 0.0, 0.0, 0.0],
            "ci95": [0.0, 0.0, 0.0, 0.0],
        },
    )
    decades = TrendAnalyzer().decade_averages(yearly)
    assert decades["decade"].tolist() == [2000, 2010]
    np.testing.assert_allclose(decades["mean_anomaly"].to_numpy(), [0.5, 3.0])


def test_analyze_returns_result() -> None:
    result = TrendAnalyzer().analyze(_hand_built_frame())
    assert isinstance(result, AnalysisResult)
    assert list(result.yearly.columns) == ["year", "mean_anomaly", "std", "n", "se", "ci95"]
    assert isinstance(result.trend, TrendResult)
    assert "decade" in result.decade_averages.columns
