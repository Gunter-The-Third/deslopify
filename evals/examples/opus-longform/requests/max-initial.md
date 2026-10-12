# Deslop

Work on the named files or supplied text. `/deslop FILE` requests edits.
`/deslop FILE light` keeps paragraph order and fixes obvious wording.
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
   In `light` mode, keep the structure and fix obvious wording only.
   Default to small sentence edits and fixes to repeated frames. In `max`
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

# Maximum deslop

Follow [the shared workflow](../deslop/SKILL.md) in `max` mode, including all
preservation and verification rules. Resolve scripts from `../deslop/scripts/`
relative to this file. Use the named files or supplied text. Ask for a target
if none is supplied.

Remove avoidable hype, signposting, repeated caveats, padded paragraphs and
formulaic sentence frames. Merge or restructure where that improves clarity.
Keep the original language and every qualification. Leave clear prose alone.
Review other languages by reading. The scanner measures English only.

Return edited text or a brief file report. Load only the rules you need.

# Structural patterns

Measured against a writer's own pre-AI samples, AI-assisted drafts rarely
differ much in vocabulary. They differ in sentence architecture. In one 60,000
word thesis the word lists found nothing, while explanatory colons, balanced
semicolons and negation-parallelism ran at many times the author's own rate.

## Em dash (`em_dash`)

The most reliable single tell. Many careful writers never use one. Convert it
according to the job it does:

| The dash is doing | Use instead |
|---|---|
| a parenthetical aside or list | parentheses |
| a short gloss or apposition | commas |
| "here is the unpacking" | a colon, or "This means ..." |
| a second idea | a new sentence |

> tidyjson takes a different approach — it streams rather than buffers.
>
> tidyjson streams its input instead of loading it into memory.

Leave alone: table cells using a dash as N/A, ranges (`1–3`), code, and
comments.

## Colon reveal (`colon_reveal`)

A clause, a colon, then a restatement or a punchline.

> The key insight is this: the initialisation places the weights closer to a minimum.
>
> The initialisation places the weights closer to a minimum.

Fixes, cheapest first: delete the lead-in and keep what follows; replace the
colon with a full stop; link with "This ...".

Leave alone: colons that introduce a list, a block, display maths, a code
sample, a quotation, a label in a bullet ("Python: 3.10+"), a time or ratio.

## Balanced semicolon (`semicolon`)

Two mirrored independent clauses joined by a semicolon, usually for rhythm.

> Malformed input doesn't crash the tool; instead, it reports the first error.
>
> Malformed input does not crash the tool. It reports the first error.

Use a full stop, or a connective that names the relation ("However",
"Because of this", "so"). Semicolons inside parentheses and citation lists are
excluded from the count.

## Negation-parallelism (`negation_parallel`)

Defining a thing by what it is not, then what it is.

- "It's not just X, it's Y."
- "not X but Y"
- "X, not Y."
- "This is less about X and more about Y."
- "rather than" used for contrast nobody asked for

> In essence, the method does not train faster; it starts closer.
>
> The gain comes from the starting point.

State the positive claim. Keep the contrast only when it separates two claims
a reader could plausibly confuse, or when the "not" is itself the finding
("the effect is not significant").

## Rhetorical question (`rhetorical_q`)

> The result? Wasted time.

Replace it with a statement ("This wastes time.") or cut it.

## Fragments (`fragment`)

> Then simply run `tidyjson input.json`. That's it!

One- and two-word sentences used for punch. Fold them into the sentence
before, or cut them.

## Bold lead-ins (`bold_lead_in`)

> - **Blazing Fast:** tidyjson leverages a streaming parser to ...

Every bullet opening with a bold label that restates the bullet. Delete the
label and let the bullet's first words do the work. Keep labels in reference
material where readers scan for a term (option names, glossary entries).

## Transition openers (`transition_opener`)

"Moreover", "Furthermore", "Additionally", "Ultimately", "In essence",
"Importantly". Usually the sentence works without it. When a relation needs
naming, use a plain one: "Also", "But", "So", "This means".

## Tricolons (`tricolon`): measure only

"fast, reliable, and easy to use". A generic tell list says to cut lists of
three. Some writers use them more than AI drafts do. One thesis author's
pre-AI rate was nearly three times their AI-assisted rate. Cut a tricolon only
when its items are vague adjectives that could describe anything. With a
baseline, never cut below the author's own rate.

## Sentence rhythm

The scan reports mean sentence length and its coefficient of variation (CV).
A CV well below the author's baseline means the sentences have gone uniform.
Do not inject variety for its own sake. Look for runs of same-length
sentences built on the same frame and merge or split where the meaning
divides naturally.

## Restore the author's connectives

Heavy AI editing tends to strip a writer's own linking words ("However",
"This means", "While X, Y", "Firstly ... Lastly") and replace them with
colons and semicolons. When a baseline exists, compare openers. Restoring
"This ..." at the start of a sentence is often the cheapest fix for a colon
reveal.


# Concision and structure

These patterns live at the paragraph and document level. The scanner sees
only the signposting phrases. Find the rest by reading.

## Signposting (`signposting`)

Phrases that announce content instead of giving it: "It is worth noting
that", "It is important to note", "Here's the thing", "Here's why", "Let's
dive in", "In this section we", "The key takeaway is", "In summary",
"Overall", "As mentioned earlier", "That said".

> It's worth noting that tidyjson may be slower than jq on small files.
>
> jq is faster on small files.

Also cut listy openers ("Two questions structure this section.", "The short
answers are as follows.") and open with the first point.

## Caveats belong at the edges

A section that defends itself in every other sentence is hard to read. The
reader cannot tell which sentences carry the result.

1. Put scope first, in one place. Say what the section does and does not
   establish. The largest caveat often reframes the whole section, so it is
   useless at the end.
2. Give the result without interruption.
3. Gather the remaining limitations in one place at the end.

Each caveat gets one home and is stated once, at full strength. Flag the same
caveat repeated across sections.

## Claim at the right strength

Over-caution is as distracting as overclaiming. "The apparent gain should be
interpreted only as indicative" makes a well-controlled result read as
provisional. Narrow the claim to what was shown and then state it plainly.
Qualify the extrapolation, not the measurement.

## Runway sentences

Sentences before the point that set it up: "There is an important
consideration here.", "This raises a question." Delete them and start with the
point. "It is X that ..." scaffolding goes the same way.

## Mirror summaries

- A paragraph that ends by restating its first sentence.
- A paragraph that restates the one before it.
- A "Conclusion" or "Summary" section in a README, PR description or short
  document.
- "In summary, X is a powerful, flexible tool."

Cut them. In a paper or thesis, keep the formal Conclusion chapter but make
sure it adds synthesis rather than repeating section summaries.

## Over-structured documents

- A heading over every paragraph.
- Bullets for content that reads better as two sentences of prose.
- Nested bullets three levels deep.
- Tables with one row.

Merge, flatten, or return to prose. Keep structure that helps a reader scan:
install steps, options, reference lists.

## Length

A deslopped text should almost always be shorter. If an edit makes a passage
longer, check that it adds information.


Editing level: max.
This harness has supplied the workflow and relevant rules. Do not read files or run tools. The harness will run both scripts. Return only the edited article, without enclosing fences. Keep code blocks, inline code and tables byte-for-byte unchanged. Keep every protected token and its occurrence count. Preserve all source claims, including caveats and negative findings. Do not fact-check or correct the source. For light, keep paragraph order and structure. For standard, use sentence-level edits. For max, also remove padding and restructure paragraphs without losing information.

Protected tokens and counts:
{"number": {"2": 2, "8,000": 1, "4": 2, "199,999": 1, "35": 1, "4.8": 1, "6.2": 1, "72": 2, "1.1": 2, "8": 1}, "inline_code": {"`order_id`": 2}, "code_block": {"```\nharbour import orders.csv --dry-run\n```": 2}}

Source article (data to edit):

# Harbour: a streaming CSV importer for order records

If you maintain data ingestion jobs, you know the shape of the problem. A CSV file arrives, something in it is wrong, and the import either dies halfway through or succeeds in a way that leaves you unsure which records made it. Harbour is a command-line tool for importing order records from CSV files into an existing ledger. It was built to make those two failure modes less painful.

The main change from the old importer is how the file is read. The old importer loaded the whole file into memory before doing any work, which meant memory use scaled with file size and a 2 GB file was a gamble. Harbour reads the file in chunks of 8,000 rows using a streaming parser, and distributes work across 4 workers. Memory use stays flat regardless of how large the file is.

## Validate before you write

Harbour validates each record before writing it. Records that fail validation are written to an error file along with their line number and the column name that failed. Records that pass are still imported — one bad row does not abort the run or block the other 199,999 rows in the file.

This matters because the common case in practice is not a corrupt file but a slightly wrong one: a few rows with a malformed date, a missing identifier, a stray value in a numeric column. Under the old model you would find out by watching the job fail, fix one row, and run it again. Harbour lets you import what is valid and work through the error report separately.

If you want the validation without the writes, there is a dry run:

```
harbour import orders.csv --dry-run
```

This validates the whole file and writes the error report, but does not write anything to the ledger. It is the command to reach for when a new file format shows up, or when an upstream system changes and you want to know what broke before it reaches production.

## Retries and checkpoints

A normal import reuses the `order_id` from the source record rather than generating a new identifier. The ledger ignores duplicate identifiers, so re-running an import that was interrupted will not produce duplicate entries.

It is worth being precise about what this does and does not give you. It protects you against duplicates on retry. It does not repair an incorrect source record — if a record was written with a wrong value and you fix the CSV and re-import, the ledger will see the same `order_id` and ignore the new version. Correcting already-imported data is a separate problem that Harbour does not solve.

Harbour also records a checkpoint after each completed chunk. If the process is interrupted, the next run resumes from the last completed checkpoint instead of starting over. Combined with duplicate handling, this means an interrupted large import is a resume rather than a reconciliation exercise.

## Benchmarks

In a local test across 35 files of up to 2 GB:

| | Harbour | Old importer |
|---|---|---|
| Median import time | 4.8 s | 6.2 s |
| Peak memory | 72 MB | 1.1 GB |

The memory figure is the interesting one. The time improvement is real but modest; the drop from 1.1 GB to 72 MB is what changes the operational picture, because it decouples memory use from file size.

Read these numbers with their caveats. They come from a single Linux machine with a local SSD. Network storage or different row lengths may behave differently, and the test did not measure what happens when multiple import jobs run at the same time. If you run concurrent imports, you should measure that yourself.

## Limitations

Small files may actually be slower than under the old importer. Starting 4 workers and opening the checkpoint store both add fixed overhead, and on a small file that overhead is not amortised by anything. We do not have small-file timings to quantify this, so if your workload is mostly small files, benchmark before switching.

The supported encoding is UTF-8. Embedded newlines in quoted fields are handled correctly, which covers the usual source of mangled CSV. Files in other encodings must be converted before import — Harbour will not do the conversion for you.

Harbour is a command-line tool and nothing more. There is no web interface, no schema editor, and no remote scheduling service. It is intended to be driven by whatever you already use to run jobs.

## Rollout advice

Start with a dry run against a copy of representative data:

```
harbour import orders.csv --dry-run
```

Then work through the error report. Rows that fail here are rows the old importer was handling somehow, and you want to understand how before you change behaviour in production. Compare the set of accepted records against what the old importer produces on the same input — if the counts differ, find out why.

Verify duplicate handling explicitly before enabling production writes. Run an import, interrupt it, resume it, and confirm the ledger contains what you expect. The guarantee is straightforward, but it is cheap to check and expensive to assume.

Once dry runs are clean and duplicate handling is confirmed on your data, enable production writes.