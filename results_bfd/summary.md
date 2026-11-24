# Results summary

## Mode `overlay_loose` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 153.40 | 148.00 | 23.09 | 126.00 | 199.00 | 199.00 |
| Loss (%) | 10 | 1.53 | 1.48 | 0.23 | 1.26 | 1.99 | 1.99 |
| Interruption (ms) | 10 | 153.29 | 147.47 | 23.13 | 126.00 | 199.03 | 199.03 |
| Failure -> traffic restored (ms) | 10 | 153.72 | 148.39 | 23.27 | 125.59 | 199.70 | 199.70 |

## Mode `overlay_off` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 145.40 | 141.50 | 16.35 | 125.00 | 167.00 | 167.00 |
| Loss (%) | 10 | 1.45 | 1.42 | 0.16 | 1.25 | 1.67 | 1.67 |
| Interruption (ms) | 10 | 145.24 | 141.51 | 16.44 | 125.02 | 167.01 | 167.01 |
| Failure -> traffic restored (ms) | 10 | 145.68 | 141.77 | 16.44 | 125.36 | 167.32 | 167.32 |

## Mode `overlay_pinned` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 152.10 | 153.50 | 12.40 | 133.00 | 177.00 | 177.00 |
| Loss (%) | 10 | 1.52 | 1.54 | 0.12 | 1.33 | 1.77 | 1.77 |
| Interruption (ms) | 10 | 151.93 | 153.38 | 12.63 | 132.30 | 177.02 | 177.02 |
| Failure -> traffic restored (ms) | 10 | 152.46 | 154.17 | 12.38 | 133.35 | 177.01 | 177.01 |

## Mode `overlay_pinned_fast` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 139.40 | 136.00 | 14.63 | 111.00 | 158.00 | 158.00 |
| Loss (%) | 10 | 1.39 | 1.36 | 0.15 | 1.11 | 1.58 | 1.58 |
| Interruption (ms) | 10 | 139.15 | 135.15 | 14.64 | 111.03 | 158.05 | 158.05 |
| Detection delay (ms) | 10 | 135.42 | 134.96 | 15.23 | 101.06 | 153.65 | 153.65 |
| Repair command (ms) | 10 | 7.89 | 7.50 | 1.29 | 6.64 | 10.43 | 10.43 |
| Failure -> traffic restored (ms) | 10 | 139.64 | 136.09 | 14.68 | 111.31 | 158.63 | 158.63 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
