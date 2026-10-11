## Summary

This PR introduces a robust retry mechanism for the payment webhook handler. It's not just a bug fix — it's a fundamental improvement to how we handle transient failures.

## What Changed

- **Retry Logic:** Webhook deliveries that fail with a 5xx response are now retried up to 3 times with exponential backoff (1s, 4s, 16s).
- **Idempotency:** Each retry reuses the original `event_id`, ensuring that duplicate deliveries are seamlessly ignored by the downstream ledger service.
- **Observability:** A new metric, `webhook_retry_total`, tracks retries; this allows us to monitor retry rates in Grafana.

## Why This Matters

Previously, a single transient error could cause a payment to be silently dropped. The impact? Roughly 0.4% of webhooks in the last 30 days were never processed. This change significantly reduces that risk.

## Testing

It's worth noting that I've added comprehensive unit tests covering the retry paths. Additionally, I've manually verified the behaviour against the staging environment. Moreover, all existing tests pass.

## Conclusion

Overall, this change makes our payment pipeline more resilient, reliable, and maintainable. Let me know if you have any questions!
