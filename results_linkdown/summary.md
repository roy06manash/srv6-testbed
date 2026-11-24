# Results summary

## Mode `overlay_loose` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 12.00 | 12.00 | 0.94 | 11.00 | 14.00 | 14.00 |
| Loss (%) | 10 | 0.12 | 0.12 | 0.01 | 0.11 | 0.14 | 0.14 |
| Interruption (ms) | 10 | 11.66 | 11.47 | 1.16 | 10.35 | 14.00 | 14.00 |
| Failure -> traffic restored (ms) | 10 | 11.19 | 10.98 | 1.19 | 9.26 | 13.09 | 13.09 |

## Mode `overlay_off` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 11.40 | 11.00 | 0.52 | 11.00 | 12.00 | 12.00 |
| Loss (%) | 10 | 0.11 | 0.11 | 0.01 | 0.11 | 0.12 | 0.12 |
| Interruption (ms) | 10 | 13.48 | 11.07 | 7.83 | 9.71 | 35.63 | 35.63 |
| Failure -> traffic restored (ms) | 10 | 291.12 | 11.09 | 886.10 | 10.17 | 2813.01 | 2813.01 |

## Mode `overlay_pinned` (9 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 12.67 | 12.00 | 0.87 | 12.00 | 14.00 | 14.00 |
| Loss (%) | 9 | 0.13 | 0.12 | 0.01 | 0.12 | 0.14 | 0.14 |
| Interruption (ms) | 9 | 19.78 | 12.30 | 12.66 | 11.27 | 45.67 | 45.67 |
| Failure -> traffic restored (ms) | 9 | 1167.37 | 12.09 | 2190.80 | 11.18 | 5398.47 | 5398.47 |

## Mode `overlay_pinned_fast` (9 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 12.67 | 12.00 | 1.12 | 12.00 | 15.00 | 15.00 |
| Loss (%) | 9 | 0.13 | 0.12 | 0.01 | 0.12 | 0.15 | 0.15 |
| Interruption (ms) | 9 | 12.69 | 11.83 | 2.09 | 11.02 | 17.81 | 17.81 |
| Detection delay (ms) | 9 | 126.87 | 126.72 | 1.60 | 124.82 | 129.83 | 129.83 |
| Repair command (ms) | 9 | 6.87 | 6.75 | 0.57 | 6.43 | 8.30 | 8.30 |
| Failure -> traffic restored (ms) | 9 | 488.26 | 12.08 | 1429.03 | 10.70 | 4298.99 | 4298.99 |

## Excluded runs

- overlay_pinned_006: largest gap precedes failure
- overlay_pinned_fast_009: largest gap precedes failure

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
