# Topology and addressing

```
                 Path A (primary, 2 SIDs):  r1 -> r2 -> r5
  h1 ---- r1 ----------- r2 ----------- r5 ---- h2
           \                            /
            \--------- r3 ---- r4 -----/
                 Path B (backup, 3 SIDs): r1 -> r3 -> r4 -> r5

  Failure injected on the r1-r2 link (silent: netem 100 % loss, link stays "up").
  Measured flow: h1 -> h2, UDP, 1000 packets/s, one direction.
```

All nodes are Linux network namespaces on one Ubuntu 24.04 VM (kernel 6.8), connected by veth pairs.

## Links

| Link | Subnet | Left | Right |
|---|---|---|---|
| h1 - r1 | 2001:db8:a1::/64 | h1 `hif` ::2 | r1 `toh1` ::1 |
| r1 - r2 | 2001:db8:12::/64 | r1 `to2` ::1 | r2 `to1` ::2 |
| r2 - r5 | 2001:db8:25::/64 | r2 `to5` ::2 | r5 `to2` ::5 |
| r1 - r3 | 2001:db8:13::/64 | r1 `to3` ::1 | r3 `to1` ::3 |
| r3 - r4 | 2001:db8:34::/64 | r3 `to4` ::3 | r4 `to3` ::4 |
| r4 - r5 | 2001:db8:45::/64 | r4 `to5` ::4 | r5 `to4` ::5 |
| r5 - h2 | 2001:db8:a5::/64 | r5 `toh2` ::1 | h2 `hif` ::2 |

## SIDs (each router has a dummy interface `sid0` that carries them)

| Node | Locator | Behaviour | SID |
|---|---|---|---|
| r1..r5 | fc00:N::/32 | End | fc00:N::1 |
| r5 | fc00:5::/32 | End.DT6 (table main) | fc00:5::d6 |

Note: the SID routes are attached to a dummy interface, not `lo`. On this kernel a
seg6local route on `lo` was not matched for packets arriving from another interface
(the End action's packet counter stayed at 0); on a dummy device it works.

## Routing

- Plain IPv6: r2, r3 and r4 each have a route to 2001:db8:a5::/64 towards r5. r5 routes
  2001:db8:a1::/64 back via r2, and r2, r3 and r4 have routes back towards h1 (r3 and r4 only so
  that traceroute replies can return).
- SRv6: each router can reach the locator of its next SID neighbour (r1: fc00:2::/32 and
  fc00:3::/32; r2: fc00:5::/32; r3: fc00:4::/32; r4: fc00:5::/32).

## Policies at r1 for 2001:db8:a5::/64 (`scripts/set_policy.sh`)

| Policy | Action | Segment list |
|---|---|---|
| ipv6-primary | plain route via r2 | - |
| ipv6-backup | plain route via r3 | - |
| srv6-primary | H.Encaps | fc00:2::1, fc00:5::d6 |
| srv6-backup | H.Encaps | fc00:3::1, fc00:4::1, fc00:5::d6 |

Both modes use the same topology, SIDs, failure detector and failure. Only the route at r1
differs, so differences come from the forwarding/steering mechanism alone.

## Header overhead (RFC 8754)

Outer IPv6 header (40 B) + SRH (8 B fixed + 16 B per SID):

- Path A, 2 SIDs: 40 + 8 + 32 = **80 B** (measured: 80 B)
- Path B, 3 SIDs: 40 + 8 + 48 = **96 B** (measured: 96 B)
- Plain IPv6: 0 B

## Failure detection and repair

A BFD-like UDP prober on r1 probes r2 every 50 ms; 3 intervals without a reply (measured from the
last reply) declare the link down (expected detection 100-150 ms plus jitter). The detector then
runs `set_policy.sh <mode>-backup`. This is not real BFD.
