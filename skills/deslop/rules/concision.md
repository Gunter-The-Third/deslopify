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
> tidyjson may be slower than jq on small files.

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
