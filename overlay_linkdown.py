#!/usr/bin/env python3
"""Same experiment as overlay_experiment.py, but the failure is a real link-down (carrier loss):
r2's interface to1 is set administratively down, so r1's to2 loses carrier. FRRouting sees the
interface event immediately instead of waiting for the OSPF dead interval.

Adds the mode overlay_off (no SRv6 policy: plain IPv6 over the OSPFv3 underlay).
Output: results_linkdown/  ->  python3 analyze.py results_linkdown
Usage (root, after scripts/overlay_up.sh):  sudo python3 overlay_linkdown.py --runs 10
"""
import sys, time
import overlay_experiment as oe

oe.MODES["overlay_off"] = ("off", None)


def keep_addresses():
    # without this, `ip link set down` deletes the IPv6 addresses and the detector peer goes silent
    for ns, dev in (("r1", "to2"), ("r2", "to1")):
        oe.run(oe.ns(ns, "sysctl", "-qw", f"net.ipv6.conf.{dev}.keep_addr_on_down=1"), check=False)


def clear_failure():
    oe.run(oe.ns("r2", "ip", "link", "set", "to1", "up"), check=False)
    oe.run(oe.ns("r2", "ip", "addr", "add", "2001:db8:12::2/64", "dev", "to1", "nodad"), check=False)
    oe.run(oe.ns("r1", "ip", "addr", "add", "2001:db8:12::1/64", "dev", "to2", "nodad"), check=False)


def inject_failure():
    t0 = time.monotonic_ns()
    oe.run(oe.ns("r2", "ip", "link", "set", "to1", "down"))
    return t0, time.monotonic_ns(), time.time_ns()


oe.clear_failure = clear_failure
oe.inject_failure = inject_failure

if "--out" not in sys.argv:
    sys.argv += ["--out", str(oe.ROOT / "results_linkdown")]
keep_addresses()
clear_failure()
oe.main()
