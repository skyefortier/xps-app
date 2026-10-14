# Suites on seal-1a-server

## pytest tests/ (full fast suite) at e0257dc (round-8 code, reviewed GO x2 in round 9)
```
2 failed, 1576 passed, 7 skipped, 22 warnings in 2688.89s (0:44:48)
FAILED tests/test_fit_equality.py::test_one_ulp_inside_a_very_narrow_bound_is_the_same_fit
FAILED tests/test_scattered_starts.py::test_the_two_basin_fixture_is_inside_its_basins
FAIL: 2 failures / 0 errors
```

Both failures were the same-fit comparator (tests/fit_equality.py) comparing the new `request_digest` of two requests one rounding apart. Fixed in the next commit: `request_digest` is not compared (it names the request, not the fit) and `fitted_sub` is compared as a signal curve. Every user of the comparator re-run after the fix (test_browser_fit_recording, test_component_required, test_fit_recording, test_fit_reproducibility, test_scattered_starts, autofit/test_c1s_parity_battery, test_fit_equality):
```
217 passed in 563.06s (0:09:23)
```

## JS suite (node --test, CI guard --min-passed 647) at 39d4688 (no page change since)
```
JS suite guard ok
```

History: a71661e (round 0) pytest 1499 passed / 7 skipped; c0ee89e (round 4) 1555 passed / 7 skipped.
