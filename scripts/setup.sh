#!/usr/bin/env bash
# Build the five-router SRv6 testbed in Linux network namespaces. Run as root.
#
#   h1 -- r1 -- r2 -- r5 -- h2        Path A (primary): r1-r2-r5
#          \         /
#           r3 -- r4                 Path B (backup):  r1-r3-r4-r5
#
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ "$(id -u)" -eq 0 ] || { echo "run as root (sudo)"; exit 1; }

"$HERE/teardown.sh"

for n in h1 r1 r2 r3 r4 r5 h2; do
  ip netns add "$n"
  ip -n "$n" link set lo up
done

if ! ip netns exec r1 sysctl -n net.ipv6.conf.all.seg6_enabled >/dev/null 2>&1; then
  echo "This kernel has no SRv6 support (needs CONFIG_IPV6_SEG6_LWTUNNEL, Linux >= 4.10)." >&2
  exit 1
fi

for n in r1 r2 r3 r4 r5; do
  ip netns exec "$n" sysctl -qw \
    net.ipv6.conf.all.forwarding=1 \
    net.ipv6.conf.all.seg6_enabled=1 \
    net.ipv6.conf.default.seg6_enabled=1
done

# link <nsA> <ifA> <addrA/64> <nsB> <ifB> <addrB/64>
link() {
  ip link add "$2" netns "$1" type veth peer name "$5" netns "$4"
  local side
  for side in "$1 $2 $3" "$4 $5 $6"; do
    # shellcheck disable=SC2086
    set -- $side
    ip -n "$1" link set "$2" up
    ip netns exec "$1" sysctl -qw "net.ipv6.conf.$2.seg6_enabled=1" \
      "net.ipv6.conf.$2.accept_dad=0" "net.ipv6.conf.$2.accept_ra=0"
    ip -n "$1" addr add "$3" dev "$2" nodad
  done
}

link h1 hif 2001:db8:a1::2/64  r1 toh1 2001:db8:a1::1/64
link r1 to2  2001:db8:12::1/64  r2 to1  2001:db8:12::2/64
link r2 to5  2001:db8:25::2/64  r5 to2  2001:db8:25::5/64
link r1 to3  2001:db8:13::1/64  r3 to1  2001:db8:13::3/64
link r3 to4  2001:db8:34::3/64  r4 to3  2001:db8:34::4/64
link r4 to5  2001:db8:45::4/64  r5 to4  2001:db8:45::5/64
link r5 toh2 2001:db8:a5::1/64  h2 hif 2001:db8:a5::2/64

r() { local n=$1; shift; ip -n "$n" -6 route add "$@"; }

# Hosts
r h1 default via 2001:db8:a1::1 dev hif
r h2 default via 2001:db8:a5::1 dev hif

# Underlay reachability of the *adjacent* node locators (all SIDs used are next-hop neighbours)
r r1 fc00:2::/32 via 2001:db8:12::2 dev to2
r r1 fc00:3::/32 via 2001:db8:13::3 dev to3
r r2 fc00:5::/32 via 2001:db8:25::5 dev to5
r r3 fc00:4::/32 via 2001:db8:34::4 dev to4
r r4 fc00:5::/32 via 2001:db8:45::5 dev to5

# Plain IPv6 forwarding towards h2's prefix (used by the ordinary-IPv6 baseline)
r r2 2001:db8:a5::/64 via 2001:db8:25::5 dev to5
r r3 2001:db8:a5::/64 via 2001:db8:34::4 dev to4
r r4 2001:db8:a5::/64 via 2001:db8:45::5 dev to5
# Return path (h2 -> h1), plain IPv6 over the primary path
r r5 2001:db8:a1::/64 via 2001:db8:25::2 dev to2
r r2 2001:db8:a1::/64 via 2001:db8:12::1 dev to1
r r3 2001:db8:a1::/64 via 2001:db8:13::1 dev to1
r r4 2001:db8:a1::/64 via 2001:db8:34::3 dev to3

# SRv6 SIDs: locator fc00:N::/32, End = fc00:N::1, End.DT6 on r5 = fc00:5::d6
for n in 1 2 3 4 5; do
  ip -n "r$n" link add sid0 type dummy
  ip -n "r$n" link set sid0 up
  r "r$n" "fc00:$n::1/128" encap seg6local action End dev sid0
done
r r5 fc00:5::d6/128 encap seg6local action End.DT6 table 254 dev sid0

# R1 steering policy for h2's prefix (set per experiment mode)
ip netns exec r1 "$HERE/set_policy.sh" srv6-primary

echo "Testbed up. Namespaces: h1 r1 r2 r3 r4 r5 h2"
echo "Quick check: sudo ip netns exec h1 ping -6 -c3 2001:db8:a5::2"
