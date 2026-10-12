# Harbour: a streaming CSV importer for order records

Harbour is a command-line tool for importing order records from CSV files into an existing ledger.

The old importer loaded the entire 2 GB file into memory before doing any work, so memory use scaled with file size. Harbour reads the file in chunks of 8,000 rows using a streaming parser, and distributes work across 4 workers. Memory use stays flat regardless of how large the file is.

## Validate before you write

Harbour validates each record before writing it. Records that fail validation are written to an error file along with their line number and the column name that failed. Records that pass are still imported: one bad row does not abort the run or block the other 199,999 rows in the file.

A file with a few rows containing a malformed date, a missing identifier or a stray value in a numeric column can therefore be imported in part, with the error report worked through separately. Under the old model the job failed, one row was fixed, and the import was run again.

If you want the validation without the writes, there is a dry run:

```
harbour import orders.csv --dry-run
```

This validates the whole file and writes the error report, but does not write anything to the ledger. Use it when a new file format shows up, or when an upstream system changes and you want to know what broke before it reaches production.

## Retries and checkpoints

A normal import reuses the `order_id` from the source record rather than generating a new identifier. The ledger ignores duplicate identifiers, so re-running an import that was interrupted will not produce duplicate entries.

It does not repair an incorrect source record. If a record was written with a wrong value and you fix the CSV and re-import, the ledger will see the same `order_id` and ignore the new version. Correcting already-imported data is a separate problem that Harbour does not solve.

Harbour also records a checkpoint after each completed chunk. If the process is interrupted, the next run resumes from the last completed checkpoint instead of starting over.

## Benchmarks

In a local test across 35 files of up to 2 GB:

| | Harbour | Old importer |
|---|---|---|
| Median import time | 4.8 s | 6.2 s |
| Peak memory | 72 MB | 1.1 GB |

The drop from 1.1 GB to 72 MB decouples memory use from file size.

These numbers come from a single Linux machine with a local SSD. Network storage or different row lengths may behave differently, and the test did not measure what happens when multiple import jobs run at the same time. If you run concurrent imports, you should measure that yourself.

## Limitations

Small files may actually be slower than under the old importer. Starting 4 workers and opening the checkpoint store both add fixed overhead, and on a small file that overhead is not amortised by anything. We do not have small-file timings to quantify this, so if your workload is mostly small files, benchmark before switching.

The supported encoding is UTF-8. Embedded newlines in quoted fields are handled correctly. Files in other encodings must be converted before import; Harbour will not do the conversion for you.

Harbour is a command-line tool. There is no web interface, no schema editor, and no remote scheduling service. It is intended to be driven by whatever you already use to run jobs.

## Rollout advice

Start with a dry run against a copy of representative data:

```
harbour import orders.csv --dry-run
```

Then work through the error report. Rows that fail here are rows the old importer was handling somehow; review these validation errors before changing behaviour in production. Compare the set of accepted records against what the old importer produces on the same input, and if the counts differ, find out why.

Verify duplicate handling explicitly before enabling production writes. Run an import, interrupt it, resume it, and confirm the ledger contains what you expect.

Once dry runs are clean and duplicate handling is confirmed on your data, enable production writes.