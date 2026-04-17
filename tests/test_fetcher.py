from __future__ import annotations

from collections.abc import Callable

import httpx
import pytest

from src.fetcher import (
    RateLimitExceededError,
    WeatherDataFetcher,
    WeatherFetchError,
    _payload_to_dataframe,
)
from src.models import Location

LOC = Location(name="Oslo", lat=59.9139, lon=10.7522)


def _make_fetcher(handler: Callable[[httpx.Request], httpx.Response]) -> WeatherDataFetcher:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    return WeatherDataFetcher(client=client, sleep=lambda _s: None)


def _ok_payload() -> dict[str, list[str] | list[float]]:
    return {
        "time": ["2024-01-01", "2024-01-02"],
        "temperature_2m_mean": [1.0, 2.0],
    }


def test_fetch_location_success() -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"daily": _ok_payload()})

    fetcher = _make_fetcher(handler)
    df = fetcher.fetch_location(LOC, "2024-01-01", "2024-01-02")
    fetcher.close()

    assert list(df.columns) == ["time", "temperature_2m_mean", "location", "lat", "lon"]
    assert len(df) == 2
    assert df["location"].unique().tolist() == ["Oslo"]


def test_fetch_location_params_sent_correctly() -> None:
    captured: dict[str, str] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        captured.update(req.url.params)
        return httpx.Response(200, json={"daily": _ok_payload()})

    fetcher = _make_fetcher(handler)
    fetcher.fetch_location(LOC, "2024-01-01", "2024-01-02")
    fetcher.close()

    assert captured["latitude"] == "59.9139"
    assert captured["longitude"] == "10.7522"
    assert captured["start_date"] == "2024-01-01"
    assert captured["end_date"] == "2024-01-02"
    assert captured["daily"] == "temperature_2m_mean"
    assert captured["timezone"] == "UTC"


@pytest.mark.parametrize(
    "marker_text",
    ["Hourly API request limit exceeded", "Daily API request limit exceeded"],
)
def test_rate_limit_raises(marker_text: str) -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text=marker_text)

    fetcher = _make_fetcher(handler)
    with pytest.raises(RateLimitExceededError):
        fetcher.fetch_location(LOC, "2024-01-01", "2024-01-02")
    fetcher.close()


def test_transient_error_then_success() -> None:
    calls = {"n": 0}

    def handler(_req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(500, text="transient")
        return httpx.Response(200, json={"daily": _ok_payload()})

    fetcher = _make_fetcher(handler)
    df = fetcher.fetch_location(LOC, "2024-01-01", "2024-01-02")
    fetcher.close()

    assert calls["n"] == 2
    assert len(df) == 2


def test_persistent_failure_raises() -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="down")

    fetcher = _make_fetcher(handler)
    with pytest.raises(WeatherFetchError):
        fetcher.fetch_location(LOC, "2024-01-01", "2024-01-02")
    fetcher.close()


def test_missing_daily_block_raises() -> None:
    with pytest.raises(WeatherFetchError):
        _payload_to_dataframe({}, LOC)


def test_fetch_all_concatenates() -> None:
    def handler(_req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"daily": _ok_payload()})

    fetcher = _make_fetcher(handler)
    locs = [
        LOC,
        Location(name="Quito", lat=-0.18, lon=-78.47),
    ]
    df = fetcher.fetch_all(locs, "2024-01-01", "2024-01-02")
    fetcher.close()

    assert len(df) == 4
    assert set(df["location"].unique()) == {"Oslo", "Quito"}


def test_default_client_constructed_when_none_passed() -> None:
    fetcher = WeatherDataFetcher()
    assert fetcher._owns_client is True
    fetcher.close()


def test_close_does_not_close_external_client() -> None:
    transport = httpx.MockTransport(lambda _r: httpx.Response(200, json={"daily": _ok_payload()}))
    client = httpx.Client(transport=transport)
    fetcher = WeatherDataFetcher(client=client)
    fetcher.close()
    assert not client.is_closed
    client.close()
