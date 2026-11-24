# Results summary

## Mode `overlay_loose` (5 valid runs of 5)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 5 | 34079.80 | 34017.00 | 178.48 | 33900.00 | 34313.00 | 34313.00 |
| Loss (%) | 5 | 61.96 | 61.85 | 0.32 | 61.64 | 62.39 | 62.39 |
| Interruption (ms) | 5 | 34079.93 | 34017.19 | 178.44 | 33900.06 | 34312.93 | 34312.93 |
| Failure -> traffic restored (ms) | 5 | 34079.93 | 34016.92 | 178.22 | 33900.33 | 34312.78 | 34312.78 |

## Mode `overlay_off` (5 valid runs of 5)

| Metric | n | mean | median | stdev | min | p95 | max |
|---|---|---|---|---|---|---|---|
| Lost packets | 5 | 34118.80 | 34083.00 | 291.95 | 33741.00 | 34530.00 | 34530.00 |
| Loss (%) | 5 | 62.03 | 61.97 | 0.53 | 61.35 | 62.78 | 62.78 |
| Interruption (ms) | 5 | 34118.90 | 34083.29 | 291.89 | 33741.19 | 34530.04 | 34530.04 |
| Failure -> traffic restored (ms) | 5 | 34118.90 | 34083.06 | 292.10 | 33740.64 | 34529.99 | 34529.99 |

## Header overhead (RFC 8754, theoretical)

| Path | SIDs | Outer IPv6 | SRH | Total overhead |
|---|---|---|---|---|
| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |
| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |

Measured overhead comes from `verify_sids.py` (see sid_traversal.md).
