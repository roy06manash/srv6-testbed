#!/usr/bin/env bash
# Scripted backup-policy switch. Run INSIDE r1's namespace:
#   ip netns exec r1 scripts/set_policy.sh <ipv6-primary|ipv6-backup|srv6-primary|srv6-backup>
#
# All four policies replace the same route (same prefix + metric), so a switch is one
# atomic `ip route replace`.
set -euo pipefail
DST=2001:db8:a5::/64
case "${1:-}" in
  ipv6-primary) ip -6 route replace "$DST" via 2001:db8:12::2 dev to2 metric 100 ;;
  ipv6-backup)  ip -6 route replace "$DST" via 2001:db8:13::3 dev to3 metric 100 ;;
  srv6-primary) ip -6 route replace "$DST" encap seg6 mode encap \
                  segs fc00:2::1,fc00:5::d6 dev to2 metric 100 ;;
  srv6-backup)  ip -6 route replace "$DST" encap seg6 mode encap \
                  segs fc00:3::1,fc00:4::1,fc00:5::d6 dev to3 metric 100 ;;
  *) echo "usage: $0 <ipv6|srv6>-<primary|backup>" >&2; exit 2 ;;
esac
