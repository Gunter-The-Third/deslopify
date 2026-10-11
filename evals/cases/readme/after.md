# tidyjson

tidyjson formats JSON. It streams its input instead of loading it into memory, so it handles files of up to 2 GB and uses about 40 MB of memory whatever the file size.

## Features

- Reports the line and column of the first error in malformed input instead of crashing.
- Works as a drop-in replacement for `python -m json.tool`.

## Limitations

tidyjson may be slower than jq on very small files.

## Install

```bash
pip install tidyjson
```

Then run `tidyjson input.json`.
