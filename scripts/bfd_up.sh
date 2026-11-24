#!/usr/bin/env bash
# Add real BFD (FRR bfdd, 50 ms x 3) on the r1-r2 link, registered with OSPFv3. Run as root,
# with the overlay topology up (scripts/overlay_up.sh).
set -uo pipefail
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }
[ -x /usr/lib/frr/bfdd ] || { echo "/usr/lib/frr/bfdd not found: sudo apt-get install -y frr"; exit 1; }

for n in r1 r2; do
  pkill -f "bfdd -d -N $n" 2>/dev/null || true
  mkdir -p /var/run/frr/$n; chmod 777 /var/run/frr/$n
  ip netns exec $n /usr/lib/frr/bfdd -d -N $n -u root -g root || echo "WARN: bfdd failed to start in $n"
done
sleep 2
for pair in "r1 to2" "r2 to1"; do
  set -- $pair
  vtysh -N $1 -c "configure terminal" -c "bfd" -c "profile fast" -c "detect-multiplier 3" \
        -c "receive-interval 50" -c "transmit-interval 50" -c "exit" -c "exit" \
        -c "interface $2" -c "ipv6 ospf6 bfd profile fast" -c "end" 2>&1 | grep -v vtysh.conf
done
echo "--- waiting for the BFD session (max 15 s)"
for i in $(seq 1 30); do
  vtysh -N r1 -c "show bfd peers brief" 2>/dev/null | grep -q " up" && break
  sleep 0.5
done
for n in r1 r2; do
  echo "--- $n bfd peers"; vtysh -N $n -c "show bfd peers brief" 2>&1 | grep -v vtysh.conf
done
echo "--- r1 ospf neighbours"; vtysh -N r1 -c "show ipv6 ospf6 neighbor" 2>&1 | grep -v vtysh.conf
