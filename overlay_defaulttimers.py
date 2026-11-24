#!/usr/bin/env python3
"""OSPFv3 with DEFAULT timers (hello 10 s, dead 40 s), BFD off, silent r1-r2 failure.
Modes: overlay_off (plain IPv6) and overlay_loose (SRv6, one SID). Restores hello 1 s / dead 3 s
and BFD on all links at the end.  Usage (root, after overlay_up.sh and bfd_all.sh):
  sudo python3 overlay_defaulttimers.py --runs 5"""
import subprocess, sys, time
import overlay_experiment as oe

oe.MODES["overlay_off"] = ("off", None)
LINKS = {"r1": ["to2", "to3"], "r2": ["to1", "to5"], "r3": ["to1", "to4"],
         "r4": ["to3", "to5"], "r5": ["to2", "to4"]}


def vt(n, iface, *cmds):
    args = ["vtysh", "-N", n, "-c", "configure terminal", "-c", f"interface {iface}"]
    for c in cmds:
        args += ["-c", c]
    oe.run(args + ["-c", "end"], check=False)


def set_timers(hello, dead, bfd_off=False):
    for n, ifs in LINKS.items():
        for i in ifs:
            if bfd_off:
                vt(n, i, "no ipv6 ospf6 bfd")
            vt(n, i, f"ipv6 ospf6 hello-interval {hello}", f"ipv6 ospf6 dead-interval {dead}")


def wait_full(limit):
    t = time.time()
    while time.time() - t < limit:
        ok = all(oe.run(["vtysh", "-N", n, "-c", "show ipv6 ospf6 neighbor"], check=False)
                 .stdout.count("Full") == 2 for n in LINKS)
        if ok:
            return True
        time.sleep(2)
    return False


for a, v in (("--modes", "overlay_off,overlay_loose"), ("--duration", "55"),
             ("--out", str(oe.ROOT / "results_ospf_default"))):
    if a not in sys.argv:
        sys.argv += [a, v]
try:
    set_timers(10, 40, bfd_off=True)
    print("waiting for OSPF Full on all routers with hello 10 / dead 40 ...")
    if not wait_full(120):
        sys.exit("OSPF did not reach Full with the default timers")
    oe.main()
finally:
    print("restoring hello 1 / dead 3 and BFD ...")
    set_timers(1, 3)
    wait_full(120)
    subprocess.run(["bash", str(oe.ROOT / "scripts" / "bfd_all.sh")], capture_output=True)
    print("restored")
