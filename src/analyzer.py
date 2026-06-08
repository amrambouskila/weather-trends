from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from src.models import TrendResult

CI95_Z: float = 1.96
YEARLY_COLUMNS: list[str] = ["year", "mean_anomaly", "std", "n", "se", "ci95"]


@dataclass(frozen=True, eq=False)
class AnalysisResult:
    """Yearly anomalies, the fitted warming trend, and decade averages for one analysis run."""

    yearly: pd.DataFrame
    trend: TrendResult
    decade_averages: pd.DataFrame


class TrendAnalyzer:
    """Derives yearly temperature anomalies and a linear warming trend from daily records."""

    def yearly_anomalies(self, raw: pd.DataFrame) -> pd.DataFrame:
        frame = raw.copy()
        frame["time"] = pd.to_datetime(frame["time"])
        frame["year"] = frame["time"].dt.year

        loc_year = frame.groupby(["year", "location"])["temperature_2m_mean"].mean().reset_index()
        baseline = loc_year.groupby("location")["temperature_2m_mean"].mean().rename("baseline").reset_index()
        loc_year = loc_year.merge(baseline, on="location", how="left")
        loc_year["anomaly"] = loc_year["temperature_2m_mean"] - loc_year["baseline"]

        yearly = (
            loc_year.groupby("year")["anomaly"]
            .agg(mean_anomaly="mean", std="std", n="count")
            .reset_index()
            .sort_values("year")
            .reset_index(drop=True)
        )
        yearly["std"] = yearly["std"].fillna(0.0)  # a year with one location has no spread across locations
        yearly["se"] = yearly["std"] / np.sqrt(yearly["n"])
        yearly["ci95"] = CI95_Z * yearly["se"]
        return yearly[YEARLY_COLUMNS]

    def trend(self, yearly: pd.DataFrame) -> TrendResult:
        year = yearly["year"].to_numpy(dtype=float)
        anomaly = yearly["mean_anomaly"].to_numpy(dtype=float)
        fit = stats.linregress(year, anomaly)
        return TrendResult(
            slope=float(fit.slope),
            intercept=float(fit.intercept),
            r_squared=float(fit.rvalue) ** 2,
            p_value=float(fit.pvalue),
        )

    def decade_averages(self, yearly: pd.DataFrame) -> pd.DataFrame:
        frame = yearly[["year", "mean_anomaly"]].copy()
        frame["decade"] = (frame["year"] // 10) * 10
        return frame.groupby("decade")["mean_anomaly"].mean().reset_index().sort_values("decade").reset_index(drop=True)

    def analyze(self, raw: pd.DataFrame) -> AnalysisResult:
        yearly = self.yearly_anomalies(raw)
        return AnalysisResult(yearly=yearly, trend=self.trend(yearly), decade_averages=self.decade_averages(yearly))
