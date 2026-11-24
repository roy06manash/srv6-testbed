# Results summary

## Mode `ipv6` (20 valid runs of 20)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 20 | 147.50 | 147.50 | 9.80 | 132.00 | 162.00 | 169.00 |
| Loss (%) | 20 | 2.46 | 2.46 | 0.16 | 2.20 | 2.70 | 2.82 |
| Interruption (ms) | 20 | 147.38 | 147.02 | 9.86 | 132.03 | 162.04 | 169.03 |
| Detection delay (ms) | 20 | 140.81 | 141.06 | 8.92 | 126.45 | 154.55 | 160.57 |
| Repair command (ms) | 20 | 6.80 | 6.32 | 1.30 | 5.78 | 8.39 | 11.36 |
| Failure -> traffic restored (ms) | 20 | 147.76 | 147.50 | 9.71 | 132.73 | 162.30 | 168.91 |

## Mode `srv6` (20 valid runs of 20)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 20 | 141.95 | 141.00 | 7.28 | 131.00 | 155.00 | 157.00 |
| Loss (%) | 20 | 2.37 | 2.35 | 0.12 | 2.18 | 2.58 | 2.62 |
| Interruption (ms) | 20 | 141.83 | 141.09 | 7.19 | 131.03 | 155.02 | 156.20 |
| Detection delay (ms) | 20 | 135.79 | 134.54 | 7.18 | 125.44 | 149.43 | 149.83 |
| Repair command (ms) | 20 | 6.34 | 6.23 | 0.49 | 5.76 | 7.05 | 7.72 |
| Failure -> traffic restored (ms) | 20 | 142.33 | 141.67 | 7.20 | 131.57 | 155.58 | 157.01 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
