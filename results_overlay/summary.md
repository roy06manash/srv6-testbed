# Results summary

## Mode `overlay_loose` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 2629.70 | 2658.50 | 281.01 | 2046.00 | 3008.00 | 3008.00 |
| Loss (%) | 10 | 26.30 | 26.59 | 2.81 | 20.46 | 30.08 | 30.08 |
| Interruption (ms) | 10 | 2629.38 | 2658.09 | 281.05 | 2045.79 | 3007.51 | 3007.51 |
| Failure -> traffic restored (ms) | 10 | 2630.18 | 2659.19 | 280.92 | 2046.77 | 3008.56 | 3008.56 |

## Mode `overlay_pinned` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 2505.20 | 2527.00 | 272.16 | 2158.00 | 2885.00 | 2885.00 |
| Loss (%) | 10 | 25.05 | 25.27 | 2.72 | 21.58 | 28.85 | 28.85 |
| Interruption (ms) | 10 | 2505.04 | 2527.02 | 272.28 | 2157.87 | 2885.02 | 2885.02 |
| Failure -> traffic restored (ms) | 10 | 2505.58 | 2527.49 | 272.17 | 2158.32 | 2885.73 | 2885.73 |

## Mode `overlay_pinned_fast` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 147.30 | 151.50 | 8.42 | 133.00 | 156.00 | 156.00 |
| Loss (%) | 10 | 1.47 | 1.52 | 0.08 | 1.33 | 1.56 | 1.56 |
| Interruption (ms) | 10 | 146.86 | 151.35 | 8.63 | 132.41 | 155.77 | 155.77 |
| Detection delay (ms) | 10 | 141.43 | 145.87 | 8.72 | 126.28 | 150.79 | 150.79 |
| Repair command (ms) | 10 | 5.84 | 5.85 | 0.23 | 5.40 | 6.11 | 6.11 |
| Failure -> traffic restored (ms) | 10 | 147.63 | 152.11 | 8.60 | 132.94 | 156.56 | 156.56 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
