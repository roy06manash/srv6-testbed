#!/usr/bin/env python3
"""SRv6 overlay on an OSPFv3 underlay: repeated silent r1-r2 failures (run as root after
scripts/overlay_up.sh).

Modes (same traffic, same failure, OSPFv3 running underneath):
  overlay_loose        SRH with one SID (fc00:5::d6). OSPF alone chooses and repairs the path.
  overlay_pinned       SRH pinned through r2. No scripted repair.
  overlay_pinned_fast  Pinned policy + BFD-like detector that switches to the r3/r4 backup path.
Output: results_overlay/ (same format as run_experiment.py; use analyze.py).
"""
import argparse, json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / "tools"
SET = ROOT / "scripts" / "set_overlay.sh"
H2, R1_LINK, R2_LINK = "2001:db8:a5::2", "2001:db8:12::1", "2001:db8:12::2"
DET_DELAY = 0.6

MODES = {
    "overlay_loose": ("loose", None),
    "overlay_pinned": ("pinned-primary", None),
    "overlay_pinned_fast": ("pinned-primary", "pinned-backup"),
}


def ns(name, *cmd):
    return ["ip", "netns", "exec", name, *map(str, cmd)]


def run(cmd, check=True):
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def policy(p):
    run(ns("r1", SET, p))


def clear_failure():
    run(ns("r1", "tc", "qdisc", "del", "dev", "to2", "root"), check=False)
    run(ns("r2", "tc", "qdisc", "del", "dev", "to1", "root"), check=False)


def inject_failure():
    t0 = time.monotonic_ns()
    run(ns("r1", "tc", "qdisc", "add", "dev", "to2", "root", "netem", "loss", "100%"))
    t_applied, wall = time.monotonic_ns(), time.time_ns()
    run(ns("r2", "tc", "qdisc", "add", "dev", "to1", "root", "netem", "loss", "100%"))
    return t0, t_applied, wall


def underlay_primary():
    o = run(ns("r1", "ip", "-6", "route", "show", "fc00:5::/32"), check=False).stdout
    return "dev to2" in o and "dev to3" not in o


def wait_primary(timeout=60):
    t = time.time()
    while time.time() - t < timeout:
        if underlay_primary():
            return True
        time.sleep(0.5)
    return False


def warmup(initial):
    for p in ("pinned-primary", "pinned-backup", "loose", initial):
        policy(p)
        run(ns("h1", "ping", "-6", "-c", "3", "-i", "0.2", "-W", "1", H2), check=False)


def run_one(mode, label, out, a):
    initial, repair = MODES[mode]
    raw = out / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    clear_failure()
    if not wait_primary():
        sys.exit("OSPF did not return to the primary path; check scripts/ospf_diag.sh")
    warmup(initial)
    time.sleep(0.5)

    recv_csv, det_log, snd_json = (raw / f"{label}.csv", raw / f"{label}.detector.json",
                                   raw / f"{label}.sender.json")
    recv = subprocess.Popen(ns("h2", "python3", TOOLS / "udp_receiver.py", "--port", 9000,
                               "--run-for", a.duration + 2.5, "--out", recv_csv))
    time.sleep(0.3)
    snd = subprocess.Popen(ns("h1", "python3", TOOLS / "udp_sender.py", H2, "--port", 9000,
                              "--pps", a.pps, "--duration", a.duration, "--out", snd_json))
    det = None
    if repair:
        time.sleep(DET_DELAY)
        det = subprocess.Popen(ns("r1", "python3", TOOLS / "detector.py", R2_LINK, "--bind", R1_LINK,
                                  "--interval-ms", a.detect_interval_ms, "--mult", a.detect_mult,
                                  "--on-down", f"{SET} {repair}", "--log", det_log,
                                  "--max-seconds", a.duration + 1))
        time.sleep(max(0.0, a.fail_at + 0.5 - DET_DELAY))
    else:
        time.sleep(a.fail_at + 0.5)
    t_before, t_applied, wall = inject_failure()

    procs = [snd, recv] + ([det] if det else [])
    for p in procs:
        p.wait(timeout=a.duration + 15)
    clear_failure()
    policy(initial)

    meta = {"mode": mode, "label": label, "verify": False, "pps": a.pps, "duration": a.duration,
            "t_fail_before_ns": t_before, "t_fail_applied_ns": t_applied, "t_fail_wall_ns": wall,
            "sender": json.loads(snd_json.read_text()),
            "detector": json.loads(det_log.read_text()) if det else None,
            "recv_csv": f"raw/{label}.csv",
            "rc": {"sender": snd.returncode, "receiver": recv.returncode,
                   "detector": det.returncode if det else None}}
    (raw / f"{label}.meta.json").write_text(json.dumps(meta, indent=1))
    d = meta["detector"]
    extra = ""
    if d and d["t_detect_ns"]:
        extra = f", detect {(d['t_detect_ns'] - t_applied) / 1e6:.1f} ms"
    elif d:
        extra = ", FAILURE NOT DETECTED"
    print(f"  {label}: sent {meta['sender']['sent']}{extra}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--modes", default=",".join(MODES))
    ap.add_argument("--pps", type=int, default=1000)
    ap.add_argument("--duration", type=float, default=10.0)
    ap.add_argument("--fail-at", type=float, default=2.0)
    ap.add_argument("--detect-interval-ms", type=float, default=50.0)
    ap.add_argument("--detect-mult", type=int, default=3)
    ap.add_argument("--settle", type=float, default=2.0)
    ap.add_argument("--out", default=str(ROOT / "results_overlay"))
    a = ap.parse_args()
    if os.geteuid() != 0:
        sys.exit("run as root (sudo)")
    modes = a.modes.split(",")
    for m in modes:
        if m not in MODES:
            sys.exit(f"unknown mode {m}; choose from {', '.join(MODES)}")
    if "r1" not in run(["ip", "netns", "list"], check=False).stdout:
        sys.exit("testbed not up: run scripts/overlay_up.sh first")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    echo = subprocess.Popen(ns("r2", "python3", TOOLS / "echo_responder.py", R2_LINK),
                            stdout=subprocess.DEVNULL)
    time.sleep(0.5)
    try:
        for i in range(a.runs):
            order = modes if i % 2 == 0 else modes[::-1]
            for m in order:
                print(f"run {i + 1}/{a.runs} mode {m}")
                run_one(m, f"{m}_{i:03d}", out, a)
                time.sleep(a.settle)
    finally:
        echo.terminate()
        clear_failure()
        policy("pinned-primary")
    print(f"Done. Next: python3 analyze.py {out}")


if __name__ == "__main__":
    main()
