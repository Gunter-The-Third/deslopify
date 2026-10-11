# deslop

A skill for coding agents that finds AI-sounding prose and fixes it with
minimal edits, keeping the author's voice and every fact intact. It works on
Markdown, LaTeX, reStructuredText and plain text: READMEs, docs, PR
descriptions, papers and theses.

Most tools in this space ban a list of words. That catches little. Measured
against writers' own pre-AI samples, AI-assisted text differs mainly in
sentence architecture (em dashes, colon reveals, balanced semicolons,
"not X but Y") and in document habits (signposting, caveats scattered through
results, summaries that repeat the paragraph above). deslop measures those
patterns, compares them with the author's own rates when a sample is
available, and edits only what is out of line.

It aims at text a reader can follow. It does not try to beat AI detectors and
never adds typos or random variation.

## How it works

1. `slopscan.py` counts each pattern per 1,000 words and lists every hit as
   `file:line`.
2. The agent reads each hit in context against the rules in
   [`skills/deslop/rules/`](skills/deslop/rules/) and decides whether it is a
   problem. Plenty of colons and contrasts are legitimate.
3. When asked to edit, it makes sentence-level changes in the author's voice.
4. A second scan checks the rates, and `factdiff.py` checks extracted numbers,
   citations, cross-references, URLs, quotations, code and maths, including
   repeated occurrences. The agent reads the prose diff to check meaning,
   units, names and claim strength.

## Install

**Claude Code plugin**

```text
/plugin marketplace add Gunter-The-Third/deslopify
/plugin install deslop@deslop
```

**Claude Code skill (manual)**

```bash
git clone https://github.com/Gunter-The-Third/deslopify.git
cp -r deslopify/skills/deslop deslopify/skills/deslopchinese ~/.claude/skills/
```

**Other agents.** Point the agent at `skills/deslop/SKILL.md`, or copy its
contents into your agent's instruction file. The scripts need only Python 3.8+.

Then ask: "deslop the README", "review docs/ for AI tells", "tighten this PR
description".

## Commands

| Personal skill command | Behaviour |
|---|---|
| `/deslop README.md` | Edit with small sentence changes. |
| `/deslop README.md review` | Report findings. |
| `/deslop README.md max` | Also restructure padded paragraphs and repeated caveats. |
| `/deslopchinese README.md` | Alias for the maximum pass, retaining the original language. |

Plugin installs use `/deslop:deslop` and `/deslop:deslopchinese`, as
[Claude Code documents](https://code.claude.com/docs/en/skills#choose-where-skills-load).
The maximum pass keeps every fact and qualification. It leaves clear prose
alone. The scanner measures English. Other languages need a reading pass.

The main skill is short and loads only the rules needed for the task. It
scans targets together, uses compact reports and gives a brief final reply.
These reduce instruction and output text. Actual token use depends on the
model and input.

## Using the scripts directly

```bash
S=skills/deslop/scripts

# Rates per 1,000 words, with every hit listed
python3 $S/slopscan.py README.md docs/ --list

# Compact model context: nonzero features and grouped locations
python3 $S/slopscan.py README.md docs/ --compact

# Only some features
python3 $S/slopscan.py paper.tex --list --feature em_dash --feature colon_reveal

# Fail CI when the text drifts
python3 $S/slopscan.py docs/ --fail-above 2.0

# Check protected tokens in a rewrite
python3 $S/factdiff.py before.md after.md
python3 $S/factdiff.py --git HEAD README.md
```

Sample output:

```text
feature              hits  per 1k   ceil  status
em_dash                 2   11.56   1.00  HIGH
colon_reveal            1    5.78   1.00  ok (under 2 hits)
negation_parallel       2   11.56   1.00  HIGH
bold_lead_in            3   17.34   3.00  HIGH
tricolon                2   11.56   2.00  measured only
...
excess over ceilings: 82.99 per 1k words
```

A feature needs at least two hits to be marked HIGH, so a single em dash in a
short file does not count as a pattern.

## Baselines

Generic ceilings get some features backwards. One thesis author's own pre-AI
writing used lists of three at nearly three times the rate of their
AI-assisted draft, so a generic "cut tricolons" rule would have pushed that
text further from their voice. When the author has older writing, build a
baseline and the scanner will judge each feature against their own rate.
[`baselines/README.md`](baselines/README.md) explains how.

## What is detected

| Feature | Example |
|---|---|
| `em_dash` | "a different approach — it streams" |
| `colon_reveal` | "The key insight is this: ..." |
| `semicolon` | "It doesn't crash; instead, it reports ..." |
| `negation_parallel` | "It's not just a fix, it's ...", "X, not Y." |
| `signposting` | "It's worth noting", "Here's why", "In summary" |
| `stock_lexicon` | delve, leverage, robust, seamless, pivotal |
| `intensifier` | truly, incredibly, significantly |
| `hedge_stack` | "may potentially" |
| `transition_opener` | Moreover, Furthermore, Ultimately |
| `copula_avoidance` | "serves as", "boasts" |
| `bold_lead_in` | "- **Blazing Fast:** ..." |
| `rhetorical_q` | "The result? Wasted time." |
| `fragment` | "That's it!" |
| `exclamation`, `emoji` | |
| `tricolon` | measured only, unless a baseline is given |

Some patterns need a reader rather than a regex: caveats scattered through a
result, summaries that repeat the paragraph above, one concept under several
names. The skill tells the agent to read for them.

## Evals

```bash
python3 evals/run_evals.py
```

Each case in `evals/cases/` pairs a sloppy original with a reference rewrite.
The runner checks that the scanner scores the rewrite lower and that the
rewrite keeps the protected tokens. Regression tests check repeated tokens,
code whitespace, citation locators, quotations, scientific notation and compact
reports. [Example results](evals/EXAMPLES.md) show the measured edits and
instruction sizes.
To test an agent, have it write `candidate.md` (or
`.tex`) beside each `before` file. The runner then checks that the candidate
scores lower, is no more than 5% longer and keeps the protected tokens. Files in
`evals/clean/` are ordinary human prose and must score close to zero.

## Limitations

- The counts are leads for a reader to check. The scanner misses some
  patterns and flags some legitimate uses. The evals cover three reference
  rewrites and a few clean samples. They do not establish a detection rate.
- `factdiff.py` checks extracted tokens and their counts. It cannot catch a
  changed unit or a reversed claim when the protected tokens stay the same.
  Code is compared exactly, including whitespace and fence language.
- Rates on texts under about 300 words are noisy.
- Text extracted from PDFs carries captions, forms and bibliographies that
  inflate the colon and fragment counts. Strip them from baseline samples.
- English only.

## License

MIT
