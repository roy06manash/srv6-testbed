#!/usr/bin/env bash
# Where do ICMPv6 time-exceeded errors go during an SRv6 traceroute? Run as root.
HERE="$(cd "$(dirname "$0")" && pwd)"
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
rm -f /tmp/d2_*.txt
for pt in "r1 toh1" "r1 to2" "r1 to3" "r2 to1" "r2 to5" "r5 to2" "r5 toh2"; do
  set -- $pt
  ip netns exec $1 timeout 15 tcpdump -n -l -i $2 'icmp6 and ip6[40] == 3' > /tmp/d2_$1_$2.txt 2>/dev/null &
done
sleep 1.5
ip netns exec h1 traceroute -6 -n -q 1 -w 1 -m 5 2001:db8:a5::2
sleep 1; pkill tcpdump; sleep 0.5
for f in /tmp/d2_*.txt; do
  echo "--- $(basename $f .txt | sed 's/d2_//'):"
  grep -i "time exceeded" $f | awk '{print $2, $3, $4}' | sort | uniq -c
done
