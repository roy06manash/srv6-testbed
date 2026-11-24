#!/usr/bin/env bash
# Path-steering demo (no failure): traceroute, per-link counters, and a
# "transit routers have no route to the destination" test.
D="$(cd "$(dirname "$0")" && pwd)"
P="$D/set_policy.sh"
DST=2001:db8:a5::2
POLICIES="ipv6-primary ipv6-backup srv6-primary srv6-backup"
rx() { ip netns exec "$1" cat "/sys/class/net/$2/statistics/rx_packets"; }

set_pol() {
  ip netns exec r1 "$P" "$1"
  ip netns exec h1 ping -6 -c 3 -W 1 -q $DST >/dev/null 2>&1   # warm up neighbours
}

count() {   # $1 = policy; sends 100 pings and shows how many packets each transit router received
  set_pol "$1"
  local a2 a3 a4 recv
  a2=$(rx r2 to1); a3=$(rx r3 to1); a4=$(rx r4 to3)
  recv=$(ip netns exec h1 ping -6 -c 100 -i 0.01 -W 1 -q $DST 2>&1 | awk '/transmitted/ {print $4}')
  printf "%-13s delivered %3s/100   packets seen: r2=%-4s r3=%-4s r4=%-4s\n" "$1" "${recv:-0}" \
    $(( $(rx r2 to1) - a2 )) $(( $(rx r3 to1) - a3 )) $(( $(rx r4 to3) - a4 ))
}

echo "=== 1. traceroute h1 -> h2 under each policy (no failure)"
for pol in $POLICIES; do
  set_pol "$pol"
  echo "--- $pol"
  ip netns exec h1 traceroute -6 -n -q 1 -w 1 $DST
done

echo
echo "=== 2. which transit routers carried the traffic (100 pings each)"
for pol in $POLICIES; do count "$pol"; done

echo
echo "=== 3. r3 and r4 have NO route to h2's prefix (they only know SIDs/locators)"
trap 'ip -n r3 -6 route replace 2001:db8:a5::/64 via 2001:db8:34::4 dev to4
      ip -n r4 -6 route replace 2001:db8:a5::/64 via 2001:db8:45::5 dev to5
      ip netns exec r1 "$P" srv6-primary' EXIT
ip -n r3 -6 route del 2001:db8:a5::/64
ip -n r4 -6 route del 2001:db8:a5::/64
count ipv6-backup
count srv6-backup
echo
echo "(routes on r3/r4 and the srv6-primary policy are restored on exit)"
