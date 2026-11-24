#!/usr/bin/env bash
# Stop any per-router FRR daemons, then remove all testbed namespaces.
pkill -f '/usr/lib/frr/(zebra|ospf6d|bfdd)' 2>/dev/null || true
sleep 0.5
for n in r1 r2 r3 r4 r5; do rm -rf "/var/run/frr/$n"; done
for n in h1 r1 r2 r3 r4 r5 h2; do
  ip netns del "$n" 2>/dev/null || true
done
