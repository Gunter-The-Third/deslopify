Write a 700–900 word technical blog post introducing Harbour, a fictional CSV
importer, to developers who maintain data ingestion jobs. Use your ordinary
writing style. Do not imitate or exaggerate AI-writing patterns. Return the
article as Markdown, without an enclosing code fence or commentary about
this task. Include an introduction, a practical example, the design choices,
benchmark results, limitations and rollout advice.

All project details and benchmark figures below are fictional inputs for a
writing demonstration. Use only these facts. Do not add features, results,
customer stories, claims of novelty or invented documentation links.

- Harbour imports order records from CSV files into an existing ledger.
- The old importer loaded the whole file into memory. Harbour reads chunks
  of 8,000 rows, using a streaming parser and 4 workers.
- It validates each record before writing it. Invalid records are written
  to an error file with their line number and column name. Valid records can
  still be imported when other records fail validation.
- A dry run validates the file and writes the error report without writing
  to the ledger. Use this exact command: `harbour import orders.csv --dry-run`.
- A normal import reuses the source record's `order_id`. The ledger ignores
  duplicate identifiers, which makes retrying an interrupted import safe
  against duplicate entries. It does not repair an incorrect source record.
- The tool records a checkpoint after each completed chunk. After an
  interruption, it resumes from the last completed checkpoint.
- In a local test on 35 files of up to 2 GB, median import time was 4.8 s,
  compared with 6.2 s for the old importer. Peak memory was 72 MB, compared
  with 1.1 GB for the old importer.
- These measurements came from one Linux machine with a local SSD. They may
  not generalise to network storage or different row lengths. The test did
  not measure behaviour with multiple import jobs running at the same time.
- Small files may be slower because starting workers and opening the
  checkpoint store add overhead. No small-file timings are available.
- The supported encoding is UTF-8. Embedded newlines in quoted fields are
  supported. Files in other encodings must be converted before import.
- Harbour is a command-line tool. It has no web interface, schema editor or
  remote scheduling service.
- Begin rollout with a dry run on a copy of representative data. Review the
  error report, compare accepted records with the old importer and verify
  duplicate handling before enabling production writes.
