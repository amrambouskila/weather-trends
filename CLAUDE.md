# CLAUDE.md - Weather Trends Analyzer

---

<mandatory_workflow>

> **MANDATORY WORKFLOW: READ THIS ENTIRE FILE BEFORE EVERY CHANGE.** Every time. No skimming, no assuming prior-session context carries over — it does not.
>
> **Why:** This project spans multiple sessions and months of development. Skipping the re-read produces decisions that contradict the architecture, duplicate existing patterns, break data contracts, or introduce tech debt that compounds.
>
> **The workflow, every time:**
> 1. Read this entire file in full.
> 2. Read the master plan document: `docs/WEATHER_TRENDS_MASTER_PLAN.md`.
> 3. Read `docs/status.md` — current state / what was just built.
> 4. Read `docs/versions.md` — recent version history.
> 5. Read the source files you plan to modify — understand existing patterns first.
> 6. Then implement, following the rules and contracts defined here.

</mandatory_workflow>

---

<critical_context>

## 0. Critical Context

This is a **global weather trend analyzer** — a data-driven climate analysis tool that fetches historical temperature data (1940-2025) from the Open-Meteo Archive API for representative cities worldwide, computes anomalies and linear trends with statistical significance, and produces publication-quality visualizations.

**What this project is NOT:**
- Not a weather forecasting tool — it analyzes historical trends, not future predictions.
- Not a real-time dashboard — it processes archival data in batch.
- Not a climate model — it performs statistical analysis of observed data, not physical simulation.

**Key constraint:** All data is fetched from APIs or generated via mock. No hard-coded temperature data. Location metadata (lat/lon/name) lives in configuration, not scattered through code.

**Current phase:** Phase 1 — CLI script. Single-file prototype (`weather_trend.py`) exists and works. Needs refactoring into proper project structure with type annotations, tests, Docker, and CI/CD.

</critical_context>

---

<project_identity>

## 1. Project Identity

- **Name:** weather-trends
- **Location:** `weather-trends/`
- **Master plan:** `docs/WEATHER_TRENDS_MASTER_PLAN.md`
- **Purpose:** Fetch, aggregate, and visualize global temperature trends from 1940-2025 using the Open-Meteo Archive API.
- **Stack:** Python 3.13, pandas, numpy, scipy, matplotlib, seaborn, httpx
- **Data source:** Open-Meteo Archive API (`https://archive-api.open-meteo.com/v1/archive`)

</project_identity>

---

<phase_constraints>

## 2. Phase Constraints

### Phase 1: CLI Script (current)
- Refactor `weather_trend.py` into proper module structure under `src/`.
- Add type annotations, tests, Docker, CI/CD.
- Output: matplotlib/seaborn charts saved to `output/` directory.
- **In scope:** data fetching, anomaly calculation, trend regression, static visualization.
- **NOT in scope:** web UI, database, scheduled collection, interactive charts.

### Phase 2: Streamlit Dashboard (future)
- Interactive web dashboard for exploring trends.
- Date range selection, city filtering, comparison views.
- Dockerized Streamlit app.

### Phase 3: FastAPI Backend + Scheduled Collection (future)
- Automated daily/weekly data collection via cron.
- PostgreSQL for persistent storage.
- REST API for querying stored data.
- Frontend visualization via React (if needed beyond Streamlit).

</phase_constraints>

---

<architecture>

## 3. Architecture & Code Rules

### General
- **`from __future__ import annotations`** at the top of every module.
- Full type annotations on every function signature. `ANN` ruff rules enforced.
- **No `Any`** without explicit justification.
- **No magic numbers.** Location data, API URLs, date ranges — all from config or constants.
- **One concept per file.** No god files. The analyzer, data fetcher, trend calculator, and visualizer are separate modules.
- **OOP where it makes sense.** The current `GlobalWeatherAnalyzer` monolith gets split into focused classes/modules.

### Naming
- `snake_case.py` modules, `PascalCase` classes, `snake_case` functions/methods, `UPPER_SNAKE_CASE` constants.
- Domain-standard variable names: `lat`, `lon`, `temp`, `anomaly`, `slope`, `r2`, `p_value`, `ci95`.

### Dependencies (non-negotiable)
- **HTTP client:** `httpx` — never `requests`.
- **Data:** `pandas` — never polars.
- **Numerical:** `numpy`, `scipy` for regression/statistics.
- **Visualization:** `seaborn` + `matplotlib` — never plotly, never bokeh.
- **Testing:** `pytest` + `pytest-cov` — never unittest.
- **Lint/format:** `ruff`, `line-length = 120`.
- **Package manager:** `uv` — never pip directly, never poetry.

### Error Handling
- Validate at system boundaries only: API responses, CLI arguments, config file loads.
- No bare `except:` clauses. Catch specific exception types.
- API rate limits: retry with backoff, log the event, never recurse infinitely.

</architecture>

---

<data_contracts>

## 4. Domain Model & Data Contracts

### Location
```python
from pydantic import BaseModel

class Location(BaseModel):
    name: str
    lat: float  # decimal degrees, WGS84
    lon: float  # decimal degrees, WGS84
```

### Temperature Record (raw from API)
```python
class DailyTemperatureRecord(BaseModel):
    time: str           # "YYYY-MM-DD"
    temperature_2m_mean: float | None  # degrees Celsius
    location: str
    lat: float
    lon: float
```

### Yearly Anomaly (computed)
```python
class YearlyAnomaly(BaseModel):
    year: int
    mean_anomaly: float     # degrees Celsius, relative to location baseline
    std: float              # standard deviation across locations
    n: int                  # number of locations with data
    se: float               # standard error = std / sqrt(n)
    ci95: float             # 1.96 * se
```

### Trend Result (computed)
```python
class TrendResult(BaseModel):
    slope: float            # degrees Celsius per year
    intercept: float
    r_squared: float
    p_value: float
    slope_unit: str = "degC/year"
```

</data_contracts>

---

<file_structure>

## 5. Module Structure (Target)

```
weather-trends/
├── src/
│   ├── __init__.py
│   ├── config.py           # Locations list, API base URL, date ranges, output paths
│   ├── fetcher.py          # WeatherDataFetcher — httpx-based API client with retry/backoff
│   ├── mock_data.py        # MockDataGenerator — realistic synthetic data for testing/offline
│   ├── analyzer.py         # TrendAnalyzer — anomaly computation, linear regression, statistics
│   ├── visualizer.py       # TrendVisualizer — seaborn/matplotlib chart generation
│   └── cli.py              # CLI entrypoint — argparse, orchestrates fetch → analyze → visualize
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures (mock API responses, sample DataFrames)
│   ├── test_config.py
│   ├── test_fetcher.py     # Mock httpx responses, test retry logic
│   ├── test_mock_data.py
│   ├── test_analyzer.py    # Validate trend math against known analytical solutions
│   └── test_visualizer.py  # Verify chart generation without display
├── output/                 # Generated charts (gitignored)
├── weather_trend.py        # Original script (kept as reference, will be removed after refactor)
└── ...
```

</file_structure>

---

<testing>

## 6. Testing Requirements

- **Framework:** pytest + pytest-cov. `asyncio_mode = "auto"` if async code is introduced.
- **Coverage target:** 100%. Enforced in CI pipeline. `pragma: no cover` only for `if __name__ == "__main__"` blocks.
- **Numerical assertions:** `np.testing.assert_allclose(actual, expected, atol=..., rtol=...)` with documented tolerances. Never `==` for floats.
- **Reference validation:** At least one test per module validates against a known analytical solution:
  - `test_analyzer.py`: Feed a DataFrame with a known linear trend (e.g., 0.02 degC/year); verify computed slope matches within tolerance.
  - `test_fetcher.py`: Mock httpx responses; verify DataFrame construction.
  - `test_mock_data.py`: Verify mock generator produces data with the specified trend.
- **No mocking of math.** scipy.stats.linregress, numpy operations — test with real computations.
- **Mock the API.** httpx responses are mocked in fetcher tests. Use `pytest-httpx` or manual mocking.
- **Parametrize:** Use `@pytest.mark.parametrize` for multiple cities, date ranges, edge cases.

</testing>

---

<containerization>

## 7. Containerization

### Files
- `Dockerfile` — `python:3.13-slim`, installs deps via uv, copies source, runs CLI.
- `docker-compose.yml` — Single service (`weather-trends`), bind-mount `output/` for chart files.
- `.dockerignore` — Standard Python exclusions.

### Phase notes
- **Phase 1:** Single container, CLI tool. No healthcheck needed (runs and exits).
- **Phase 2:** Becomes a long-running Streamlit service. Add healthcheck, port exposure.
- **Phase 3:** Adds PostgreSQL + Redis. Full `depends_on` with healthchecks.

</containerization>

---

<ci_cd>

## 8. CI/CD — GitHub Actions

**File:** `.github/workflows/ci.yml` (public GitHub remote; release bumps via `.github/workflows/release.yml`). Jobs are chained with `needs:` in the order below.

**Stages (in order):**
1. **lint** — `ruff check .` (select includes `S`) — fail on any error.
2. **sast** — CodeQL + Semgrep + `pip-audit` + `gitleaks` — fail on any HIGH/CRITICAL finding. See section 8a.
3. **test** — `pytest --cov` with JUnit XML published via `dorny/test-reporter` — fail on any test failure.
4. **coverage gate** — `--cov-fail-under=100` in the same `test` job. Build blocked if coverage drops.
5. **build** — `uv build` — must complete without errors.
6. **docker-build** — `docker build .` + `trivy image --severity HIGH,CRITICAL --exit-code 1` — verify Dockerfile builds and the image is clean.

</ci_cd>

---

<security>

## 8a. Security — SAST Scanning & Injection Safety (Non-Negotiable)

Implements global `~/.claude/CLAUDE.md` section 19 for this project. Security is part of the Definition of Done for every task, not a later phase.

### SAST scanning
The CI pipeline MUST have a `sast` stage between `lint` and `test` that fails on any HIGH/CRITICAL finding. MEDIUM findings are triaged: fixed, or suppressed inline with a written justification. `allow_failure: true` on a SAST job is non-compliant. The stage is required from the first pipeline commit onward.

**Tool set (Python-only project, no frontend until Phase 3):**
- **Semgrep** — `semgrep scan --config auto --error` with `p/default`, `p/owasp-top-ten`, `p/python`, `p/docker`. Project rules, if any, in `.semgrep/`.
- **ruff `S` rules** (flake8-bandit) — the required `pyproject.toml` lint select becomes `select = ["E", "F", "I", "N", "UP", "ANN", "S"]`, with `S101` added to the `tests/*` per-file-ignores. Catches `shell=True`, `eval`/`exec`, `pickle`, unsafe `yaml.load`, hard-coded secrets, and string-built SQL in the `lint` stage.
- **`pip-audit`** (`uv run --with pip-audit pip-audit`) — known-vulnerable dependencies fail the pipeline. Neither `semgrep` nor `pip-audit` is in the `dev` dependency group (it holds only pytest, pytest-cov, pytest-asyncio, and ruff): semgrep pulls ~67 packages, so both are run as ephemeral tools (`uvx` / `uv run --with`) instead of bloating every `uv sync`.
- **`gitleaks detect --no-git --redact`** — any leaked credential fails the pipeline.
- **Trivy** — `trivy image --severity HIGH,CRITICAL --exit-code 1 <image>` in the `docker-build` stage against the freshly built image.

**Provider wiring (as wired in `.github/workflows/ci.yml`):** the `sast` job (`needs: lint`; `test` is `needs: sast`) runs `github/codeql-action` (init → analyze, language `python`), `uvx semgrep scan` with `--severity ERROR --error` uploading SARIF via `github/codeql-action/upload-sarif` and failing the job on findings, `gitleaks/gitleaks-action@v2`, and `uv run --with pip-audit pip-audit`. `aquasecurity/trivy-action` runs in `docker-build` against the `weather-trends:ci` image. `security-events: write` is granted at job level. (The GitLab equivalent, should the project ever move, is the `Security/*.gitlab-ci.yml` templates plus an explicit `semgrep` job with `artifacts: reports: sast:` — overriding the templates' default `allow_failure: true`.)

**Local parity:**
```
uv run ruff check .
uvx semgrep scan --config auto --error .
uv run --with pip-audit pip-audit
gitleaks detect --no-git --redact
```

### Injection safety — input boundary inventory
Everything entering the process from outside is hostile until it has crossed a typed validation boundary. Current boundaries in this codebase:

| Boundary | Code | Injection classes | Required defense |
|----------|------|-------------------|------------------|
| Open-Meteo API response | `src/fetcher.py` `fetch_location` → `response.json()` / `response.text`, `_payload_to_dataframe` | Unsafe deserialization, resource exhaustion, log injection | JSON only (never `pickle`/`eval`). Validate the `daily` block shape before building the DataFrame; non-conforming payloads raise `WeatherFetchError`. `HTTP_TIMEOUT_SECONDS` on the client, `MAX_RETRIES` bounded, backoff never recursive. Response text is matched against `RATE_LIMIT_MARKERS` only — never echoed into file names, paths, logs, or shell. Error messages interpolate `location.name` (repo config), never response content. |
| Outbound request URL | `src/fetcher.py` → `API_BASE_URL` from `src/config.py` | SSRF | The URL is a constant; only `lat`/`lon` (floats from `config.LOCATIONS`) and ISO date strings go into query params. No URL, host, or scheme is ever derived from input. If Phase 2/3 accepts user coordinates, they stay numeric `Location` fields and the base URL stays constant. |
| CLI arguments | `src/cli.py` `parse_args`: `--start-date`, `--end-date`, `--output-dir`, `--mock` | Path traversal (output dir), query-parameter injection (dates forwarded to the API) | `--start-date`/`--end-date` are validated as `YYYY-MM-DD` (`datetime.date.fromisoformat`) before reaching `WeatherDataFetcher`; anything else is a CLI error. `--output-dir` is `Path`-typed; the output file name is the constant `CHART_FILENAME` in `src/visualizer.py` — no input ever names a file. In Docker the directory is the bind-mounted `/app/output`. |
| `OUTPUT_DIR` env var | `src/config.py` | Path traversal | Same as `--output-dir`: directory only, constant file name, `mkdir(parents=True, exist_ok=True)`, never delete or overwrite outside it. |
| Chart output | `src/visualizer.py` `TrendVisualizer.render` → `fig.savefig` | Path traversal | Writes only `output_dir / CHART_FILENAME`. Agg backend, never `plt.show()`. |

Not boundaries (in-repo, trusted): `config.LOCATIONS`, `MockDataGenerator` output, `TrendAnalyzer` inputs produced in-process.

**Not applicable in Phase 1, stated explicitly:** no SQL (no database), no subprocess/shell, no templating, no authentication, no LLM calls (prompt injection N/A), no React frontend (XSS/CSP N/A).

**Boundaries that arrive with later phases** (each is added to this table, with its classes and defenses, in the same change that introduces it):
- **Phase 2 Streamlit:** sidebar date range and city selection are user input. Cities are matched against `config.LOCATIONS` by name (allowlist), never used to construct paths or queries. Dates go through the same ISO validation as the CLI. No `unsafe_allow_html=True`. `@st.cache_data` keys are the validated values only.
- **Phase 3 FastAPI + PostgreSQL + Redis:** every endpoint's query/body goes through a Pydantic v2 model; list endpoints have pagination caps; all DB access is SQLAlchemy 2.0 with bound parameters — `text()` only with `:named` binds, never f-strings/`%`/`.format()`; ordering/filter columns come from an allowlist map; CORS is an explicit origin allowlist; request body size limits on uvicorn; scheduled collection jobs take no external input. If a React frontend is added: `dangerouslySetInnerHTML` is ESLint-banned, `eslint-plugin-security` + `eslint-plugin-no-unsanitized` join the lint config, `pnpm audit --audit-level=high` joins `sast`, and `nginx.conf` ships CSP (`default-src 'self'`), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.

### Project-specific additions
- Open-Meteo is an unauthenticated public API; no secrets exist in Phase 1. When Phase 3 adds database/Redis credentials they come from `.env`/CI variables only (the `PreToolUse` hook blocks `.env*` writes) — never from `config.py`.
- The container runs as a batch job (`restart: "no"`) with a single bind mount (`./output:/app/output`). Never bind-mount the project root.
- `weather_trend.py` (legacy prototype) is scanned like any other file until it is removed.

The task-completion checklist in section 13 includes a **Security check** item.

</security>

---

<visualization_standards>

## 9. Visualization Standards

- **Library:** seaborn + matplotlib. Never plotly.
- **Style:** seaborn's `whitegrid` or `ticks` style. Clean, publication-quality.
- **Charts to produce:**
  1. **Trend line** — yearly mean anomaly with 95% CI error bars, linear regression overlay, slope/p-value/R^2 annotation.
  2. **Distribution** — histogram of yearly mean anomalies.
  3. **Per-city comparison** — small multiples or overlay of per-city trends.
  4. **Decade averages** — bar chart of decade-averaged anomalies.
- **Output:** Save to `output/` directory as PNG (300 DPI). Never `plt.show()` in non-interactive mode.
- **Figure sizing:** `figsize` in inches, consistent across charts. Axis labels with units.

</visualization_standards>

---

<git_policy>

## 10. Hands Off Git

I manage git myself — branches, commits, merges, rebases, pushes, tags, history, all of it. You do not run any git command that changes state. No `git add`, no `git commit`, no `git checkout`, no `git merge`, no `git push`, no `git stash`, no `git reset`. Read-only git is fine (`git status`, `git diff`, `git log`, `git show`, `git blame`) when needed for inspection.

When you finish a task, report:
1. What files you changed and why (one line each).
2. Whether the change group is cohesive enough to be one commit or should be split.
3. A suggested commit message (subject + body), clearly labeled as a suggestion.

</git_policy>

---

<environment>

## 11. Environment Configuration

```
# .env (gitignored)
WEATHER_TRENDS_PORT=8501        # Phase 2: Streamlit port
OUTPUT_DIR=./output             # Where charts are saved
```

</environment>

---

<change_policy>

## 12. Change Policy & Local Documentation

When completing a feature or significant change, update:

1. **`docs/status.md`** — Current state, what was just built, what's next.
2. **`docs/versions.md`** — Computed next version per semver:
   - **Patch:** bug fix, docs-only, styling.
   - **Minor:** new feature, new module, new chart type.
   - **Major:** breaking change to data contracts. Ask first.
   - Only ONE unreleased version at a time above `pyproject.toml`'s version.
   - Do NOT modify `pyproject.toml`'s version field directly — release pipeline handles it.

</change_policy>

---

<definition_of_done>

## 13. Output & Completion Expectations

At the end of every non-trivial task, run through this checklist:

1. **Summary** — What changed and why (1-2 sentences).
2. **Reuse check** — Confirmed no duplicated logic; searched existing modules before writing new ones.
3. **Tech-debt check** — No shortcuts, no hacks, no `Any`, no dead code, no `TODO` without linked task.
4. **File-organization check** — One concept per file.
5. **Data-contract check** — No typed models changed without approval.
6. **Data-driven check** — No hard-coded domain values (locations, URLs, dates) outside `config.py`.
7. **Docs check** — `status.md` and `versions.md` updated.
8. **Test check** — Tests added/updated for any logic changes. Coverage maintained at 100%.
9. **Security check** — Local SAST clean (`ruff` with `S`, Semgrep, `pip-audit`, `gitleaks`); every touched input boundary names its injection class(es) and defense; section 8a `<security>` updated if a boundary was added.
10. **Forward-compatibility check** — Changes align with Phase 2/3 plans.
11. **Git state** — Report changed files and suggest a commit message.

</definition_of_done>

---

<closing_reminder>

## 14. Reminder

Re-read this file before the next change. Every session, every time.

</closing_reminder>