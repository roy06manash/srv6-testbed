# Results summary

## Mode `overlay_off` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 11.60 | 11.50 | 0.70 | 11.00 | 13.00 | 13.00 |
| Loss (%) | 10 | 0.12 | 0.11 | 0.01 | 0.11 | 0.13 | 0.13 |
| Interruption (ms) | 10 | 44.05 | 11.20 | 71.05 | 10.53 | 211.17 | 211.17 |
| Failure -> traffic restored (ms) | 10 | 1400.41 | 11.19 | 2933.43 | 9.34 | 7282.89 | 7282.89 |

## Mode `overlay_pinned` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 12.80 | 13.00 | 0.92 | 12.00 | 15.00 | 15.00 |
| Loss (%) | 10 | 0.13 | 0.13 | 0.01 | 0.12 | 0.15 | 0.15 |
| Interruption (ms) | 10 | 14.02 | 12.70 | 4.89 | 11.85 | 27.88 | 27.88 |
| Failure -> traffic restored (ms) | 10 | 496.95 | 12.32 | 1533.51 | 10.37 | 4861.39 | 4861.39 |

## Mode `overlay_protected` (4 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 4 | 0.25 | 0.00 | 0.50 | 0.00 | 1.00 | 1.00 |
| Loss (%) | 4 | 0.00 | 0.00 | 0.01 | 0.00 | 0.01 | 0.01 |
| Interruption (ms) | 4 | 0.35 | 0.00 | 0.70 | 0.00 | 1.40 | 1.40 |
| Failure -> traffic restored (ms) | 4 | 2465.92 | 3046.37 | 1671.39 | 10.77 | 3760.16 | 3760.16 |

## Excluded runs

- overlay_protected_001: largest gap precedes failure
- overlay_protected_002: largest gap precedes failure
- overlay_protected_004: largest gap precedes failure
- overlay_protected_006: largest gap precedes failure
- overlay_protected_007: largest gap precedes failure
- overlay_protected_009: largest gap precedes failure

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
