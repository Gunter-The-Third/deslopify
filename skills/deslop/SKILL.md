---
name: deslop
description: Find and fix AI-sounding prose in Markdown, LaTeX and plain-text files (em dashes, colon reveals, "not X but Y", signposting, stock vocabulary, stacked hedges, caveats scattered through results, padded summaries) with minimal edits that keep the author's voice and every fact. Use when asked to deslop, de-AI, humanise, tighten or clean up writing, or to review a README, docs, PR description, paper or thesis for AI tells.
---

# Deslop

The goal is prose a reader can follow quickly, in the author's own voice. Fix a
pattern only when the fix makes the writing better for the reader. This skill
does not try to beat AI detectors, and it never adds typos, slang or random
variation to make text look human.

Two scripts sit in `scripts/` beside this file. Both use only the Python
standard library (3.8+).

- `slopscan.py` counts each tell per 1,000 words, compares the rate with a
  ceiling and lists every hit as `file:line`.
- `factdiff.py` compares extracted numbers, citations, cross-references,
  URLs, quotations, code and maths, including occurrence counts. It compares
  code exactly. It cannot check prose meaning, units, names or claim strength.

## Workflow

1. **Scope.** Use the files the user named. If they named a directory or a
   repo, take its prose: `*.md`, `*.tex`, `*.rst`, `*.txt`, docs folders, the
   README. Leave out generated files, vendored code, changelogs written by
   tools, licences and legal text, and anything quoted from someone else.
2. **Baseline.** Ask whether the author has writing from before they used AI
   tools (ideally 5,000+ words in the same genre). If they do, build a
   baseline with `slopscan.py --save-baseline baseline.json <their files>` and
   pass `--baseline baseline.json` from then on. Without one, the scanner uses
   rough built-in ceilings. Say which one the report used.
3. **Scan.** `python3 scripts/slopscan.py <paths> [--baseline B] --list`
4. **Triage.** Read each hit in context and decide whether it is a real
   problem. The rules files explain each pattern and its legitimate uses.
   Then read the text yourself for what a regex cannot see: summaries that
   repeat the paragraph above, caveats scattered through a result, runway
   sentences, one concept under several names, a heading for every
   paragraph. The scanner is a heuristic. The evals do not establish its
   detection rate.
5. **Report or edit.** Report by default. Edit only when the user asks you to
   fix, edit, rewrite or deslop the files.
6. **Verify every edit.**
   - Re-run `slopscan.py` and confirm the flagged rates fell.
   - Run `factdiff.py BEFORE AFTER`, or `factdiff.py --git HEAD FILE` in a
     git repo. Any difference it reports must be restored, or explained to
     the user if the change is correct.
   - Read the prose diff for changed meaning, units, names, defined terms and
     claim strength, even when `factdiff.py` passes. A lower scan score alone
     does not establish a better rewrite.
   - Confirm the text got shorter or stayed the same length.

## Rules

Read these when triaging. They are short.

- [rules/structural.md](rules/structural.md): sentence architecture. This is
  where most of the signal is.
- [rules/rhetoric.md](rules/rhetoric.md): vocabulary, inflation, hedging and
  narrated candour.
- [rules/concision.md](rules/concision.md): caveat placement, signposting,
  repetition and document structure.
- [rules/formats.md](rules/formats.md): READMEs, PR descriptions, commit
  messages, papers and code comments.

## Hard rules

- Never change a number, unit, citation, cross-reference, URL, code, maths,
  quotation, name or defined term. Check units, names and defined terms by
  reading the diff. `factdiff.py` checks the extracted tokens.
- Do not change how strongly a claim is made. When removing a stacked hedge,
  keep the hedge that carries the real uncertainty. Do not add confidence the
  evidence does not support.
- Make the smallest edit that fixes the problem. Rewrite at the sentence
  level and leave sound sentences alone.
- Keep the author's voice: their spelling (Australian, British, American),
  terminology, person (first person or not) and habitual connectives.
- When a baseline says a feature is "below baseline: leave alone", do not edit
  it. Cutting it further moves the text away from the author.
- Do not touch code blocks, inline code, front matter, tables, quotations,
  licence text or generated files unless the user asks.
- One finding the user can act on beats five they have to argue with. When a
  hit is a judgement call, put it under "Left alone" with the reason.

## Report format

1. **Summary.** Words scanned, baseline used, the features marked HIGH, and the
   two or three changes that would help the reader most.
2. **Findings**, worst first. Each has `file:line`, a verbatim quote of at most
   two lines, the pattern, and a minimal rewrite (or "cut" when the sentence
   carries no information).
3. **Left alone.** Hits you judged legitimate, and why.

After editing, report instead: files changed, the excess before and after,
words before and after, and the `factdiff` result for each file.
