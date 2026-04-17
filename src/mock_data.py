from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from src.models import Location

BASE_TEMP_EQUATOR_C: float = 28.0
BASE_TEMP_LAT_FACTOR: float = 0.45
SEASONAL_AMP_BASE_C: float = 3.0
SEASONAL_AMP_LAT_FACTOR: float = 0.22
DAYS_PER_YEAR: float = 365.25
MISSING_DROP_SCALE: float = 0.15


class MockDataGenerator:
    """Generate realistic synthetic temperature data for offline runs and tests."""

    def __init__(
        self,
        start_date: str = "1990-01-01",
        end_date: str = "2025-12-31",
        freq: str = "D",
        trend_c_per_year: float = 0.02,
        residual_loc_std: float = 0.8,
        daily_noise_std: float = 1.2,
        ar1_phi: float = 0.75,
        missing_rate: float = 0.0,
        seed: int = 42,
    ) -> None:
        self._start_date = start_date
        self._end_date = end_date
        self._freq = freq
        self._trend_c_per_year = trend_c_per_year
        self._residual_loc_std = residual_loc_std
        self._daily_noise_std = daily_noise_std
        self._ar1_phi = ar1_phi
        self._missing_rate = missing_rate
        self._seed = seed

    def generate(self, locations: Iterable[Location]) -> pd.DataFrame:
        rng = np.random.default_rng(self._seed)
        dates = pd.date_range(start=self._start_date, end=self._end_date, freq=self._freq)
        n = len(dates)

        years = dates.year.to_numpy()
        frac_year = years + (dates.dayofyear.to_numpy() - 1) / DAYS_PER_YEAR
        year0 = float(pd.Timestamp(self._start_date).year)
        doy = dates.dayofyear.to_numpy()

        frames: list[pd.DataFrame] = []
        for loc in locations:
            lat_abs = abs(loc.lat)
            base_mean = BASE_TEMP_EQUATOR_C - BASE_TEMP_LAT_FACTOR * lat_abs
            amp = SEASONAL_AMP_BASE_C + SEASONAL_AMP_LAT_FACTOR * lat_abs
            # Cosine form peaks mid-year in the northern hemisphere (early July) and
            # six months later in the southern, and is orthogonal to frac_year so a
            # linear regression recovers the planted trend without seasonal bias.
            hemisphere_sign = -1.0 if loc.lat < 0 else 1.0
            seasonal = -hemisphere_sign * amp * np.cos(2 * np.pi * doy / DAYS_PER_YEAR)

            ar = _ar1_noise(rng, n, self._ar1_phi, self._daily_noise_std)
            loc_residual = rng.normal(0.0, self._residual_loc_std)
            trend = self._trend_c_per_year * (frac_year - year0)

            temp = base_mean + seasonal + loc_residual + trend + ar

            df_loc = pd.DataFrame(
                {
                    "time": dates.strftime("%Y-%m-%d"),
                    "temperature_2m_mean": temp.astype(float),
                    "location": loc.name,
                    "lat": loc.lat,
                    "lon": loc.lon,
                },
            )

            if 0.0 < self._missing_rate < 1.0:
                mask = rng.random(n) < self._missing_rate
                df_loc.loc[mask, "temperature_2m_mean"] = np.nan

            frames.append(df_loc)

        out = pd.concat(frames, ignore_index=True)

        if 0.0 < self._missing_rate < 1.0:
            drop_mask = rng.random(len(out)) < (self._missing_rate * MISSING_DROP_SCALE)
            out = out.loc[~drop_mask].reset_index(drop=True)

        return out


def _ar1_noise(
    rng: np.random.Generator,
    n: int,
    phi: float,
    sigma: float,
) -> np.ndarray:
    eps = rng.normal(0.0, sigma, size=n)
    ar = np.empty(n, dtype=float)
    ar[0] = eps[0]
    for i in range(1, n):
        ar[i] = phi * ar[i - 1] + eps[i]
    return ar
