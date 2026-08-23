from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from src.analyzer import AnalysisResult, TrendAnalyzer
from src.config import DEFAULT_END_DATE, DEFAULT_START_DATE, LOCATIONS, OUTPUT_DIR
from src.fetcher import RateLimitExceededError, WeatherDataFetcher
from src.mock_data import MockDataGenerator
from src.visualizer import TrendVisualizer


def build_dataframe(
    *,
    use_mock: bool,
    start_date: str,
    end_date: str,
    fetcher: WeatherDataFetcher | None = None,
    mock_generator: MockDataGenerator | None = None,
) -> pd.DataFrame:
    """Fetch real data, falling back to synthetic mock data on rate limit or when use_mock is set."""
    generator = mock_generator or MockDataGenerator(start_date=start_date, end_date=end_date)
    if use_mock:
        return generator.generate(LOCATIONS)

    active_fetcher = fetcher or WeatherDataFetcher()
    try:
        return active_fetcher.fetch_all(LOCATIONS, start_date, end_date)
    except RateLimitExceededError:
        print("API rate limit reached — falling back to synthetic mock data.")
        return generator.generate(LOCATIONS)
    finally:
        active_fetcher.close()


def print_summary(result: AnalysisResult) -> None:
    yearly = result.yearly
    trend = result.trend
    separator = "=" * 60
    print(separator)
    print("GLOBAL WEATHER ANALYSIS SUMMARY REPORT")
    print(separator)
    print(f"Year range: {int(yearly['year'].min())} - {int(yearly['year'].max())}")
    print(f"Years analyzed: {len(yearly)}")
    print(f"Mean anomaly: {yearly['mean_anomaly'].mean():.3f} °C")
    print(f"Trend: {trend.slope:.4f} {trend.slope_unit} (p={trend.p_value:.3g}, R²={trend.r_squared:.3f})")
    print("Decade averages:")
    for _, row in result.decade_averages.iterrows():
        print(f"  {int(row['decade'])}s: {row['mean_anomaly']:.3f} °C")
    print(separator)


def iso_date_argument(value: str) -> str:
    """Reject anything that is not a strict ISO calendar date before it reaches the API query string."""
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected ISO date YYYY-MM-DD, got {value!r}") from exc
    return value


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze global temperature trends from 1940 onward.")
    parser.add_argument("--mock", action="store_true", help="Use synthetic mock data instead of the live API.")
    parser.add_argument(
        "--start-date", type=iso_date_argument, default=DEFAULT_START_DATE, help="ISO start date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--end-date", type=iso_date_argument, default=DEFAULT_END_DATE, help="ISO end date (YYYY-MM-DD)."
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory for the chart PNG.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    raw = build_dataframe(use_mock=args.mock, start_date=args.start_date, end_date=args.end_date)
    result = TrendAnalyzer().analyze(raw)
    output_path = TrendVisualizer(output_dir=args.output_dir).render(result)
    print_summary(result)
    print(f"Chart written to {output_path}")


if __name__ == "__main__":
    main()
