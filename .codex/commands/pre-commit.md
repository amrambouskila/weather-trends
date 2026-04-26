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

### 2. Test Suite
Run `pytest --cov -q` and report results.
- PASS: all tests pass, coverage at 100%
- FAIL: list failures and coverage gaps

### 3. Code Review
For every file in `git diff --name-only`:
- Read the file in full.
- Check against the review checklist (see `/review` command).
- Report any critical or should-fix issues.

### 4. Data-Driven Check
Grep for hard-coded values that should be in `config.py`:
- Latitude/longitude literals outside `config.py`
- API URL strings outside `config.py`
- Date range strings outside `config.py` and tests

### 5. Type Annotation Check
Verify all functions in `src/` have full type annotations.
Grep for `Any` usage — flag each with justification status.

### 6. Documentation Check
Verify `docs/status.md` and `docs/versions.md` reflect the current changes.
- Compare `git diff` file list against docs mentions.
- Flag if significant code changes lack doc updates.

### 7. Interface Integrity
If any Pydantic models in `src/` were modified:
- Flag the change explicitly.
- Verify tests still pass with the new model shape.

## Verdict Table

| Check | Status | Notes |
|-------|--------|-------|
| Lint | PASS/FAIL | ... |
| Tests | PASS/FAIL | ... |
| Code Review | PASS/FAIL | ... |
| Data-Driven | PASS/FAIL | ... |
| Type Annotations | PASS/FAIL | ... |
| Documentation | PASS/FAIL | ... |
| Interface Integrity | PASS/FAIL | ... |

**READY TO COMMIT** or **NOT READY** (with reasons).