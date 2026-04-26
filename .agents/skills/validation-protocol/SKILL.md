---
name: validation-protocol
description: Proactively applied when writing or modifying tests; enforces real assertions, reference values, and no-mocking rules
---

# Validation Protocol Skill

## When to Apply
- When editing any file in `tests/`.
- When adding new analysis logic that requires test coverage.

## Protocol

### Test quality requirements:

1. **No mocking of math.** Never mock `scipy.stats.linregress`, `numpy` operations, or `pandas` aggregations. Test with real computations.

2. **Mock only external I/O.** HTTP responses from Open-Meteo API should be mocked (use `pytest-httpx` or `unittest.mock.patch`). File system operations may be mocked. Math and statistics — never.

3. **Reference-value tests required.** At least one test per analysis module must validate against a known result:
   - **Trend slope:** Generate synthetic data with an exact known trend (e.g., 0.02 degC/year). Verify computed slope matches within `atol=0.005`.
   - **Anomaly computation:** Feed data with known per-location baselines. Verify anomalies are correct.
   - **CI calculation:** Feed data with known std/n. Verify CI = 1.96 * std / sqrt(n).

4. **Numerical assertions use `np.testing.assert_allclose`.** Never `==` for floats. Document the tolerance and justify it:
   ```python
   # Tolerance: slope should be within 0.005 degC/year of known value.
   # Larger tolerance accounts for noise in mock data with AR(1) process.
   np.testing.assert_allclose(result.slope, 0.02, atol=0.005)
   ```

5. **Parametrize for multiple conditions.** Use `@pytest.mark.parametrize` for:
   - Different city counts (1, 6, 12)
   - Different date ranges
   - Edge cases (single year, all-NaN location, zero trend)

6. **No tautological tests.** "The function returns what the function computes" is not a test. Every assertion must compare against an independently computed expected value.

7. **Test file structure mirrors source:** `src/analyzer.py` → `tests/test_analyzer.py`.