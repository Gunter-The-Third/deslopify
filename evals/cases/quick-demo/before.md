# tidyjson

tidyjson isn't just another JSON formatter — it leverages a streaming parser to handle files of up to 2 GB. The key insight is this: it uses around 40 MB of memory regardless of input size.

It's worth noting that tidyjson may potentially be slower than jq on very small files. Overall, this seamless approach is robust and flexible.
