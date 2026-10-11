# Rhetoric, vocabulary and hedging

The vocabulary tells are easy to find and quick to fix. They are rarely the
whole problem. A text with no "delve" in it can still read as generated (see
[structural.md](structural.md)).

## Stock vocabulary (`stock_lexicon`)

delve, tapestry, testament, realm, landscape, multifaceted, holistic, nuanced,
seamless, robust, leverage, utilise, underscore, pivotal, paramount, crucial,
vital, foster, elevate, unlock, empower, streamline, game-changer,
cutting-edge, ever-evolving, intricate, meticulous, showcase, embark, vibrant,
synergy, paradigm, transformative, myriad, plethora, invaluable, harness,
comprehensive, "plays a key role", "sheds light on", "in today's world",
"navigate the", "due to the fact that", "serves to".

Replace each with the plain word, or with the specific fact it gestures at.

> tidyjson leverages a streaming parser.
>
> tidyjson uses a streaming parser.

> This change makes the pipeline more resilient.
>
> Failed deliveries are now retried three times.

Some of these are technical terms in some fields ("robust statistics",
"landscape" in optimisation). Leave those.

## Empty intensifiers (`intensifier`)

very, truly, incredibly, extremely, highly, significantly, substantially,
remarkably, fundamentally, essentially, absolutely, genuinely, blazing.

Delete the word, or replace it with the number. "Significantly" in a
scientific text should mean statistical significance and come with a test.

## Inflation without support

"novel", "first", "groundbreaking", "state-of-the-art", "powerful",
"flexible", "developer-friendly". Keep a claim only when the text supports it.
Otherwise cut it or replace it with the evidence.

## Stacked hedges (`hedge_stack`)

> These results may potentially not generalise in some cases.

Keep the one hedge that carries the real uncertainty and drop the rest. Do not
remove the last hedge from a claim that needs one.

## Narrated candour

"To be honest", "In the interest of full disclosure", "One point of honesty
about ...", "It should be acknowledged that", "flagged honestly". State the
limitation itself. Announcing honesty invites the reader to wonder about the
rest.

## Copula avoidance (`copula_avoidance`)

"serves as", "stands as", "functions as", "boasts". Use "is" or "has".

## Vague attribution

"Studies show", "Experts agree", "It has been shown that", with no citation.
Add the citation or cut the appeal.

## Synonym cycling

One concept renamed across a passage to avoid repetition (receiver, detector,
classifier). Once a term is defined, use it every time. Repetition is clearer
than variety in technical writing.

## Exclamations and emoji (`exclamation`, `emoji`)

Remove them from technical prose, READMEs and PR descriptions unless the
project's established style uses them.
