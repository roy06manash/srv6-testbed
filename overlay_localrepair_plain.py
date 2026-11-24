#!/usr/bin/env python3
"""Control for the local repair: the same link-down failure and the same primary/backup metric
pair at r1, but PLAIN IPv6 routes (no SRH). Modes: plain_protected (plain routes) and
overlay_protected (SRv6 routes). Output: results_localrepair_plain/
Usage (root, after scripts/overlay_up.sh):  sudo python3 overlay_localrepair_plain.py --runs 10"""
import sys, time
import overlay_experiment as oe

DST = "2001:db8:a5::/65"
orig_policy = oe.policy


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


def r3_addr():
    o = oe.run(["ip", "-n", "r3", "-6", "-o", "addr", "show", "dev", "to1", "scope", "global"]).stdout
    return o.split("inet6 ")[1].split("/")[0]


def policy(p):
    if p == "plain-protected":
        orig_policy("off")
        r1 = lambda *c: oe.run(oe.ns("r1", *c))
        r1("sysctl", "-qw", "net.ipv6.conf.to2.ignore_routes_with_linkdown=1")
        r1("ip", "-6", "route", "replace", DST, "via", "2001:db8:12::2", "dev", "to2", "metric", "10")
        r1("ip", "-6", "route", "replace", DST, "via", R3, "dev", "to3", "metric", "20")
    else:
        orig_policy(p)


orig_warmup = oe.warmup


def warmup(initial):
    """Run the normal warmup, then require 10 of 10 pings to succeed before the run starts."""
    orig_warmup(initial)
    t = time.time()
    while time.time() - t < 40:
        r = oe.run(oe.ns("h1", "ping", "-6", "-c", "10", "-i", "0.1", "-W", "1", oe.H2), check=False)
        if ", 0% packet loss" in r.stdout:
            return
        time.sleep(1)
    print("WARNING: connectivity not stable after 40 s")


R3 = r3_addr()
print("r3 address on the r1-r3 link:", R3)
oe.policy = policy
oe.warmup = warmup
oe.clear_failure = clear_failure
oe.inject_failure = inject_failure
oe.MODES.clear()
oe.MODES.update({"plain_protected": ("plain-protected", None),
                 "overlay_protected": ("protected", None)})
if "--out" not in sys.argv:
    sys.argv += ["--out", str(oe.ROOT / "results_localrepair_plain")]
if "--modes" not in sys.argv:
    sys.argv += ["--modes", ",".join(oe.MODES)]
keep_addresses()
clear_failure()
oe.main()
