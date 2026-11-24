#!/usr/bin/env bash
# Measured frame size of a 100-byte ping through r1: plain IPv6 vs seg6 encap vs encap.red.
# Captures on the first link after r1 (r2 for path A, r3 for path B). Run as root.
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }
cd "$(dirname "$0")/.."
DST=2001:db8:a5::/65; H2=2001:db8:a5::2
R1="ip netns exec r1"
clean() { for m in 10 20; do $R1 ip -6 route del $DST metric $m 2>/dev/null; done; $R1 ip -6 route del $DST 2>/dev/null; return 0; }
run_cfg() {  # label capture_ns capture_if mode segs dev
  clean
  if [ -n "$4" ]; then
    $R1 ip -6 route replace $DST encap seg6 mode $4 segs $5 dev $6 2>/tmp/ovh_err || { printf "%-34s UNSUPPORTED (%s)\n" "$1" "$(cat /tmp/ovh_err)"; return; }
  fi
  sleep 1
  rm -f /tmp/ovh.pcap
  ip netns exec $2 tcpdump -Z root -i $3 -Q in -nn -w /tmp/ovh.pcap >/dev/null 2>&1 &
  local tp=$!; sleep 0.7
  local rx; rx=$(ip netns exec h1 ping -6 -c 5 -i 0.3 -s 100 -W 1 $H2 | grep -o '[0-9]* received')
  sleep 0.5; kill $tp 2>/dev/null; wait $tp 2>/dev/null
  local rt; rt=$($R1 ip -6 route get $H2 2>/dev/null | head -1 | cut -c1-100)
  local l; l=$(tshark -r /tmp/ovh.pcap -Y "icmpv6.type==128" -T fields -e frame.len -e ipv6.nxt 2>/dev/null | head -1)
  printf "%-34s frame %s B / next-headers %s  (ping: %s)\n    route: %s\n" "$1" "$(echo "$l" | cut -f1)" "$(echo "$l" | cut -f2)" "$rx" "$rt"
}
run_cfg "plain IPv6 (path A)"           r2 to1 ""        ""                               ""
run_cfg "encap, path A, 2 SIDs"         r2 to1 encap     "fc00:2::1,fc00:5::d6"           to2
run_cfg "encap.red, path A, 2 SIDs"     r2 to1 encap.red "fc00:2::1,fc00:5::d6"           to2
run_cfg "encap, 1 SID"                  r2 to1 encap     "fc00:5::d6"                     to2
run_cfg "encap.red, 1 SID"              r2 to1 encap.red "fc00:5::d6"                     to2
run_cfg "encap, path B, 3 SIDs"         r3 to1 encap     "fc00:3::1,fc00:4::1,fc00:5::d6" to3
run_cfg "encap.red, path B, 3 SIDs"     r3 to1 encap.red "fc00:3::1,fc00:4::1,fc00:5::d6" to3
clean; $R1 scripts/set_overlay.sh off
echo "policy reset to off"
