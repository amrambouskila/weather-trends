from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analyzer import AnalysisResult
from src.models import TrendResult
from src.visualizer import CHART_FILENAME, TrendVisualizer


def _result() -> AnalysisResult:
    yearly = pd.DataFrame(
        {
            "year": [2000, 2001, 2002, 2003],
            "mean_anomaly": [-0.2, 0.0, 0.1, 0.3],
            "std": [0.1, 0.1, 0.1, 0.1],
            "n": [12, 12, 12, 12],
            "se": [0.03, 0.03, 0.03, 0.03],
            "ci95": [0.06, 0.06, 0.06, 0.06],
        },
    )
    decades = pd.DataFrame({"decade": [2000], "mean_anomaly": [0.05]})
    trend = TrendResult(slope=0.1, intercept=-200.0, r_squared=0.9, p_value=0.01)
    return AnalysisResult(yearly=yearly, trend=trend, decade_averages=decades)


def test_render_writes_png(tmp_path: Path) -> None:
    output_path = TrendVisualizer(output_dir=tmp_path).render(_result())
    assert output_path == tmp_path / CHART_FILENAME
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_creates_missing_output_dir(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "charts"
    output_path = TrendVisualizer(output_dir=target).render(_result())
    assert output_path.exists()
