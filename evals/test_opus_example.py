"""Check the saved Opus provenance and preservation across editing levels."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXAMPLE = ROOT / "examples/opus-longform"
sys.path.insert(0, str(ROOT.parent / "skills/deslop/scripts"))
import factdiff
import slopscan

LEVELS = ("light", "standard", "max")


class OpusExampleTests(unittest.TestCase):
    def setUp(self):
        self.source = (EXAMPLE / "before.md").read_text(encoding="utf-8")
        self.manifest = json.loads((EXAMPLE / "run.json").read_text(encoding="utf-8"))

    def test_original_matches_recorded_opus_response(self):
        payload = json.loads((EXAMPLE / "responses/original.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["result"], self.source)
        self.assertTrue(any("opus" in model for model in payload["modelUsage"]))
        self.assertGreaterEqual(slopscan.scan_text(self.source, ".md").words, 500)

    def test_fallback_output_cannot_be_labelled_opus(self):
        from generate_opus_example import validate_response
        payload = {"result": "An article", "subtype": "success", "is_error": False,
                   "modelUsage": {"claude-opus-5": {"outputTokens": 0},
                                  "claude-sonnet": {"outputTokens": 1000}}}
        with self.assertRaises(ValueError):
            validate_response(payload)

    def test_every_pass_starts_from_the_same_original(self):
        source_hash = hashlib.sha256(self.source.encode("utf-8")).hexdigest()
        self.assertEqual(self.manifest["source_sha256"], source_hash)
        for level in LEVELS:
            with self.subTest(level=level):
                self.assertEqual(self.manifest["levels"][level]["source_sha256"], source_hash)
                request = (EXAMPLE / "requests" / (level + ".md")).read_text(encoding="utf-8")
                self.assertTrue(request.endswith(self.source))

    def test_edits_match_recorded_opus_responses(self):
        for level in LEVELS:
            with self.subTest(level=level):
                payload = json.loads((EXAMPLE / "responses" / (level + ".json")).read_text(encoding="utf-8"))
                edited = (EXAMPLE / (level + ".md")).read_text(encoding="utf-8")
                self.assertEqual(payload["result"], edited)
                self.assertTrue(any("opus" in model for model in payload["modelUsage"]))

    def test_all_levels_preserve_protected_tokens(self):
        for level in LEVELS:
            with self.subTest(level=level):
                edited = (EXAMPLE / (level + ".md")).read_text(encoding="utf-8")
                result = factdiff.compare(self.source, edited)
                self.assertTrue(result["ok"], result["diff"])

    def test_tables_are_unchanged(self):
        tables = [line for line in self.source.splitlines() if line.startswith("|")]
        self.assertTrue(tables)
        for level in LEVELS:
            with self.subTest(level=level):
                edited = (EXAMPLE / (level + ".md")).read_text(encoding="utf-8")
                self.assertEqual([line for line in edited.splitlines() if line.startswith("|")], tables)

    def test_reported_metrics_match_saved_articles(self):
        original = slopscan.scan_text(self.source, ".md")
        self.assertEqual(original.words, self.manifest["source_words"])
        self.assertAlmostEqual(slopscan.excess(original), self.manifest["source_excess"])
        for level in LEVELS:
            with self.subTest(level=level):
                edited = (EXAMPLE / (level + ".md")).read_text(encoding="utf-8")
                scan = slopscan.scan_text(edited, ".md")
                row = self.manifest["levels"][level]
                self.assertEqual(scan.words, row["words"])
                self.assertAlmostEqual(slopscan.excess(scan), row["excess"])
                self.assertEqual(hashlib.sha256(edited.encode("utf-8")).hexdigest(), row["sha256"])


if __name__ == "__main__":
    unittest.main()
