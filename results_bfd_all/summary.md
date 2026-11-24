# Results summary

## Mode `overlay_loose` (9 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 143.33 | 137.00 | 15.36 | 130.00 | 180.00 | 180.00 |
| Loss (%) | 9 | 1.43 | 1.37 | 0.15 | 1.30 | 1.80 | 1.80 |
| Interruption (ms) | 9 | 143.26 | 137.02 | 15.39 | 130.03 | 180.03 | 180.03 |
| Failure -> traffic restored (ms) | 9 | 143.56 | 137.40 | 15.26 | 130.33 | 180.09 | 180.09 |

## Mode `overlay_off` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 151.60 | 153.50 | 13.53 | 132.00 | 175.00 | 175.00 |
| Loss (%) | 10 | 1.52 | 1.54 | 0.14 | 1.32 | 1.75 | 1.75 |
| Interruption (ms) | 10 | 151.45 | 152.95 | 13.59 | 132.02 | 175.02 | 175.02 |
| Failure -> traffic restored (ms) | 10 | 151.77 | 153.53 | 13.43 | 132.20 | 174.98 | 174.98 |

## Mode `overlay_pinned` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 145.50 | 143.50 | 19.57 | 124.00 | 185.00 | 185.00 |
| Loss (%) | 10 | 1.46 | 1.44 | 0.20 | 1.24 | 1.85 | 1.85 |
| Interruption (ms) | 10 | 145.42 | 143.55 | 19.56 | 124.03 | 184.57 | 184.57 |
| Failure -> traffic restored (ms) | 10 | 145.59 | 143.77 | 19.76 | 124.23 | 185.42 | 185.42 |

## Mode `overlay_pinned_fast` (9 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 140.44 | 140.00 | 10.78 | 124.00 | 163.00 | 163.00 |
| Loss (%) | 9 | 1.40 | 1.40 | 0.11 | 1.24 | 1.63 | 1.63 |
| Interruption (ms) | 9 | 140.28 | 139.20 | 10.83 | 124.03 | 163.03 | 163.03 |
| Detection delay (ms) | 9 | 133.81 | 133.93 | 11.61 | 110.05 | 149.11 | 149.11 |
| Repair command (ms) | 9 | 13.55 | 12.86 | 3.02 | 9.74 | 20.29 | 20.29 |
| Failure -> traffic restored (ms) | 9 | 140.58 | 139.91 | 10.75 | 124.16 | 163.38 | 163.38 |

## Excluded runs

- overlay_loose_000: too few packets received
- overlay_pinned_fast_002: detected before failure (false positive)

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
