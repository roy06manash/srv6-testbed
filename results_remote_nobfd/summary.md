# Results summary

## Mode `remote_loose` (9 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 2417.56 | 2191.00 | 322.15 | 2122.00 | 3012.00 | 3012.00 |
| Loss (%) | 9 | 24.18 | 21.91 | 3.22 | 21.22 | 30.12 | 30.12 |
| Interruption (ms) | 9 | 2417.43 | 2191.03 | 322.31 | 2121.86 | 3012.14 | 3012.14 |
| Failure -> traffic restored (ms) | 9 | 2417.75 | 2191.76 | 321.96 | 2122.35 | 3012.11 | 3012.11 |

## Mode `remote_off` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 3171.10 | 2372.00 | 2399.14 | 2084.00 | 9947.00 | 9947.00 |
| Loss (%) | 10 | 31.71 | 23.72 | 23.99 | 20.84 | 99.47 | 99.47 |
| Interruption (ms) | 10 | 2176.34 | 2227.51 | 819.85 | 0.56 | 2959.03 | 2959.03 |
| Failure -> traffic restored (ms) | 10 | 2949.91 | 2372.60 | 1705.86 | 2083.95 | 7731.17 | 7731.17 |

## Excluded runs

- remote_loose_009: largest gap precedes failure

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
