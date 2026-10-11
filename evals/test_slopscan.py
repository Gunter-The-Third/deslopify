"""Compact reports retain findings and scoring with less output."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT.parent / "skills" / "deslop" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import slopscan


class CompactReportTests(unittest.TestCase):
    def setUp(self):
        self.source = ROOT / "cases" / "readme" / "before.md"
        self.scan = slopscan.scan_text(self.source.read_text(encoding="utf-8"), ".md", "before.md")

    def test_every_finding_keeps_its_feature_and_location(self):
        compact = slopscan.report(self.scan, None, False, None, compact=True)
        for hit in self.scan.hits:
            with self.subTest(feature=hit.feature, line=hit.line):
                location = "{}:{}  [".format(hit.path, hit.line)
                rows = [line for line in compact.splitlines() if line.startswith(location)]
                self.assertEqual(len(rows), 1)
                self.assertIn(hit.feature, rows[0])

    def test_compact_removes_duplicate_snippets_and_zero_rows(self):
        full = slopscan.report(self.scan, None, True, None)
        compact = slopscan.report(self.scan, None, False, None, compact=True)
        self.assertLess(len(compact), len(full) * 0.65)
        for feature, count in self.scan.counts().items():
            if count == 0:
                self.assertNotIn(feature + ":", compact)

    def test_baseline_guidance_is_retained(self):
        baseline = slopscan.baseline_from_scan(self.scan, ["author.md"])
        baseline["rates"]["em_dash"] = 100.0
        compact = slopscan.report(self.scan, baseline, False, None, compact=True)
        self.assertIn("baseline: author.md", compact)
        self.assertIn("below baseline: leave alone", compact)

    def test_feature_filter_keeps_matching_locations(self):
        compact = slopscan.report(self.scan, None, False, {"em_dash"}, compact=True)
        self.assertIn("em_dash:", compact)
        self.assertNotIn("stock_lexicon", compact)
        for hit in self.scan.hits:
            if hit.feature == "em_dash":
                self.assertIn("{}:{}  [em_dash]".format(hit.path, hit.line), compact)

    def test_clean_text_is_valid_without_findings(self):
        scan = slopscan.scan_text("The sensor stayed above 12.4 V overnight.", ".md")
        compact = slopscan.report(scan, None, False, None, compact=True)
        self.assertEqual(scan.hits, [])
        self.assertIn("excess over ceilings: 0.00", compact)

    def test_cli_scores_and_exit_status_are_unchanged(self):
        base = [sys.executable, str(SCRIPTS / "slopscan.py"), str(self.source), "--fail-above", "2"]
        full = subprocess.run(base, capture_output=True, text=True)
        compact = subprocess.run(base + ["--compact"], capture_output=True, text=True)
        self.assertEqual(full.returncode, 1, full.stderr)
        self.assertEqual(compact.returncode, full.returncode, compact.stderr)
        summary = "excess over ceilings: {:.2f} per 1k words".format(slopscan.excess(self.scan))
        self.assertIn(summary, full.stdout)
        self.assertIn(summary, compact.stdout)

    def test_json_stays_complete_with_compact_flag(self):
        base = [sys.executable, str(SCRIPTS / "slopscan.py"), str(self.source), "--json"]
        full = subprocess.run(base, capture_output=True, text=True, check=True)
        compact = subprocess.run(base + ["--compact"], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(full.stdout), json.loads(compact.stdout))


if __name__ == "__main__":
    unittest.main()
