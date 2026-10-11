# Guidance by format

## README

- Open with one or two sentences: what it does and for whom. No "Overview"
  heading, no emoji headings, no "Why X?" section that sells.
- Show install and a minimal usage example early. Code beats description.
- Put limitations in their own short section. A README that admits jq is
  faster on small files is more credible than one that says "blazing fast".
- No "Conclusion" or "Give it a try today!".
- Features as plain bullets that each state a fact, without bold labels.

## Pull request description

- Summary: what changed and why, in one to three sentences. Lead with the
  problem it fixes and its measured impact.
- Changes: one bullet per behaviour change, not per file.
- Testing: what was run, in plain bullets.
- No "This PR introduces", no "robust", no closing summary, no "Let me know if
  you have any questions!".

## Commit message

- Subject in the imperative, under about 72 characters, no full stop.
- Body only when the why is not obvious from the diff.
- Never "This commit ...", "Enhance", "Streamline" or bullet lists that
  repeat the diff.

## Paper or thesis

- Keep the field's conventions: section structure, passive voice where the
  field expects it, defined terms, formal register.
- Never touch equations, theorem statements, citations, labels or numbers.
  Ask before editing captions or proofs.
- Most of the work is structural: colon reveals, balanced semicolons,
  "not X but Y", interleaved caveats, mirror summaries at the end of sections.
- Respect the author's spelling variety and person. If they never write "we",
  do not introduce it.

## Code comments and docstrings

Out of scope unless the user asks. When asked: delete comments that restate
the code, keep comments that explain why, and do not change docstrings that
tools parse (argument names, types, doctest examples).
