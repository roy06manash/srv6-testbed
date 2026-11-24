#!/usr/bin/env python3
"""OSPFv3 baseline: repeated failures that the routing protocol itself repairs (no detector,
no scripted switch). Run as root after scripts/ospf_up.sh. Writes results_ospf/raw/ospf_NNN.*
in the same format as run_experiment.py so analyze.py can summarise it."""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

from run_experiment import ROOT, TOOLS, H2, clear_failure, inject_failure, ns, run


def converged():
    """All 10 adjacencies Full and r1 reaches h2's prefix via the primary link (to2)."""
    full = 0
    for n in ("r1", "r2", "r3", "r4", "r5"):
        out = subprocess.run(["vtysh", "-N", n, "-c", "show ipv6 ospf6 neighbor"],
                             capture_output=True, text=True).stdout
        full += out.count("Full")
    route = subprocess.run(["ip", "-n", "r1", "-6", "route", "show", "2001:db8:a5::/64"],
                           capture_output=True, text=True).stdout
    return full >= 10 and "dev to2" in route


def wait_converged(timeout):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        if converged():
            return True
        time.sleep(0.5)
    return False


def run_one(label, out, a):
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    clear_failure()
    if not wait_converged(90):
        print(f"  {label}: OSPF did not reconverge on the primary path; skipping")
        return False
    time.sleep(1.0)
    run(ns("h1", "ping", "-6", "-c", "3", "-i", "0.2", "-W", "1", H2), check=False)
    recv_csv, snd_json = raw / f"{label}.csv", raw / f"{label}.sender.json"
    recv = subprocess.Popen(ns("h2", "python3", TOOLS / "udp_receiver.py", "--port", 9000,
                               "--run-for", a.duration + 2.5, "--out", recv_csv))
    time.sleep(0.3)
    snd = subprocess.Popen(ns("h1", "python3", TOOLS / "udp_sender.py", H2, "--port", 9000,
                              "--pps", a.pps, "--duration", a.duration, "--out", snd_json))
    time.sleep(a.fail_at + 0.5)  # same offset as run_experiment.py
    _, t_applied, wall = inject_failure()
    snd.wait(timeout=a.duration + 15)
    recv.wait(timeout=a.duration + 15)
    clear_failure()
    sender = json.loads(snd_json.read_text())
    meta = {"mode": "ospf", "label": label, "verify": False, "pps": a.pps, "duration": a.duration,
            "t_fail_applied_ns": t_applied, "t_fail_wall_ns": wall, "sender": sender,
            "detector": None, "recv_csv": f"raw/{label}.csv",
            "ospf_hello_s": a.hello, "ospf_dead_s": a.dead}
    (raw / f"{label}.meta.json").write_text(json.dumps(meta, indent=1))
    received = sum(1 for _ in open(recv_csv)) - 1
    print(f"  {label}: lost {sender['sent'] - received} of {sender['sent']} packets")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--pps", type=int, default=1000)
    ap.add_argument("--duration", type=float, default=10.0)
    ap.add_argument("--fail-at", type=float, default=2.0)
    ap.add_argument("--hello", type=int, default=1, help="OSPF hello s (label only; set by ospf_up.sh)")
    ap.add_argument("--dead", type=int, default=3, help="OSPF dead s (label only; set by ospf_up.sh)")
    ap.add_argument("--out", default=str(ROOT / "results_ospf"))
    a = ap.parse_args()
    if os.geteuid() != 0:
        sys.exit("run as root (sudo)")
    if not wait_converged(60):
        sys.exit("OSPF is not up/converged: run scripts/ospf_up.sh first")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    done = 0
    for i in range(a.runs):
        print(f"run {i + 1}/{a.runs}")
        done += run_one(f"ospf_{i:03d}", out, a)
    print(f"Done: {done} runs. Next: python3 analyze.py {out}")


if __name__ == "__main__":
    main()
