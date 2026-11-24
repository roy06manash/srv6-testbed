# SID traversal verification

## Mode `ipv6`

| Capture point | Observed (outer DA, SL, #SIDs) | Packets | Mean frame B | Verdict |
|---|---|---|---|---|
| r1_toh1 | plain: 6000 | 6000 | 162.0 | PASS |
| r1_to2 | plain: 2265 | 2265 | 162.0 | PASS |
| r2_to5 | plain: 2265 | 2265 | 162.0 | PASS |
| r1_to3 | plain: 3595 | 3595 | 162.0 | PASS |
| r3_to4 | plain: 3595 | 3595 | 162.0 | PASS |
| r4_to5 | plain: 3595 | 3595 | 162.0 | PASS |
| r5_toh2 | plain: 5860 | 5860 | 162.0 | PASS |

## Mode `srv6`

| Capture point | Observed (outer DA, SL, #SIDs) | Packets | Mean frame B | Verdict |
|---|---|---|---|---|
| r1_toh1 | plain: 6000 | 6000 | 162.0 | PASS |
| r1_to2 | ('fc00:2::1', 1, 2): 2254 | 2254 | 242.0 | PASS |
| r2_to5 | ('fc00:5::d6', 0, 2): 2254 | 2254 | 242.0 | PASS |
| r1_to3 | ('fc00:3::1', 2, 3): 3606 | 3606 | 258.0 | PASS |
| r3_to4 | ('fc00:4::1', 1, 3): 3606 | 3606 | 258.0 | PASS |
| r4_to5 | ('fc00:5::d6', 0, 3): 3606 | 3606 | 258.0 | PASS |
| r5_toh2 | plain: 5860 | 5860 | 162.0 | PASS |

## Header overhead (measured vs RFC 8754 expectation)

| Link | Plain IPv6 frame B | SRv6 frame B | Measured overhead B | Expected B |
|---|---|---|---|---|
| r1_to2 (2 SIDs) | 162.0 | 242.0 | 80.0 | 80 |
| r1_to3 (3 SIDs) | 162.0 | 258.0 | 96.0 | 96 |

**Overall: PASS**
