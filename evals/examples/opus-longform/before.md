# Harbour: a streaming CSV importer for order records

If you maintain data ingestion jobs, you know the shape of the problem. A CSV file arrives, something in it is wrong, and the import either dies halfway through or succeeds in a way that leaves you unsure which records made it. Harbour is a command-line tool for importing order records from CSV files into an existing ledger. It was built to make those two failure modes less painful.

The main change from the old importer is how the file is read. The old importer loaded the whole file into memory before doing any work, which meant memory use scaled with file size and a 2 GB file was a gamble. Harbour reads the file in chunks of 8,000 rows using a streaming parser, and distributes work across 4 workers. Memory use stays flat regardless of how large the file is.

## Validate before you write

Harbour validates each record before writing it. Records that fail validation are written to an error file along with their line number and the column name that failed. Records that pass are still imported — one bad row does not abort the run or block the other 199,999 rows in the file.

This matters because the common case in practice is not a corrupt file but a slightly wrong one: a few rows with a malformed date, a missing identifier, a stray value in a numeric column. Under the old model you would find out by watching the job fail, fix one row, and run it again. Harbour lets you import what is valid and work through the error report separately.

If you want the validation without the writes, there is a dry run:

```
harbour import orders.csv --dry-run
```

This validates the whole file and writes the error report, but does not write anything to the ledger. It is the command to reach for when a new file format shows up, or when an upstream system changes and you want to know what broke before it reaches production.

## Retries and checkpoints

A normal import reuses the `order_id` from the source record rather than generating a new identifier. The ledger ignores duplicate identifiers, so re-running an import that was interrupted will not produce duplicate entries.

It is worth being precise about what this does and does not give you. It protects you against duplicates on retry. It does not repair an incorrect source record — if a record was written with a wrong value and you fix the CSV and re-import, the ledger will see the same `order_id` and ignore the new version. Correcting already-imported data is a separate problem that Harbour does not solve.

Harbour also records a checkpoint after each completed chunk. If the process is interrupted, the next run resumes from the last completed checkpoint instead of starting over. Combined with duplicate handling, this means an interrupted large import is a resume rather than a reconciliation exercise.

## Benchmarks

In a local test across 35 files of up to 2 GB:

| | Harbour | Old importer |
|---|---|---|
| Median import time | 4.8 s | 6.2 s |
| Peak memory | 72 MB | 1.1 GB |

The memory figure is the interesting one. The time improvement is real but modest; the drop from 1.1 GB to 72 MB is what changes the operational picture, because it decouples memory use from file size.

Read these numbers with their caveats. They come from a single Linux machine with a local SSD. Network storage or different row lengths may behave differently, and the test did not measure what happens when multiple import jobs run at the same time. If you run concurrent imports, you should measure that yourself.

## Limitations

Small files may actually be slower than under the old importer. Starting 4 workers and opening the checkpoint store both add fixed overhead, and on a small file that overhead is not amortised by anything. We do not have small-file timings to quantify this, so if your workload is mostly small files, benchmark before switching.

The supported encoding is UTF-8. Embedded newlines in quoted fields are handled correctly, which covers the usual source of mangled CSV. Files in other encodings must be converted before import — Harbour will not do the conversion for you.

Harbour is a command-line tool and nothing more. There is no web interface, no schema editor, and no remote scheduling service. It is intended to be driven by whatever you already use to run jobs.

## Rollout advice

Start with a dry run against a copy of representative data:

```
harbour import orders.csv --dry-run
```

Then work through the error report. Rows that fail here are rows the old importer was handling somehow, and you want to understand how before you change behaviour in production. Compare the set of accepted records against what the old importer produces on the same input — if the counts differ, find out why.

Verify duplicate handling explicitly before enabling production writes. Run an import, interrupt it, resume it, and confirm the ledger contains what you expect. The guarantee is straightforward, but it is cheap to check and expensive to assume.

Once dry runs are clean and duplicate handling is confirmed on your data, enable production writes.