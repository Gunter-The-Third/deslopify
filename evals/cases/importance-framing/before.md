# Import measurements

The key insight is this: peak memory fell from 1.1 GB to 72 MB. This is a vital improvement — the memory figure is the interesting one, and it changes the operational picture.

It is worth noting that small files may potentially be slower because worker startup adds overhead. This limitation is crucial — it is cheap to check and expensive to assume.

Only enable production writes once dry runs are clean and duplicate handling is confirmed.
