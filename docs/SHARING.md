# Share Deslopify

## Short post

I built Deslopify, an open-source writing skill for coding agents. It cleans
up AI-sounding READMEs, PR descriptions and papers with small edits, author
baselines and checks for changes to numbers, citations, code and equations.
It keeps real uncertainty, including words such as “may”. There is also a
maximum pass for padded paragraphs and repeated caveats.

[Demo and installation](https://github.com/Gunter-The-Third/deslopify).

## Show HN

Title:

```text
Show HN: Deslopify, a prose-editing skill for coding agents
```

I made this while working on technical writing. I wanted edits that keep the
author's voice and the strength of each claim. The skill gives an agent a
short workflow and optional author baselines. Its two Python tools scan prose
patterns and check protected tokens.

The repo includes before/after examples and a demo you can run without a
model. The checks use only the Python standard library. Meaning still needs
a reading pass, and the small eval set does not establish a detection rate.

I'd like examples of false positives or edits that lose information.

## Image and links

- [Share image, 1200 × 630](assets/social-preview.png).
- [Vector demo](assets/demo.svg).
- [Runnable demo source](../evals/cases/quick-demo/before.md).
- [Example outputs](../evals/EXAMPLES.md).

Suggested GitHub About text:

> Writing skills for coding agents that clean up AI-sounding prose, with
> author baselines and checks for protected details.

Suggested topics: `claude-code`, `agent-skills`, `writing`, `documentation`,
`latex`, `editing`.

Use the PNG for GitHub's social preview or attach it to a post. Keep the
demo and install commands beside it so readers can try the project.
