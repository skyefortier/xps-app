#!/usr/bin/env python
"""
CI no-silent-skip guard (run-brief item: "CI so gates cannot silently
skip").

Reads a pytest junit XML and FAILS unless:
- at least --min-tests testcases actually RAN (guards against collection
  wipeouts that exit 0), and
- at most --max-skipped were skipped (guards against env-gated REQUIRED
  gates silently skipping — the gate job runs with --max-skipped 0).

Usage: ci_check_junit.py report.xml --min-tests N [--max-skipped M]
"""
import argparse
import sys
import xml.etree.ElementTree as ET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("--min-tests", type=int, required=True)
    ap.add_argument("--max-skipped", type=int, default=0)
    args = ap.parse_args()

    root = ET.parse(args.xml).getroot()
    suites = root.iter("testsuite")
    tests = skipped = failures = errors = 0
    for s in suites:
        tests += int(s.get("tests", 0))
        skipped += int(s.get("skipped", 0))
        failures += int(s.get("failures", 0))
        errors += int(s.get("errors", 0))

    ran = tests - skipped
    print(f"junit: {tests} collected, {ran} ran, {skipped} skipped, "
          f"{failures} failures, {errors} errors")
    if failures or errors:
        sys.exit(f"FAIL: {failures} failures / {errors} errors")
    if ran < args.min_tests:
        sys.exit(f"FAIL: only {ran} tests ran (< {args.min_tests}) — "
                 "collection wipeout or mass skip")
    if skipped > args.max_skipped:
        sys.exit(f"FAIL: {skipped} skipped (> {args.max_skipped}) — a "
                 "required gate may have silently skipped")
    print("OK")


if __name__ == "__main__":
    main()
