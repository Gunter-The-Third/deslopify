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
