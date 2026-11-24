#!/usr/bin/env python3
"""Link-down failure with a pre-computed local repair at r1 (TI-LFA-like, NOT TI-LFA):
primary and backup SRv6 policies are installed together, and the kernel skips the primary when
its link loses carrier. Modes: overlay_protected (local repair), overlay_pinned (OSPF repairs),
overlay_off (plain IPv6 over OSPFv3). Output: results_localrepair/
Usage (root, after scripts/overlay_up.sh):  sudo python3 overlay_localrepair.py --runs 10"""
import sys, time
import overlay_experiment as oe

oe.MODES.clear()
oe.MODES.update({"overlay_off": ("off", None), "overlay_pinned": ("pinned-primary", None),
                 "overlay_protected": ("protected", None)})


def keep_addresses():
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
    sys.argv += ["--out", str(oe.ROOT / "results_localrepair")]
if "--modes" not in sys.argv:
    sys.argv += ["--modes", ",".join(oe.MODES)]
keep_addresses()
clear_failure()
oe.main()
