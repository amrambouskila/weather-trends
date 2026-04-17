from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models import DailyTemperatureRecord, Location, TrendResult, YearlyAnomaly


class TestLocation:
    def test_valid_location(self) -> None:
        loc = Location(name="Quito", lat=-0.1807, lon=-78.4678)
        assert loc.name == "Quito"
        assert loc.lat == -0.1807
        assert loc.lon == -78.4678

    @pytest.mark.parametrize(
        ("lat", "lon"),
        [(90.1, 0.0), (-90.1, 0.0), (0.0, 180.1), (0.0, -180.1)],
    )
    def test_out_of_range_coordinates_rejected(self, lat: float, lon: float) -> None:
        with pytest.raises(ValidationError):
            Location(name="x", lat=lat, lon=lon)

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Location(name="", lat=0.0, lon=0.0)


class TestDailyTemperatureRecord:
    def test_with_temperature(self) -> None:
        r = DailyTemperatureRecord(
            time="2024-07-01",
            temperature_2m_mean=25.3,
            location="Tokyo",
            lat=35.6762,
            lon=139.6503,
        )
        assert r.temperature_2m_mean == 25.3

    def test_null_temperature_allowed(self) -> None:
        r = DailyTemperatureRecord(
            time="2024-07-01",
            temperature_2m_mean=None,
            location="Tokyo",
            lat=35.6762,
            lon=139.6503,
        )
        assert r.temperature_2m_mean is None


class TestYearlyAnomaly:
    def test_valid(self) -> None:
        a = YearlyAnomaly(year=2020, mean_anomaly=0.8, std=0.2, n=12, se=0.058, ci95=0.113)
        assert a.year == 2020

    def test_negative_std_rejected(self) -> None:
        with pytest.raises(ValidationError):
            YearlyAnomaly(year=2020, mean_anomaly=0.8, std=-0.1, n=12, se=0.05, ci95=0.1)

    def test_zero_n_rejected(self) -> None:
        with pytest.raises(ValidationError):
            YearlyAnomaly(year=2020, mean_anomaly=0.8, std=0.1, n=0, se=0.05, ci95=0.1)


class TestTrendResult:
    def test_valid(self) -> None:
        t = TrendResult(slope=0.02, intercept=-40.0, r_squared=0.95, p_value=1e-6)
        assert t.slope_unit == "degC/year"

    @pytest.mark.parametrize("r2", [-0.01, 1.01])
    def test_r_squared_out_of_range(self, r2: float) -> None:
        with pytest.raises(ValidationError):
            TrendResult(slope=0.02, intercept=0.0, r_squared=r2, p_value=0.1)

    @pytest.mark.parametrize("p", [-0.01, 1.01])
    def test_p_value_out_of_range(self, p: float) -> None:
        with pytest.raises(ValidationError):
            TrendResult(slope=0.02, intercept=0.0, r_squared=0.9, p_value=p)
