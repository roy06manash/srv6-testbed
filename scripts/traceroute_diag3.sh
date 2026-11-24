#!/usr/bin/env bash
# Follow one SRv6 traceroute probe (hop limit 2, then 3) and print hop limits on each link.
HERE="$(cd "$(dirname "$0")" && pwd)"
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
for ttl in 2 3; do
  echo "################ probe with hop limit $ttl"
  rm -f /tmp/d3_*.txt
  for pt in "r1 toh1" "r1 to2" "r2 to5" "r5 toh2"; do
    set -- $pt
    ip netns exec $1 timeout 6 tcpdump -n -l -v -i $2 'ip6 and (udp or ip6[6]==43 or icmp6)' > /tmp/d3_$1_$2.txt 2>/dev/null &
  done
  sleep 1.5
  ip netns exec h1 traceroute -6 -n -f $ttl -m $ttl -q 1 -w 1 2001:db8:a5::2 | tail -1
  sleep 1; pkill tcpdump; sleep 0.5
  for f in /tmp/d3_r1_toh1 /tmp/d3_r1_to2 /tmp/d3_r2_to5 /tmp/d3_r5_toh2; do
    echo "--- $(basename $f | sed 's/d3_//'):"
    grep -E "hlim|IP6" ${f}.txt | tr -s ' ' | grep -E "hlim" | sed 's/, flowlabel[^,]*//' | cut -c1-110 | head -4
  done
done
