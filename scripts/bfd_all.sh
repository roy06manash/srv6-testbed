#!/usr/bin/env bash
# Real BFD (FRR bfdd, 50 ms x 3) on all five core links, registered with OSPFv3.
# Run as root with the overlay topology up (scripts/overlay_up.sh).
set -uo pipefail
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }
[ -x /usr/lib/frr/bfdd ] || { echo "bfdd missing: sudo apt-get install -y frr"; exit 1; }

# router : core interfaces
declare -A IFS_OF=( [r1]="to2 to3" [r2]="to1 to5" [r3]="to1 to4" [r4]="to3 to5" [r5]="to2 to4" )

for n in r1 r2 r3 r4 r5; do
  pkill -f "bfdd -d -N $n" 2>/dev/null || true
done
sleep 1
for n in r1 r2 r3 r4 r5; do
  mkdir -p /var/run/frr/$n; chmod 777 /var/run/frr/$n
  ip netns exec $n /usr/lib/frr/bfdd -d -N $n -u root -g root || echo "WARN: bfdd failed in $n"
done
sleep 2
for n in r1 r2 r3 r4 r5; do
  vtysh -N $n -c "configure terminal" -c "bfd" -c "profile fast" -c "detect-multiplier 3" \
        -c "receive-interval 50" -c "transmit-interval 50" -c "exit" -c "exit" 2>&1 | grep -v vtysh.conf
  for i in ${IFS_OF[$n]}; do
    vtysh -N $n -c "configure terminal" -c "interface $i" -c "ipv6 ospf6 bfd profile fast" -c "end" 2>&1 | grep -v vtysh.conf
  done
done
echo "--- waiting for 10 BFD sessions (5 links x 2 ends), max 20 s"
for t in $(seq 1 40); do
  up=0
  for n in r1 r2 r3 r4 r5; do
    c=$(vtysh -N $n -c "show bfd peers brief" 2>/dev/null | grep -c " up")
    up=$((up+c))
  done
  [ "$up" -ge 10 ] && break
  sleep 0.5
done
echo "sessions up: $up of 10"
for n in r1 r2 r3 r4 r5; do
  echo "--- $n"; vtysh -N $n -c "show bfd peers brief" 2>&1 | grep -v vtysh.conf
done
echo "--- ospf neighbours"
for n in r1 r2 r3 r4 r5; do echo "$n: $(vtysh -N $n -c 'show ipv6 ospf6 neighbor' 2>/dev/null | grep -c Full) Full"; done
