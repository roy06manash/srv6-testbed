#!/usr/bin/env bash
# Independent cross-check of SRv6 hops with tshark (compare with results/sid_traversal.md).
P="$(cd "$(dirname "$0")/.." && pwd)/results/pcaps/srv6"
for f in r1_to2 r2_to5 r1_to3 r3_to4 r4_to5; do
  echo "--- $f"
  tshark -r "$P/$f.pcap" -Y "ipv6.routing.type == 4" \
    -T fields -e ipv6.dst -e ipv6.routing.segleft -e ipv6.routing.srh.last_entry 2>/dev/null \
    | sort | uniq -c | sort -rn | head -3
done
echo "--- r5_toh2 (should have no routing header)"
tshark -r "$P/r5_toh2.pcap" -Y "ipv6.routing.type == 4" 2>/dev/null | wc -l
