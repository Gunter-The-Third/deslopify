# tidyjson

## 🚀 Overview

tidyjson isn't just another JSON formatter — it's a complete toolkit for taming messy data. In today's fast-paced development world, developers need tools that are fast, reliable, and easy to use. That's where tidyjson comes in.

## ✨ Key Features

- **Blazing Fast:** tidyjson leverages a streaming parser to process files of up to 2 GB without loading them into memory.
- **Robust Error Handling:** Malformed input doesn't crash the tool; instead, tidyjson reports the line and column of the first error.
- **Seamless Integration:** It serves as a drop-in replacement for `python -m json.tool`.

## Why tidyjson?

Here's the thing: most formatters choke on large files. The result? Wasted time. tidyjson takes a fundamentally different approach — it streams rather than buffers, so memory use stays flat at around 40 MB regardless of input size.

It's worth noting that tidyjson may potentially be slower than jq on very small files. Ultimately, though, the trade-off is well worth it.

## Getting Started

Install it with pip:

```bash
pip install tidyjson
```

Then simply run `tidyjson input.json`. That's it!

## Conclusion

In summary, tidyjson is a powerful, flexible, and developer-friendly tool that empowers you to work with JSON data more effectively. Give it a try today!
