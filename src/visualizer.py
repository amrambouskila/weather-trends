from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from src.analyzer import AnalysisResult
from src.config import CHART_DPI, OUTPUT_DIR

plt.switch_backend("Agg")  # headless rendering for Docker/CI; charts are saved, never shown

CHART_FILENAME: str = "temperature_trend.png"
FIGURE_SIZE: tuple[float, float] = (14.0, 5.0)
HISTOGRAM_BINS: int = 20


class TrendVisualizer:
    """Renders the yearly anomaly trend (with 95% CI) and its distribution to a PNG file."""

    def __init__(self, output_dir: Path = OUTPUT_DIR, dpi: int = CHART_DPI) -> None:
        self._output_dir = output_dir
        self._dpi = dpi

    def render(self, result: AnalysisResult) -> Path:
        sns.set_theme(style="whitegrid")
        self._output_dir.mkdir(parents=True, exist_ok=True)

        yearly = result.yearly
        year = yearly["year"].to_numpy(dtype=float)
        anomaly = yearly["mean_anomaly"].to_numpy(dtype=float)
        ci95 = yearly["ci95"].to_numpy(dtype=float)
        trend = result.trend

        fig, (ax_trend, ax_dist) = plt.subplots(1, 2, figsize=FIGURE_SIZE)

        ax_trend.errorbar(year, anomaly, yerr=ci95, fmt="o-", linewidth=2, markersize=3, capsize=3, elinewidth=1)
        label = f"Trend: {trend.slope:.4f}°C/year | p={trend.p_value:.3g} | R²={trend.r_squared:.3f}"
        ax_trend.plot(year, trend.slope * year + trend.intercept, "--", alpha=0.8, label=label)
        ax_trend.set_title("Average Global Temperature Trend (with 95% CI)")
        ax_trend.set_xlabel("Year")
        ax_trend.set_ylabel("Temperature Anomaly (°C)")
        ax_trend.legend()

        ax_dist.hist(anomaly, bins=HISTOGRAM_BINS, alpha=0.7, edgecolor="black")
        ax_dist.set_title("Temperature Distribution (Yearly Means)")
        ax_dist.set_xlabel("Temperature Anomaly (°C)")
        ax_dist.set_ylabel("Frequency")

        fig.tight_layout()
        output_path = self._output_dir / CHART_FILENAME
        fig.savefig(output_path, dpi=self._dpi)
        plt.close(fig)
        return output_path
