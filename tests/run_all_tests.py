import os
import sys
import time
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def create_full_suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    tier1 = loader.loadTestsFromName("tests.test_tier1_features")
    tier2 = loader.loadTestsFromName("tests.test_tier2_boundaries")
    tier3 = loader.loadTestsFromName("tests.test_tier3_security")
    tier4 = loader.loadTestsFromName("tests.test_tier4_personas")
    suite.addTests([tier1, tier2, tier3, tier4])
    return suite, [
        ("Tier 1: Feature Coverage (>=5 per feature)", tier1),
        ("Tier 2: Boundary & Corner Cases (>=5 per feature)", tier2),
        ("Tier 3: Security & Cross-Role Combinations", tier3),
        ("Tier 4: Real-World Military Personas", tier4),
    ]

def run_tests_with_tier_breakdown():
    suite, tiers = create_full_suite()

    print("=" * 80)
    print("QUAN LY DIEN THOAI DAI DOI - E2E TEST SUITE RUNNER")
    print("Python Version: " + sys.version.split()[0])
    print("Environment: Isolated In-Memory SQLite Fixtures")
    print("Strict Constraint: ZERO COMMENTS IN CODE")
    print("=" * 80)

    start_total = time.time()
    tier_results = []
    all_failures = []
    all_errors = []

    for tier_name, tier_suite in tiers:
        runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, "w"))
        t_start = time.time()
        res = runner.run(tier_suite)
        t_duration = time.time() - t_start

        total_count = res.testsRun
        fail_count = len(res.failures)
        err_count = len(res.errors)
        pass_count = total_count - fail_count - err_count

        tier_results.append({
            "name": tier_name,
            "total": total_count,
            "passed": pass_count,
            "failed": fail_count,
            "errors": err_count,
            "duration": t_duration
        })

        for f in res.failures:
            all_failures.append((tier_name, f[0].id(), str(f[1])))
        for e in res.errors:
            all_errors.append((tier_name, e[0].id(), str(e[1])))

    total_duration = time.time() - start_total

    print("\n" + "-" * 80)
    print(f"{'Tier Name':<50} | {'Total':<6} | {'Pass':<5} | {'Fail':<5} | {'Err':<4}")
    print("-" * 80)

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_errors = 0

    for tr in tier_results:
        grand_total += tr["total"]
        grand_passed += tr["passed"]
        grand_failed += tr["failed"]
        grand_errors += tr["errors"]
        print(f"{tr['name']:<50} | {tr['total']:<6} | {tr['passed']:<5} | {tr['failed']:<5} | {tr['errors']:<4}")

    print("-" * 80)
    print(f"{'GRAND TOTAL':<50} | {grand_total:<6} | {grand_passed:<5} | {grand_failed:<5} | {grand_errors:<4}")
    print(f"Total Execution Time: {total_duration:.2f}s")
    print("=" * 80)

    if all_failures or all_errors:
        print("\nIDENTIFIED IMPLEMENTATION DEFECTS / PENDING MILESTONES:")
        for t_name, test_id, msg in all_failures:
            first_line = msg.strip().splitlines()[-1] if msg.strip() else "Assertion failed"
            print(f"  [FAIL] {test_id} ({t_name}) -> {first_line}")
        for t_name, test_id, msg in all_errors:
            first_line = msg.strip().splitlines()[-1] if msg.strip() else "Error occurred"
            print(f"  [ERROR] {test_id} ({t_name}) -> {first_line}")
        print("=" * 80)

    return grand_failed == 0 and grand_errors == 0

if __name__ == "__main__":
    success = run_tests_with_tier_breakdown()
    sys.exit(0 if success else 1)
