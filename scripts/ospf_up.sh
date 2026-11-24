#!/usr/bin/env bash
# Build the testbed with OSPFv3 (FRRouting, one instance per router namespace) instead of the
# static routes towards the host prefixes. Run as root. HELLO/DEAD (seconds) set the timers.
set -euo pipefail
umask 022
HERE="$(cd "$(dirname "$0")" && pwd)"
HELLO="${HELLO:-1}"
DEAD="${DEAD:-3}"
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }

"$HERE/setup.sh" >/dev/null

# OSPF must learn the host prefixes: remove the static routes setup.sh installed for them
ip -n r1 -6 route del 2001:db8:a5::/64
for n in r2 r3 r4; do
  ip -n "$n" -6 route del 2001:db8:a5::/64
  ip -n "$n" -6 route del 2001:db8:a1::/64
done
ip -n r5 -6 route del 2001:db8:a1::/64

declare -A LINKS=( [r1]="to2 to3 toh1" [r2]="to1 to5" [r3]="to1 to4" [r4]="to3 to5" [r5]="to2 to4 toh2" )
declare -A RID=( [r1]=1.1.1.1 [r2]=2.2.2.2 [r3]=3.3.3.3 [r4]=4.4.4.4 [r5]=5.5.5.5 )

mkdir -p /var/log/frr
for n in r1 r2 r3 r4 r5; do
  mkdir -p "/etc/frr/$n" "/var/run/frr/$n"
  chmod 777 "/var/run/frr/$n" /var/log/frr
  echo "hostname $n-zebra" > "/etc/frr/$n/zebra.conf"
  {
    echo "hostname $n-ospf6d"
    echo "log file /var/log/frr/$n-ospf6d.log"
    echo "router ospf6"
    echo " ospf6 router-id ${RID[$n]}"
    echo "exit"
    for i in ${LINKS[$n]}; do
      echo "interface $i"
      echo " ipv6 ospf6 area 0.0.0.0"
      if [[ $i == toh* ]]; then
        echo " ipv6 ospf6 passive"
      else
        echo " ipv6 ospf6 network point-to-point"
        echo " ipv6 ospf6 hello-interval $HELLO"
        echo " ipv6 ospf6 dead-interval $DEAD"
      fi
      echo "exit"
    done
  } > "/etc/frr/$n/ospf6d.conf"
  ip netns exec "$n" /usr/lib/frr/zebra  -d -N "$n" -u root -g root -f "/etc/frr/$n/zebra.conf"
  ip netns exec "$n" /usr/lib/frr/ospf6d -d -N "$n" -u root -g root -f "/etc/frr/$n/ospf6d.conf"
done

sleep 1
for n in r1 r2 r3 r4 r5; do
  vtysh -N "$n" -f "/etc/frr/$n/ospf6d.conf" 2>&1 | grep -v -E "vtysh.conf|MPLS" || true
done
echo "waiting for OSPF adjacencies (hello ${HELLO}s, dead ${DEAD}s)..."
full=0
for t in $(seq 1 60); do
  full=0
  for n in r1 r2 r3 r4 r5; do
    c=$(vtysh -N "$n" -c "show ipv6 ospf6 neighbor" 2>/dev/null | grep -c Full || true)
    full=$((full + c))
  done
  [ "$full" -ge 10 ] && break
  sleep 1
done
echo "Full adjacencies: $full (expected 10)"

for t in $(seq 1 30); do
  ip -n r1 -6 route show 2001:db8:a5::/64 | grep -q . && break
  sleep 1
done
echo "--- r1 neighbours";  vtysh -N r1 -c "show ipv6 ospf6 neighbor"
echo "--- r1 route to h2's prefix (learned by OSPF)"
ip -n r1 -6 route show 2001:db8:a5::/64
echo "--- ping h1 -> h2"
ip netns exec h1 ping -6 -c 3 -W 2 2001:db8:a5::2 | tail -3
