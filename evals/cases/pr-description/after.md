## Summary

Retry payment webhook deliveries that fail with a 5xx response. Until now a single transient error dropped the payment silently, and roughly 0.4% of webhooks in the last 30 days were never processed.

## Changes

- Failed deliveries are retried up to 3 times with exponential backoff (1s, 4s, 16s).
- Each retry reuses the original `event_id`, so the ledger service ignores duplicates.
- A new metric, `webhook_retry_total`, counts retries and can be graphed in Grafana.

## Testing

- Unit tests cover the retry paths.
- Checked by hand against staging.
- Existing tests pass.
