from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.mock_data import MockDataGenerator, _ar1_noise
from src.models import Location


def _two_locations() -> list[Location]:
    return [
        Location(name="Quito", lat=-0.18, lon=-78.47),
        Location(name="Reykjavik", lat=64.13, lon=-21.95),
    ]


def test_schema_matches_contract() -> None:
    gen = MockDataGenerator(start_date="2000-01-01", end_date="2000-12-31")
    df = gen.generate(_two_locations())
    assert list(df.columns) == ["time", "temperature_2m_mean", "location", "lat", "lon"]
    assert set(df["location"].unique()) == {"Quito", "Reykjavik"}


def test_trend_signal_is_recoverable() -> None:
    # Using 30 years of daily data so noise averages out and linregress recovers the planted trend.
    planted = 0.03
    gen = MockDataGenerator(
        start_date="1990-01-01",
        end_date="2019-12-31",
        trend_c_per_year=planted,
        daily_noise_std=0.5,
        ar1_phi=0.0,
        seed=7,
    )
    df = gen.generate(_two_locations())
    df["time"] = pd.to_datetime(df["time"])
    df["frac_year"] = df["time"].dt.year + (df["time"].dt.dayofyear - 1) / 365.25
    result = stats.linregress(df["frac_year"].to_numpy(), df["temperature_2m_mean"].to_numpy())
    np.testing.assert_allclose(result.slope, planted, atol=0.01)


def test_hemisphere_seasonality_opposite_phase() -> None:
    # At a July timestep the northern city should be warmer than its January value,
    # and the southern city should be colder than its January value.
    gen = MockDataGenerator(
        start_date="2000-01-01",
        end_date="2000-12-31",
        daily_noise_std=0.0,
        ar1_phi=0.0,
        residual_loc_std=0.0,
        trend_c_per_year=0.0,
        seed=1,
    )
    df = gen.generate(_two_locations())
    df["time"] = pd.to_datetime(df["time"])
    jul = df[df["time"].dt.month == 7].groupby("location")["temperature_2m_mean"].mean()
    jan = df[df["time"].dt.month == 1].groupby("location")["temperature_2m_mean"].mean()
    assert jul["Reykjavik"] > jan["Reykjavik"]
    assert jul["Quito"] < jan["Quito"]


def test_seed_reproducibility() -> None:
    gen1 = MockDataGenerator(start_date="2020-01-01", end_date="2020-03-01", seed=42)
    gen2 = MockDataGenerator(start_date="2020-01-01", end_date="2020-03-01", seed=42)
    df1 = gen1.generate(_two_locations())
    df2 = gen2.generate(_two_locations())
    np.testing.assert_array_equal(df1["temperature_2m_mean"], df2["temperature_2m_mean"])


def test_different_seeds_produce_different_data() -> None:
    gen1 = MockDataGenerator(start_date="2020-01-01", end_date="2020-03-01", seed=1)
    gen2 = MockDataGenerator(start_date="2020-01-01", end_date="2020-03-01", seed=2)
    df1 = gen1.generate(_two_locations())
    df2 = gen2.generate(_two_locations())
    assert not np.array_equal(df1["temperature_2m_mean"], df2["temperature_2m_mean"])


def test_missing_rate_produces_nans_and_drops() -> None:
    gen = MockDataGenerator(
        start_date="2000-01-01",
        end_date="2001-12-31",
        missing_rate=0.2,
        seed=3,
    )
    df = gen.generate(_two_locations())
    assert df["temperature_2m_mean"].isna().any()
    gen_full = MockDataGenerator(
        start_date="2000-01-01",
        end_date="2001-12-31",
        missing_rate=0.0,
        seed=3,
    )
    full_len = len(gen_full.generate(_two_locations()))
    assert len(df) < full_len


def test_missing_rate_zero_leaves_data_intact() -> None:
    gen = MockDataGenerator(start_date="2000-01-01", end_date="2000-06-30", missing_rate=0.0)
    df = gen.generate(_two_locations())
    assert not df["temperature_2m_mean"].isna().any()


def test_ar1_noise_first_element_matches_epsilon() -> None:
    rng = np.random.default_rng(0)
    n = 5
    # Reproduce the generator's first draw ourselves to verify ar[0] == eps[0].
    rng2 = np.random.default_rng(0)
    eps_first = rng2.normal(0.0, 1.0, size=n)[0]
    noise = _ar1_noise(rng, n, phi=0.5, sigma=1.0)
    np.testing.assert_allclose(noise[0], eps_first)
