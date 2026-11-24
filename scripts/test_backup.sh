#!/usr/bin/env bash
# Switch r1 to the SRv6 backup policy, then show the route, the ping and a capture on r3-r4.
D="$(cd "$(dirname "$0")" && pwd)"
ip netns exec r1 "$D/set_policy.sh" srv6-backup || exit 1
echo "--- r1 route"
ip netns exec r1 ip -6 route show 2001:db8:a5::/64
echo "--- capture on r3 (to4) while pinging"
( ip netns exec r3 timeout 8 tcpdump -nn -c 2 -i to4 ip6 2>/dev/null ) &
sleep 1
ip netns exec h1 ping -6 -c3 -W3 2001:db8:a5::2 | tail -3
wait
ip netns exec r1 "$D/set_policy.sh" srv6-primary
echo "(policy restored to srv6-primary)"
