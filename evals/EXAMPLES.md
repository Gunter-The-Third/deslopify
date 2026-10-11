# Example runs

On 12 October 2026, the current Codex assistant rewrote the three English
fixtures using the compact skill instructions. `candidate.*` files were
checked with `python3 evals/run_evals.py`. These were edits by the assistant
in this session, rather than independent Claude slash-command runs. Claude
Code was installed but signed out. The scores use built-in ceilings.

| Example | Prose words | Excess per 1,000 words | Protected tokens | Smaller scan output |
|---|---:|---:|---|---:|
| readme | 173 → 63 | 82.99 → 0.00 | pass | 69% |
| pr-description | 167 → 91 | 54.88 → 0.00 | pass | 69% |
| results-section | 143 → 107 | 71.92 → 0.00 | pass | 75% |

Both clean samples scored 0.00 and were left unchanged. The technical note
contains “robust statistics”, a legitimate term that a reader should keep.
Rates on these short fixtures are noisy. The score is an editing aid, and
these examples do not measure detection accuracy.

The main skill went from 795 to 362 whitespace-separated words (54% fewer).
The maximum-mode alias adds 126 words and reads the same core workflow.
Compact output was 69–75% smaller in characters than `--list` for
these three sources. Character and word counts are proxies for context size,
not measurements of model tokens or total inference cost.

Manual review retained the README's “may be slower”, the PR's transient
failure qualifier, and the results section's uncertainty, fixed budget and
absence of faster training. It also found two problems in the old reference
rewrites: the README had made a tentative claim definite, and the results
section had lost the training-speed statement and weakened the initialisation
claim. Those references now preserve the source claims.

The scanner can accept clear prose containing legitimate technical terms.
`factdiff` cannot establish meaning preservation. Both checks need a reader.

## Outputs

### readme

Source: [before.md](cases/readme/before.md).

````markdown
# tidyjson

tidyjson formats JSON with a streaming parser. It handles files of up to 2 GB
and uses around 40 MB of memory regardless of input size.

## Features

- Malformed input does not crash the tool. It reports the line and column of the first error.
- It works as a drop-in replacement for `python -m json.tool`.

## Limitations

tidyjson may be slower than jq on very small files.

## Install

```bash
pip install tidyjson
```

Run `tidyjson input.json`.
````

### pr-description

Source: [before.md](cases/pr-description/before.md).

````markdown
## Summary

Retry payment webhook deliveries that fail with a 5xx response. Previously,
a transient error could silently drop a payment. Roughly 0.4% of webhooks
in the last 30 days were never processed.

## Changes

- Failed deliveries are retried up to 3 times with exponential backoff (1s, 4s, 16s).
- Each retry reuses the original `event_id`, so the downstream ledger service ignores duplicate deliveries.
- The new `webhook_retry_total` metric tracks retries for monitoring in Grafana.

## Testing

- Added unit tests for the retry paths.
- Verified the behaviour by hand against staging.
- All existing tests pass.
````

### results-section

Source: [before.tex](cases/results-section/before.tex).

````tex
\section{Results}

The proposed method achieves 94.2\% accuracy on the held-out test set, compared with 91.7\% for the baseline \cite{smith2020}. The improvement holds across all five random seeds (Table~\ref{tab:seeds}).

The learned initialisation places the weights closer to a good minimum. After one epoch, the training loss is 0.83 for the proposed method and 1.41 for the baseline, a reduction of 41\% (Figure~\ref{fig:loss}). The method does not train faster. The gain comes from the starting point.

The method was evaluated only on CIFAR-10, with the training budget fixed at 200 epochs. The fixed budget could favour methods that converge quickly. The results may not generalise to other datasets.
````
