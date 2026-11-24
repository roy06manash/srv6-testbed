#!/usr/bin/env bash
# mtr path view for plain IPv6 and the SRv6 policies (overlay topology up). Run as root.
HERE="$(cd "$(dirname "$0")" && pwd)"
for p in off pinned-primary pinned-backup; do
  ip netns exec r1 "$HERE/set_overlay.sh" "$p"
  echo "=============== policy: $p"
  ip netns exec h1 mtr -6 -n -r -c 8 -i 0.3 2001:db8:a5::2
done
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
