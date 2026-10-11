---
name: deslop
description: Remove AI-sounding prose with minimal edits that preserve voice and meaning. Use for deslop, de-AI, humanise or tighten requests; review requests report findings without editing.
---

# Deslop

Work on the named files or supplied text. `/deslop FILE` requests edits.
`/deslop FILE review` requests findings. `/deslop FILE max` requests a
thorough pass. With no target, ask for one.

## Preserve

Keep the language, spelling variety, voice, terminology and claim strength.
Preserve every number, unit, citation, cross-reference, URL, name, defined
term, quotation, equation and code span or block. Leave front matter, tables,
licences, generated files and other authors' quotations alone unless asked.
Keep real uncertainty when removing stacked hedges. Never invent facts,
confidence, typos or random variation. A lower score alone is not success.

## Work

1. Resolve `scripts/` relative to this skill file, independent of the working
   directory. Scan English prose in one batch with `slopscan.py --compact`.
   Use a supplied or established baseline with `--baseline`. Otherwise state
   that built-in ceilings were used. Leave features marked below baseline.
   The scanner measures English only. Review other languages by reading.
2. Read each target once in context. Consult only the needed rules:
   [structural](rules/structural.md) for sentence frames,
   [rhetoric](rules/rhetoric.md) for vocabulary or hedges,
   [concision](rules/concision.md) for repetition or structure,
   [formats](rules/formats.md) for genre-specific decisions.
   Keep legitimate contrasts, list introductions and technical terms.
3. Remove empty signposting, hype, runway sentences and mirror summaries.
   Fix repeated sentence frames. Default to small sentence edits. In `max`
   mode, also merge padded paragraphs and repeated caveats while retaining
   every qualification. Leave clear prose alone. Do not chase a zero score.
4. For edits, keep a temporary original of each target. Re-scan once, run
   `factdiff.py ORIGINAL EDITED`, and read the diff for meaning, units, names
   and claim strength. Restore accidental changes. Explain intended token
   changes. Check length. Extra words need a reason.

## Reply

For supplied text, return only the edited text unless asked to explain.
For files, report words and excess before/after, baseline used and verification
in a short paragraph. For review, give up to three actionable findings with
`file:line` and a minimal rewrite. Mention legitimate hits only when useful.
Load neither all rules nor full scan tables by default.
