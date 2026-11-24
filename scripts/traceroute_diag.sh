#!/usr/bin/env bash
# Why do SRv6 transit hops not show in traceroute? Run as root with the overlay topology up.
HERE="$(cd "$(dirname "$0")" && pwd)"
for p in off pinned-primary pinned-backup; do
  ip netns exec r1 "$HERE/set_overlay.sh" "$p"
  echo "=============== policy: $p"
  ip netns exec h1 timeout 20 tcpdump -n -l -i eth0 'icmp6 and ip6[40] == 3' > /tmp/tr_$p.txt 2>/dev/null &
  sleep 1
  ip netns exec h1 traceroute -6 -n -q 2 -w 1 -m 6 2001:db8:a5::2
  sleep 1; pkill -f "tcpdump -n -l -i eth0" ; sleep 0.5
  echo "--- sources of ICMPv6 time-exceeded seen at h1:"
  grep -i "time exceeded" /tmp/tr_$p.txt | awk '{print $2}' | sort | uniq -c
done
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
