# Baselines

A baseline is the author's own writing from before they used AI tools. The
scanner measures it the same way it measures the draft, and then judges each
feature against the author's rate instead of a generic ceiling. Without one, a
tool will cut patterns the author has always used: lists of three, an
occasional colon, their own connectives.

## Making one

1. Collect at least 5,000 words, ideally more, in the same genre as the text
   you will scan (a thesis against old reports, a README against old docs).
   Writing from before 2023 is safest.
2. Remove material the author did not write in their own voice: front matter,
   forms, bibliographies, figure and table captions, code listings and quoted
   passages. Text extracted from a PDF needs this most.
3. Save the rates, not the text:

   ```bash
   python3 skills/deslop/scripts/slopscan.py --save-baseline baselines/alex.json samples/*.txt
   ```

The `.json` holds only per-feature rates, word counts and file names, so it can
be committed without publishing the samples. `baselines/samples/` is
git-ignored for raw text.

## Using one

```bash
python3 skills/deslop/scripts/slopscan.py draft.md --baseline baselines/alex.json
```

A feature is HIGH when its rate exceeds both twice the baseline and the
baseline plus 0.5 per 1,000 words. A feature at under half the author's rate
is marked "below baseline: leave alone".
