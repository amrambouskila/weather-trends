from __future__ import annotations

from pathlib import Path

import httpx

from src import cli
from src.fetcher import WeatherDataFetcher


def _ok_payload() -> dict[str, list[str] | list[float]]:
    return {"time": ["2000-01-01", "2000-01-02"], "temperature_2m_mean": [1.0, 2.0]}


def _success_fetcher() -> WeatherDataFetcher:
    transport = httpx.MockTransport(lambda _req: httpx.Response(200, json={"daily": _ok_payload()}))
    return WeatherDataFetcher(client=httpx.Client(transport=transport), sleep=lambda _s: None)


def _rate_limited_fetcher() -> WeatherDataFetcher:
    transport = httpx.MockTransport(lambda _req: httpx.Response(429, text="Daily API request limit exceeded"))
    return WeatherDataFetcher(client=httpx.Client(transport=transport), sleep=lambda _s: None)


def test_build_dataframe_mock() -> None:
    df = cli.build_dataframe(use_mock=True, start_date="2000-01-01", end_date="2000-06-30")
    assert list(df.columns) == ["time", "temperature_2m_mean", "location", "lat", "lon"]
    assert not df.empty


def test_build_dataframe_fetch_success() -> None:
    df = cli.build_dataframe(
        use_mock=False,
        start_date="2000-01-01",
        end_date="2000-01-02",
        fetcher=_success_fetcher(),
    )
    assert len(df) == len(cli.LOCATIONS) * 2


def test_build_dataframe_rate_limit_falls_back_to_mock(capsys) -> None:
    df = cli.build_dataframe(
        use_mock=False,
        start_date="2000-01-01",
        end_date="2000-03-31",
        fetcher=_rate_limited_fetcher(),
    )
    assert not df.empty
    assert "mock data" in capsys.readouterr().out.lower()


def test_main_mock_end_to_end(tmp_path: Path, capsys) -> None:
    cli.main(
        [
            "--mock",
            "--start-date",
            "2000-01-01",
            "--end-date",
            "2002-12-31",
            "--output-dir",
            str(tmp_path),
        ],
    )
    out = capsys.readouterr().out
    assert "GLOBAL WEATHER ANALYSIS SUMMARY REPORT" in out
    assert "Trend:" in out
    assert (tmp_path / "temperature_trend.png").exists()


def test_parse_args_defaults() -> None:
    args = cli.parse_args([])
    assert args.mock is False
    assert args.start_date == cli.DEFAULT_START_DATE
    assert args.end_date == cli.DEFAULT_END_DATE
