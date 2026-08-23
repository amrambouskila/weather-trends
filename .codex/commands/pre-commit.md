---
name: pre-commit
description: Read-only pre-commit audit — reports readiness, never stages or commits
---

# Pre-Commit Audit

Before anything else:
1. Re-read `AGENTS.md` in full.
2. Re-read `docs/WEATHER_TRENDS_MASTER_PLAN.md`.

**This command NEVER stages or commits anything. It only reports.**

## Audit Steps (sequential)

### 1. Lint Check
Run `ruff check .` and report results.
- PASS: zero errors
- FAIL: list all errors with file:line

### 2. SAST
Run `ruff check .` (the `S` rules are part of the lint select), `uvx semgrep scan --config auto --error`, `uv run --with pip-audit pip-audit`, and `gitleaks detect --no-git --redact` and report results.
- PASS: zero HIGH/CRITICAL findings; every MEDIUM finding either fixed or suppressed inline with a written justification
- FAIL: list each finding with tool, rule id, severity, file:line

### 3. Test Suite
Run `pytest --cov -q` and report results.
- PASS: all tests pass, coverage at 100%
- FAIL: list failures and coverage gaps

### 4. Code Review
For every file in `git diff --name-only`:
- Read the file in full.
- Check against the review checklist (see `/review` command).
- Report any critical or should-fix issues.

### 5. Data-Driven Check
Grep for hard-coded values that should be in `config.py`:
- Latitude/longitude literals outside `config.py`
- API URL strings outside `config.py`
- Date range strings outside `config.py` and tests

### 6. Type Annotation Check
Verify all functions in `src/` have full type annotations.
Grep for `Any` usage — flag each with justification status.

### 7. Documentation Check
Verify `docs/status.md` and `docs/versions.md` reflect the current changes.
- Compare `git diff` file list against docs mentions.
- Flag if significant code changes lack doc updates.

### 8. Interface Integrity
If any Pydantic models in `src/` were modified:
- Flag the change explicitly.
- Verify tests still pass with the new model shape.

## Verdict Table

| Check | Status | Notes |
|-------|--------|-------|
| Lint | PASS/FAIL | ... |
| SAST | PASS/FAIL | ... |
| Tests | PASS/FAIL | ... |
| Code Review | PASS/FAIL | ... |
| Data-Driven | PASS/FAIL | ... |
| Type Annotations | PASS/FAIL | ... |
| Documentation | PASS/FAIL | ... |
| Interface Integrity | PASS/FAIL | ... |

**READY TO COMMIT** or **NOT READY** (with reasons).