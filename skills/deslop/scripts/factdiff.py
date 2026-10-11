#!/usr/bin/env python3
"""factdiff: check that a rewrite kept every fact-bearing token.

Compares two versions of a file and reports any number, citation,
cross-reference, URL, quotation, inline code, code block or maths that
changes value or occurrence count. Code is compared exactly, including
whitespace. These checks cannot establish that prose kept its meaning,
units, names or claim strength. Exit status is 1 when anything differs.

Usage:
    factdiff.py BEFORE AFTER
    factdiff.py --git REV FILE      # compare FILE at REV (e.g. HEAD) with the working copy

Standard library only. Python 3.8+.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

CATEGORIES = ("number", "citation", "reference", "url", "quote", "inline_code", "code_block", "math")


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _take(pattern, text, bucket, group=1, flags=0, split=None, exact=False):
    """Record every match in bucket and blank it out of the text."""
    rx = re.compile(pattern, flags)
    for m in rx.finditer(text):
        val = m.group(group)
        for v in (re.split(split, val) if split else [val]):
            v = v if exact else _norm(v)
            if v:
                bucket[v] += 1
    return rx.sub(" ", text)


def extract(text: str) -> dict:
    f = {c: Counter() for c in CATEGORIES}
    t = text
    is_latex = "\\begin{" in text or "\\section" in text

    t = _take(r"(?ms)^[ \t]*(`{3,}|~{3,})[^\n]*\n(.*?)^[ \t]*\1[ \t]*$",
              t, f["code_block"], group=0, exact=True)
    t = _take(r"(?s)\\begin\{(verbatim|lstlisting|minted)\}(.*?)\\end\{\1\}",
              t, f["code_block"], group=0, exact=True)
    t = _take(r"``([^']+?)''", t, f["quote"])
    t = _take(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", t, f["inline_code"],
              group=0, flags=re.S, exact=True)
    if is_latex:
        t = re.sub(r"(?m)(?<!\\)%.*$", "", t)

    t = _take(r"(?s)\\begin\{(equation|align|gather|multline|eqnarray|displaymath)\*?\}(.*?)\\end\{\1\*?\}",
              t, f["math"], 2)
    t = _take(r"(?s)\$\$(.+?)\$\$", t, f["math"])
    t = _take(r"(?s)\\\[(.+?)\\\]", t, f["math"])
    t = _take(r"(?s)\\\((.+?)\\\)", t, f["math"])
    t = _take(r"(?<![\\$])\$(?!\s)((?:\\\$|[^$\n])+?)(?<!\s)\$", t, f["math"])

    t = _take(r"\\[a-zA-Z]*cite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}",
              t, f["citation"], group=0)
    t = _take(r"\[(@[^\]]+)\]", t, f["citation"], group=0)
    t = _take(r"\[(\d+(?:\s*[-\u2013,]\s*\d+)*)\](?!\()", t, f["citation"], group=0)
    t = _take(r"\\(?:ref|eqref|cref|Cref|autoref|pageref|vref|label)\*?\{([^}]*)\}",
              t, f["reference"], group=0)

    t = _take(r"\\(?:url|href)\{([^}]*)\}", t, f["url"])
    t = _take(r"\]\(([^)\s]+)[^)]*\)", t, f["url"])
    t = _take(r"(https?://[^\s)>\]}\"']+)", t, f["url"])

    t = _take(r"\u201c([^\u201d]+)\u201d", t, f["quote"])
    t = _take(r'"((?:\\.|[^"\\])+)"', t, f["quote"])

    t = re.sub(r"(?m)^\s*(?:\d+[.)]|#+)\s", " ", t)  # list and heading markers are not facts
    for m in re.finditer(r"(?<![\w.])[-+\u2212]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)"
                         r"(?:[eE][-+\u2212]?\d+)?%?", t):
        v = m.group(0).replace("\u2212", "-").rstrip(",")
        f["number"][v] += 1
    return f


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'\u2019-]*", text))


def compare(before: str, after: str) -> dict:
    a, b = extract(before), extract(after)
    diff = {c: {"removed": sorted((a[c] - b[c]).elements()),
                "added": sorted((b[c] - a[c]).elements())} for c in CATEGORIES}
    ok = not any(d["removed"] or d["added"] for d in diff.values())
    return {"ok": ok, "words_before": word_count(before), "words_after": word_count(after), "diff": diff}


def _git_show(rev: str, path: str) -> str:
    p = Path(path).resolve()
    top = subprocess.run(["git", "-C", str(p.parent), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = p.relative_to(Path(top).resolve()).as_posix()
    return subprocess.run(["git", "-C", top, "show", f"{rev}:{rel}"],
                          capture_output=True, text=True, check=True).stdout


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check that a rewrite kept every fact-bearing token.")
    ap.add_argument("before", help="original file, or a git revision with --git")
    ap.add_argument("after", help="rewritten file")
    ap.add_argument("--git", action="store_true", help="treat BEFORE as a git revision of AFTER")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        before = _git_show(args.before, args.after) if args.git else Path(args.before).read_text(encoding="utf-8")
        after = Path(args.after).read_text(encoding="utf-8")
    except (OSError, subprocess.CalledProcessError, ValueError) as e:
        print(f"factdiff: {e}", file=sys.stderr)
        return 2

    res = compare(before, after)
    if args.json:
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1

    wb, wa = res["words_before"], res["words_after"]
    change = (wa - wb) / wb * 100 if wb else 0.0
    label = f"{args.after}@{args.before}" if args.git else args.before
    print(f"factdiff: {label} -> {args.after}")
    print(f"words: {wb:,} -> {wa:,} ({change:+.0f}%)")
    if res["ok"]:
        print("OK: extracted numbers, citations, references, URLs, quotations, code and maths unchanged.")
        print("Read the prose diff to check meaning, units, names and claim strength.")
        return 0
    for c, d in res["diff"].items():
        for v in d["removed"]:
            print(f"  removed {c}: {v}")
        for v in d["added"]:
            print(f"  added   {c}: {v}")
    print("CHANGED: restore each item above, or tell the user why the change is correct.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
