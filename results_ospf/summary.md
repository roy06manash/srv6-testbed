# Results summary

## Mode `ospf` (10 valid runs of 10)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 10 | 2331.70 | 2288.00 | 223.35 | 2064.00 | 2737.00 | 2737.00 |
| Loss (%) | 10 | 23.32 | 22.88 | 2.23 | 20.64 | 27.37 | 27.37 |
| Interruption (ms) | 10 | 2331.64 | 2288.03 | 223.22 | 2063.91 | 2736.25 | 2736.25 |
| Failure -> traffic restored (ms) | 10 | 2331.94 | 2288.37 | 223.33 | 2063.86 | 2737.06 | 2737.06 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
