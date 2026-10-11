#!/usr/bin/env python3
"""Run the deslop evals.

Each directory in evals/cases/ holds a sloppy `before.*` and a reference
`after.*`. An agent under test writes `candidate.*` beside them. Checks:

  scanner   the reference scores lower than the original
  facts     the reference (and any candidate) keeps every fact-bearing token
  candidate scores lower than the original and is no more than 5% longer

Every file in evals/clean/ is ordinary human prose and must score an excess of
at most CLEAN_MAX, which guards against false positives.

Exit status is 1 if any check fails.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "skills" / "deslop" / "scripts"))

import factdiff  # noqa: E402
import slopscan  # noqa: E402

CLEAN_MAX = 1.0


def score(path):
    scan = slopscan.scan_text(path.read_text(encoding="utf-8"), path.suffix, str(path))
    return slopscan.excess(scan), scan.words


def one(case_dir, stem):
    found = sorted(case_dir.glob(stem + ".*"))
    return found[0] if found else None


def main():
    suite = unittest.defaultTestLoader.discover(str(ROOT), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    failures = len(result.failures) + len(result.errors)

    def check(ok, label, detail):
        nonlocal failures
        failures += not ok
        print(f"  {'PASS' if ok else 'FAIL'}  {label:<10} {detail}")

    for case in sorted(p for p in (ROOT / "cases").iterdir() if p.is_dir()):
        before, after, cand = one(case, "before"), one(case, "after"), one(case, "candidate")
        print(case.name)
        xb, wb = score(before)
        xa, wa = score(after)
        check(xa < xb, "scanner", f"excess {xb:.1f} -> {xa:.1f} per 1k (reference)")
        fd = factdiff.compare(before.read_text(), after.read_text())
        check(fd["ok"], "facts", "reference keeps protected tokens" if fd["ok"] else str(fd["diff"]))
        if cand:
            xc, wc = score(cand)
            check(xc < xb, "candidate", f"excess {xb:.1f} -> {xc:.1f} per 1k")
            check(wc <= wb * 1.05, "length", f"{wb} -> {wc} words")
            fc = factdiff.compare(before.read_text(), cand.read_text())
            changed = {k: v for k, v in fc["diff"].items() if v["removed"] or v["added"]}
            check(fc["ok"], "cand-facts", "candidate keeps protected tokens" if fc["ok"] else str(changed))

    print("clean")
    for f in sorted((ROOT / "clean").iterdir()):
        x, _ = score(f)
        check(x <= CLEAN_MAX, f.stem[:10], f"excess {x:.2f} per 1k (max {CLEAN_MAX})")

    print(f"\n{'all checks passed' if not failures else f'{failures} check(s) failed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
