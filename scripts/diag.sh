#!/usr/bin/env bash
# Diagnose where SRv6-steered packets get lost. Run as root inside the VM.
D="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"
ip netns exec r1 "$D/set_policy.sh" srv6-primary
for ns in r1 r2 r5; do ip netns exec $ns nstat -n; done

for spec in "r1 to2" "r2 to1" "r2 to5" "r5 to2" "r5 toh2"; do
  set -- $spec
  ip netns exec "$1" timeout 4 tcpdump -nn -l -i "$2" ip6 > "$T/$1_$2.txt" 2>&1 &
done
sleep 1
ip netns exec h1 ping -6 -c2 -W1 2001:db8:a5::2 | tail -2
sleep 3
for f in "$T"/*.txt; do
  echo "=== $(basename "$f" .txt)"
  grep -v -E 'listening|^$' "$f" | grep -E -v 'packets (captured|received|dropped)' | head -6
done
for ns in r1 r2 r5; do
  echo "=== $ns IPv6 counters (non-zero)"
  ip netns exec $ns nstat -az 2>/dev/null | grep Ip6 | awk '$2>0'
done
