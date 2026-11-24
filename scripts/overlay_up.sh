#!/usr/bin/env bash
# Topology + OSPFv3 underlay + SRv6 locators advertised by OSPF. Run as root.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }

"$HERE/ospf_up.sh" || { echo "ospf_up.sh failed"; exit 1; }

echo "--- moving SID reachability from static routes to OSPF"
del() { ip -n "$1" -6 route del "$2" via "$3" dev "$4" 2>/dev/null || true; }
del r1 fc00:2::/32 2001:db8:12::2 to2
del r1 fc00:3::/32 2001:db8:13::3 to3
del r2 fc00:5::/32 2001:db8:25::5 to5
del r3 fc00:4::/32 2001:db8:34::4 to4
del r4 fc00:5::/32 2001:db8:45::5 to5

for n in 1 2 3 4 5; do
  ip -n "r$n" addr add "fc00:$n::ffff/32" dev sid0 nodad 2>/dev/null || true
  vtysh -N "r$n" -c "configure terminal" -c "interface sid0" \
        -c "ipv6 ospf6 area 0.0.0.0" -c "exit" -c "end" || echo "WARN: r$n vtysh failed"
  vtysh -N "r$n" -c "configure terminal" -c "interface sid0" \
        -c "ipv6 ospf6 passive" -c "exit" -c "end" >/dev/null 2>&1 || true
done

echo "--- waiting for OSPF to learn every locator at r1 (max 40 s)"
for i in $(seq 1 80); do
  ok=1
  for n in 2 3 4 5; do
    ip -n r1 -6 route show "fc00:$n::/32" | grep -q "proto" || ok=0
  done
  [ $ok -eq 1 ] && break
  sleep 0.5
done
ip -n r1 -6 route show | grep fc00
[ $ok -eq 1 ] && echo "locators learned via OSPF: OK" || { echo "FAILED: locators not learned"; exit 1; }
ip netns exec r1 "$HERE/set_overlay.sh" pinned-primary
echo "--- overlay ping"
ip netns exec h1 ping -6 -c3 -W2 2001:db8:a5::2 | tail -3
