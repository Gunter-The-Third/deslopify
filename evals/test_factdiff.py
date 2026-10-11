"""Regression checks for edits that previously passed factdiff."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "deslop" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import factdiff


class FactdiffTests(unittest.TestCase):
    def assert_change(self, before, after, category):
        result = factdiff.compare(before, after)
        self.assertFalse(result["ok"])
        self.assertTrue(result["diff"][category]["removed"] or
                        result["diff"][category]["added"])
        return result

    def test_repeated_tokens_cannot_be_deleted_or_added(self):
        examples = {
            "number": "Accuracy was 94.2%.",
            "citation": r"The result holds \cite{smith2020}.",
            "reference": r"See Figure~\ref{fig:loss}.",
            "url": "Read https://example.org/guide for details.",
            "quote": 'The response was "try again".',
            "inline_code": "Call `run()` once.",
            "code_block": "```python\nrun()\n```\n",
            "math": r"The loss is $x^2$.",
        }
        for category, text in examples.items():
            for before, after, direction in ((text + "\n\n" + text, text, "removed"),
                                             (text, text + "\n\n" + text, "added")):
                with self.subTest(category=category, direction=direction):
                    result = self.assert_change(before, after, category)
                    self.assertEqual(len(result["diff"][category][direction]), 1)

    def test_fenced_code_indentation_is_preserved(self):
        self.assert_change("```python\nif ready:\n    run()\nfinish()\n```\n",
                           "```python\nif ready:\n    run()\n    finish()\n```\n", "code_block")

    def test_code_string_whitespace_is_preserved(self):
        self.assert_change('```python\nprint("a  b")\n```\n',
                           '```python\nprint("a b")\n```\n', "code_block")

    def test_fence_language_is_preserved(self):
        self.assert_change("```python\nrun()\n```\n", "```bash\nrun()\n```\n", "code_block")

    def test_tilde_fence_is_protected(self):
        self.assert_change("~~~text\na  b\n~~~\n", "~~~text\na b\n~~~\n", "code_block")

    def test_latex_code_indentation_is_preserved(self):
        self.assert_change("\\begin{lstlisting}\nif ready:\n    run()\nfinish()\n\\end{lstlisting}",
                           "\\begin{lstlisting}\nif ready:\n    run()\n    finish()\n\\end{lstlisting}",
                           "code_block")

    def test_percent_in_latex_code_is_not_a_comment(self):
        self.assert_change("\\begin{lstlisting}\nvalue = n % 2\n\\end{lstlisting}",
                           "\\begin{lstlisting}\nvalue = n % 3\n\\end{lstlisting}", "code_block")

    def test_latex_code_options_are_preserved(self):
        self.assert_change(r"\begin{minted}{python}run()\end{minted}",
                           r"\begin{minted}{bash}run()\end{minted}", "code_block")

    def test_inline_code_whitespace_is_preserved(self):
        self.assert_change('Use `print("a  b")`.', 'Use `print("a b")`.', "inline_code")

    def test_multiple_backtick_code_is_protected(self):
        self.assert_change('Use ``print("`a  b`")``.', 'Use ``print("`a b`")``.', "inline_code")

    def test_citation_locator_is_preserved(self):
        self.assert_change(r"The result holds \cite[p.~12]{smith2020}.",
                           r"The result holds \cite[p.~99]{smith2020}.", "citation")

    def test_reference_command_is_preserved(self):
        self.assert_change(r"See \eqref{eq:loss}.", r"See \ref{eq:loss}.", "reference")

    def test_short_quotes_are_protected(self):
        for before, after in (('The response was "try again".', 'The response was "all done".'),
                              ('The response was “yes”.', 'The response was “no”.')):
            with self.subTest(before=before):
                self.assert_change(before, after, "quote")

    def test_multiline_quote_is_protected(self):
        self.assert_change('The response was “please\ntry again”.',
                           'The response was “please\nstop now”.', "quote")

    def test_latex_quotes_do_not_capture_surrounding_prose(self):
        before = "They said ``try again''. We measured 3 ms. They said ``all done''."
        after = "They said ``try again''. The interval is 3 ms. They said ``all done''."
        self.assertTrue(factdiff.compare(before, after)["ok"])
        self.assert_change(before, before.replace("try again", "try later"), "quote")

    def test_scientific_notation_is_protected(self):
        for before, after in (("1e3", "1e6"), ("2.5E+8", "2.5E+9"), ("1e-3", "1e-6")):
            with self.subTest(before=before):
                result = self.assert_change("Tolerance is " + before + ".",
                                            "Tolerance is " + after + ".", "number")
                self.assertEqual(result["diff"]["number"]["removed"], [before])
                self.assertEqual(result["diff"]["number"]["added"], [after])

    def test_leading_decimal_is_protected(self):
        result = self.assert_change("Probability is .05.", "Probability is .01.", "number")
        self.assertEqual(result["diff"]["number"]["removed"], [".05"])

    def test_prose_reordering_and_rewrapping_are_allowed(self):
        before = "Latency was 3 ms. Accuracy was 94.2%."
        after = "Accuracy was 94.2%.\nThe measured latency was 3 ms."
        self.assertTrue(factdiff.compare(before, after)["ok"])

    def test_semantic_changes_need_manual_review(self):
        for before, after in (("The method improves accuracy.", "The method reduces accuracy."),
                              ("The interval is 3 ms.", "The interval is 3 s.")):
            with self.subTest(before=before):
                self.assertTrue(factdiff.compare(before, after)["ok"])

    def test_cli_exit_status_and_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            before, after = Path(tmp) / "before.md", Path(tmp) / "after.md"
            before.write_text("Tolerance is 1e3.", encoding="utf-8")
            for text, status in (("The tolerance is 1e3.", 0), ("The tolerance is 1e6.", 1)):
                after.write_text(text, encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPTS / "factdiff.py"),
                                         str(before), str(after), "--json"],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertEqual(json.loads(result.stdout)["ok"], status == 0)


if __name__ == "__main__":
    unittest.main()
