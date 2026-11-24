#!/usr/bin/env bash
# Run after overlay_up.sh: each overlay policy must deliver traffic. Run as root.
HERE="$(cd "$(dirname "$0")" && pwd)"
for p in loose pinned-primary pinned-backup; do
  ip netns exec r1 "$HERE/set_overlay.sh" "$p"
  echo "== $p"
  ip -n r1 -6 route show 2001:db8:a5::/65
  ip netns exec h1 ping -6 -c5 -i 0.2 -W2 2001:db8:a5::2 | grep -E "transmitted|rtt"
done
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
