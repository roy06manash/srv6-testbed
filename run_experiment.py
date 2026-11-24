#!/usr/bin/env python3
"""Repeated-failure experiment driver (run as root after scripts/setup.sh).

For each run and each mode (ipv6 = plain IPv6 routing, srv6 = explicit SRv6 policy):
  reset -> warm up both paths -> start receiver, detector, sender -> inject a silent
  failure on the r1-r2 link (tc netem loss 100 %) -> detector switches r1 to the backup
  policy -> collect timestamps. Optional --capture adds one extra (unmeasured) run per
  mode with tcpdump on every link for SID-traversal verification.
"""
import argparse, json, os, shutil, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
H2, R1_LINK, R2_LINK = "2001:db8:a5::2", "2001:db8:12::1", "2001:db8:12::2"
CAPTURE_POINTS = [("r1", "toh1"), ("r1", "to2"), ("r2", "to5"), ("r1", "to3"),
                  ("r3", "to4"), ("r4", "to5"), ("r5", "toh2")]


def ns(name, *cmd):
    return ["ip", "netns", "exec", name, *map(str, cmd)]


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def policy(mode, which):
    run(ns("r1", ROOT / "scripts" / "set_policy.sh", f"{mode}-{which}"))


def clear_failure():
    run(ns("r1", "tc", "qdisc", "del", "dev", "to2", "root"), check=False)
    run(ns("r2", "tc", "qdisc", "del", "dev", "to1", "root"), check=False)


def inject_failure():
    t0 = time.monotonic_ns()
    run(ns("r1", "tc", "qdisc", "add", "dev", "to2", "root", "netem", "loss", "100%"))
    t_applied, wall = time.monotonic_ns(), time.time_ns()
    run(ns("r2", "tc", "qdisc", "add", "dev", "to1", "root", "netem", "loss", "100%"))
    return t0, t_applied, wall


def warmup(mode):
    """Resolve neighbours on both paths so NDP does not pollute the repair measurement."""
    for which in ("primary", "backup", "primary"):
        policy(mode, which)
        run(ns("h1", "ping", "-6", "-c", "3", "-i", "0.2", "-W", "1", H2))


def run_one(mode, label, out, a, capture):
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    clear_failure()
    warmup(mode)
    policy(mode, "primary")
    time.sleep(0.5)

    caps = []
    if capture:
        pdir = out / "pcaps" / mode
        pdir.mkdir(parents=True, exist_ok=True)
        for n, i in CAPTURE_POINTS:
            caps.append(subprocess.Popen(
                ns(n, "tcpdump", "-Z", "root", "-n", "-U", "-i", i, "-w", pdir / f"{n}_{i}.pcap", "ip6"),
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        time.sleep(1.0)

    recv_csv, det_log, snd_json = (raw / f"{label}.csv", raw / f"{label}.detector.json",
                                   raw / f"{label}.sender.json")
    recv = subprocess.Popen(ns("h2", "python3", TOOLS / "udp_receiver.py", "--port", 9000,
                               "--run-for", a.duration + 2.5, "--out", recv_csv))
    time.sleep(0.3)
    # Start traffic first. With an idle VM, timer wake-ups were delayed by 60-95 ms, which
    # breaks short detector timers; under load they are prompt. So the detector starts last.
    snd = subprocess.Popen(ns("h1", "python3", TOOLS / "udp_sender.py", H2, "--port", 9000,
                              "--pps", a.pps, "--duration", a.duration, "--out", snd_json))
    DET_DELAY = 0.6
    time.sleep(DET_DELAY)
    det = subprocess.Popen(ns("r1", "python3", TOOLS / "detector.py", R2_LINK, "--bind", R1_LINK,
                              "--interval-ms", a.detect_interval_ms, "--mult", a.detect_mult,
                              "--on-down", f"{ROOT / 'scripts' / 'set_policy.sh'} {mode}-backup",
                              "--log", det_log, "--max-seconds", a.duration + 1))
    time.sleep(max(0.0, a.fail_at + 0.5 - DET_DELAY))  # 0.5 s = sender start offset + start-up
    t_before, t_applied, wall = inject_failure()

    for p in (snd, recv, det):
        p.wait(timeout=a.duration + 15)
    for c in caps:
        c.send_signal(signal.SIGINT)
        c.wait(timeout=5)
    clear_failure()
    policy(mode, "primary")

    meta = {"mode": mode, "label": label, "verify": capture, "pps": a.pps, "duration": a.duration,
            "t_fail_before_ns": t_before, "t_fail_applied_ns": t_applied, "t_fail_wall_ns": wall,
            "sender": json.loads(snd_json.read_text()),
            "detector": json.loads(det_log.read_text()),
            "recv_csv": f"raw/{label}.csv",
            "rc": {"sender": snd.returncode, "receiver": recv.returncode, "detector": det.returncode}}
    (raw / f"{label}.meta.json").write_text(json.dumps(meta, indent=1))
    d = meta["detector"]
    if d["t_detect_ns"]:
        print(f"  {label}: detect {(d['t_detect_ns'] - t_applied) / 1e6:.1f} ms, "
              f"repair cmd {(d['t_repair_done_ns'] - d['t_detect_ns']) / 1e6:.1f} ms")
    else:
        print(f"  {label}: FAILURE NOT DETECTED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--modes", default="ipv6,srv6")
    ap.add_argument("--pps", type=int, default=1000)
    ap.add_argument("--duration", type=float, default=6.0)
    ap.add_argument("--fail-at", type=float, default=2.0, help="seconds after traffic start")
    ap.add_argument("--detect-interval-ms", type=float, default=50.0)
    ap.add_argument("--detect-mult", type=int, default=3)
    ap.add_argument("--settle", type=float, default=2.0)
    ap.add_argument("--capture", action="store_true", help="extra unmeasured run per mode with pcaps")
    ap.add_argument("--out", default=str(ROOT / "results"))
    a = ap.parse_args()

    if os.geteuid() != 0:
        sys.exit("run as root (sudo)")
    need = ["ip", "tc", "ping"] + (["tcpdump"] if a.capture else [])
    missing = [t for t in need if not shutil.which(t)]
    if missing:
        sys.exit("missing tools: " + ", ".join(missing))
    if run(["ip", "netns", "list"], check=False).stdout.find("r1") < 0:
        sys.exit("testbed not up: run scripts/setup.sh first")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    modes = a.modes.split(",")
    echo = subprocess.Popen(ns("r2", "python3", TOOLS / "echo_responder.py", R2_LINK),
                            stdout=subprocess.DEVNULL)
    time.sleep(0.5)
    try:
        if a.capture:
            for m in modes:
                print(f"verification run ({m}, with captures)")
                run_one(m, f"{m}_verify", out, a, capture=True)
                time.sleep(a.settle)
        for i in range(a.runs):
            for m in (modes if i % 2 == 0 else modes[::-1]):  # alternate order to cancel drift
                print(f"run {i + 1}/{a.runs} mode {m}")
                run_one(m, f"{m}_{i:03d}", out, a, capture=False)
                time.sleep(a.settle)
    finally:
        echo.terminate()
        clear_failure()
    print(f"Done. Next: python3 analyze.py {out}  (and python3 verify_sids.py {out} if --capture)")


if __name__ == "__main__":
    main()
