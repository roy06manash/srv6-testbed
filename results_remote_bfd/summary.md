# Results summary

## Mode `remote_loose` (9 valid runs of 9)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 149.33 | 156.00 | 20.21 | 118.00 | 172.00 | 172.00 |
| Loss (%) | 9 | 1.49 | 1.56 | 0.20 | 1.18 | 1.72 | 1.72 |
| Interruption (ms) | 9 | 149.27 | 155.24 | 20.18 | 118.02 | 172.03 | 172.03 |
| Failure -> traffic restored (ms) | 9 | 149.66 | 155.96 | 20.18 | 118.16 | 172.35 | 172.35 |

## Mode `remote_off` (9 valid runs of 9)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 9 | 147.44 | 136.00 | 18.95 | 129.00 | 180.00 | 180.00 |
| Loss (%) | 9 | 1.47 | 1.36 | 0.19 | 1.29 | 1.80 | 1.80 |
| Interruption (ms) | 9 | 147.33 | 136.01 | 18.99 | 128.41 | 179.82 | 179.82 |
| Failure -> traffic restored (ms) | 9 | 147.48 | 136.68 | 18.89 | 129.08 | 179.77 | 179.77 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
