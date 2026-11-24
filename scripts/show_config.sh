#!/usr/bin/env bash
# Dump addresses, routes (incl. seg6 / seg6local) and sysctls of every node to results/config/.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/../results/config}"
mkdir -p "$OUT"
for n in h1 r1 r2 r3 r4 r5 h2; do
  {
    echo "### $n: ip -6 addr";  ip -n "$n" -6 addr show
    echo; echo "### $n: ip -6 route"; ip -n "$n" -6 route show
    echo; echo "### $n: seg6 sysctls"
    ip netns exec "$n" sysctl -a 2>/dev/null | grep -E 'seg6|\.forwarding' | grep -E 'all|default|to[0-9h]|hif'
  } > "$OUT/$n.txt"
done
echo "Wrote node configuration to $OUT"
