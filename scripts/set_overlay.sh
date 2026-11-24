#!/usr/bin/env bash
# SRv6 overlay policy on top of the OSPFv3 underlay. Run INSIDE r1's namespace:
#   ip netns exec r1 scripts/set_overlay.sh <loose|pinned-primary|pinned-backup|protected|off>
# protected = primary (metric 10) and backup (metric 20) installed together; with
# ignore_routes_with_linkdown the kernel skips the dead primary on carrier loss (local repair).
set -euo pipefail
DST=2001:db8:a5::/65
clean() {
  ip -6 route del "$DST" metric 10 2>/dev/null || true
  ip -6 route del "$DST" metric 20 2>/dev/null || true
}
case "${1:-}" in
  loose)          clean; sysctl -qw net.ipv6.conf.to2.ignore_routes_with_linkdown=0
                  ip -6 route replace "$DST" encap seg6 mode encap segs fc00:5::d6 dev to2 ;;
  pinned-primary) clean; sysctl -qw net.ipv6.conf.to2.ignore_routes_with_linkdown=0
                  ip -6 route replace "$DST" encap seg6 mode encap segs fc00:2::1,fc00:5::d6 dev to2 ;;
  pinned-backup)  clean; sysctl -qw net.ipv6.conf.to2.ignore_routes_with_linkdown=0
                  ip -6 route replace "$DST" encap seg6 mode encap segs fc00:3::1,fc00:4::1,fc00:5::d6 dev to3 ;;
  protected)      ip -6 route del "$DST" metric 1024 2>/dev/null || true
                  sysctl -qw net.ipv6.conf.to2.ignore_routes_with_linkdown=1
                  ip -6 route replace "$DST" encap seg6 mode encap segs fc00:2::1,fc00:5::d6 dev to2 metric 10
                  ip -6 route replace "$DST" encap seg6 mode encap segs fc00:3::1,fc00:4::1,fc00:5::d6 dev to3 metric 20 ;;
  off)            clean; sysctl -qw net.ipv6.conf.to2.ignore_routes_with_linkdown=0
                  ip -6 route del "$DST" metric 1024 2>/dev/null || true ;;
  *) echo "usage: $0 <loose|pinned-primary|pinned-backup|protected|off>" >&2; exit 2 ;;
esac
