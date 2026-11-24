#!/usr/bin/env python3
"""Silent failure on the REMOTE link r2-r5 (path A, not adjacent to r1), with real BFD on that
link ON or OFF. Modes: remote_loose (SRv6 one SID, OSPF picks the path) and remote_off (plain IPv6).
Usage (root, after scripts/overlay_up.sh and scripts/bfd_all.sh):
  sudo python3 overlay_remote.py --r2r5-bfd on  --runs 10 --out results_remote_bfd
  sudo python3 overlay_remote.py --r2r5-bfd off --runs 10 --out results_remote_nobfd"""
import sys, time
import overlay_experiment as oe

oe.MODES["remote_loose"] = ("loose", None)
oe.MODES["remote_off"] = ("off", None)


def clear_failure():
    oe.run(oe.ns("r2", "tc", "qdisc", "del", "dev", "to5", "root"), check=False)
    oe.run(oe.ns("r5", "tc", "qdisc", "del", "dev", "to2", "root"), check=False)


def inject_failure():
    t0 = time.monotonic_ns()
    oe.run(oe.ns("r2", "tc", "qdisc", "add", "dev", "to5", "root", "netem", "loss", "100%"))
    t_applied, wall = time.monotonic_ns(), time.time_ns()
    oe.run(oe.ns("r5", "tc", "qdisc", "add", "dev", "to2", "root", "netem", "loss", "100%"))
    return t0, t_applied, wall


def set_bfd(on):
    cmd = "ipv6 ospf6 bfd profile fast" if on else "no ipv6 ospf6 bfd"
    for n, i in (("r2", "to5"), ("r5", "to2")):
        oe.run(["vtysh", "-N", n, "-c", "configure terminal", "-c", f"interface {i}",
                "-c", cmd, "-c", "end"], check=False)
    time.sleep(8)
    r = oe.run(["vtysh", "-N", "r2", "-c", "show bfd peers brief"], check=False).stdout
    print(f"r2 BFD sessions up: {r.count(' up')} (expect 2 with BFD on, 1 with BFD off)")


oe.clear_failure = clear_failure
oe.inject_failure = inject_failure

if "--r2r5-bfd" not in sys.argv:
    sys.exit("give --r2r5-bfd on|off")
k = sys.argv.index("--r2r5-bfd")
state = sys.argv[k + 1]
del sys.argv[k:k + 2]
if "--modes" not in sys.argv:
    sys.argv += ["--modes", "remote_loose,remote_off"]
if "--out" not in sys.argv:
    sys.argv += ["--out", str(oe.ROOT / ("results_remote_" + ("bfd" if state == "on" else "nobfd")))]
set_bfd(state == "on")
oe.main()
