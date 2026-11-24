# Results summary

## Mode `ipv6` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 68.20 | 68.50 | 8.30 | 54.00 | 81.00 | 81.00 |
| Loss (%) | 10 | 1.14 | 1.14 | 0.14 | 0.90 | 1.35 | 1.35 |
| Interruption (ms) | 10 | 67.96 | 68.38 | 8.29 | 53.71 | 81.02 | 81.02 |
| Detection delay (ms) | 10 | 61.82 | 62.30 | 8.08 | 48.65 | 74.35 | 74.35 |
| Repair command (ms) | 10 | 6.59 | 6.34 | 0.99 | 5.39 | 8.86 | 8.86 |
| Failure -> traffic restored (ms) | 10 | 68.63 | 69.01 | 8.25 | 54.34 | 81.54 | 81.54 |

## Mode `srv6` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 69.20 | 72.00 | 10.10 | 51.00 | 82.00 | 82.00 |
| Loss (%) | 10 | 1.15 | 1.20 | 0.17 | 0.85 | 1.37 | 1.37 |
| Interruption (ms) | 10 | 69.01 | 72.04 | 10.10 | 51.03 | 81.00 | 81.00 |
| Detection delay (ms) | 10 | 62.85 | 65.26 | 9.76 | 45.53 | 76.45 | 76.45 |
| Repair command (ms) | 10 | 6.38 | 6.14 | 0.74 | 5.76 | 8.27 | 8.27 |
| Failure -> traffic restored (ms) | 10 | 69.44 | 72.01 | 10.02 | 51.51 | 82.43 | 82.43 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
