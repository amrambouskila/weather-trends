from __future__ import annotations

from pathlib import Path

from src import config
from src.models import Location


def test_locations_count() -> None:
    assert len(config.LOCATIONS) == 12


def test_locations_are_location_instances() -> None:
    assert all(isinstance(loc, Location) for loc in config.LOCATIONS)


def test_location_names_are_unique() -> None:
    names = [loc.name for loc in config.LOCATIONS]
    assert len(names) == len(set(names))


def test_api_base_url_is_open_meteo_archive() -> None:
    assert config.API_BASE_URL == "https://archive-api.open-meteo.com/v1/archive"


def test_date_range_spans_1940_to_2025() -> None:
    assert config.DEFAULT_START_DATE == "1940-01-01"
    assert config.DEFAULT_END_DATE == "2025-12-31"


def test_output_dir_is_path() -> None:
    assert isinstance(config.OUTPUT_DIR, Path)


def test_chart_dpi_is_publication_quality() -> None:
    assert config.CHART_DPI >= 300


def test_retry_config_sane() -> None:
    assert config.MAX_RETRIES >= 1
    assert config.RATE_LIMIT_BACKOFF_SECONDS > 0
    assert config.HTTP_TIMEOUT_SECONDS > 0
