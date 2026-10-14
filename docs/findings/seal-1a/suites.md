# Suites on seal-1a-server

## pytest tests/ (full fast suite) at c0ee89e (round-4 code)
```
1555 passed, 7 skipped, 19 warnings in 2688.60s (0:44:48)
junit: 1562 collected, 1555 ran, 7 skipped, 0 failures, 0 errors
OK
FAILED lines: 0
```

Since c0ee89e the code changes (rounds 5-6) touch only fitting.verify_fit / _verify / _non_finite_request and the verify route; tests/test_seal_1a_verify.py at HEAD: 123 passed in 21.39s.

## JS suite (node --test, CI guard --min-passed 647) at 39d4688
```
{'passed': 647, 'todo': 2, 'skipped': 0, 'failed': 0, 'summary': {'tests': 649, 'failed': 0, 'passed': 647, 'cancelled': 0, 'skipped': 0, 'todo': 2, 'topLevel': 649, 'suites': 0}}
JS suite guard ok
```

Earlier: a71661e (round 0) pytest 1499 passed / 7 skipped.
