#!/usr/bin/env python3
"""BFD-like liveness prober + scripted repair (NOT real BFD; see stretch goals).

Sends a UDP probe every --interval-ms and tracks the time of the LAST valid reply.
Like BFD, the detection time is --mult x --interval-ms measured from the last reply
received, and the detector only arms after --arm-after consecutive replies (session "Up"),
so start-up effects cannot trigger a false alarm. On expiry it runs --on-down (the
backup-policy switch) and logs CLOCK_MONOTONIC timestamps: arming, detection decision and
repair-command completion. Expected detection delay after a silent failure is roughly
(mult-1)*interval to mult*interval, plus scheduling jitter.
"""
import argparse, json, select, socket, struct, subprocess, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--port", type=int, default=7777)
    ap.add_argument("--bind", help="source address")
    ap.add_argument("--interval-ms", type=float, default=50.0)
    ap.add_argument("--mult", type=int, default=3)
    ap.add_argument("--arm-after", type=int, default=5, help="consecutive replies before arming")
    ap.add_argument("--on-down", required=True, help="shell command run on detection")
    ap.add_argument("--log", required=True)
    ap.add_argument("--max-seconds", type=float, default=30.0)
    a = ap.parse_args()

    ai = socket.getaddrinfo(a.target, a.port, type=socket.SOCK_DGRAM)[0]
    s = socket.socket(ai[0], socket.SOCK_DGRAM)
    if a.bind:
        s.bind((a.bind, 0))
    interval = a.interval_ms / 1000.0
    hold = a.mult * interval
    log = {"interval_ms": a.interval_ms, "mult": a.mult, "arm_after": a.arm_after,
           "t_start_ns": time.monotonic_ns(), "t_armed_ns": None, "t_detect_ns": None,
           "t_repair_done_ns": None, "repair_rc": None, "probes": 0}
    deadline = time.monotonic() + a.max_seconds
    seq = good = 0
    armed = False
    last = next_send = time.monotonic()
    while time.monotonic() < deadline:
        now = time.monotonic()
        if now >= next_send:
            s.sendto(struct.pack("!Q", seq), ai[4])
            seq += 1
            log["probes"] += 1
            next_send += interval
            if next_send < now:          # fell behind: resync instead of bursting
                next_send = now + interval
        wake = min(next_send, last + hold) if armed else next_send
        ready, _, _ = select.select([s], [], [], max(0.0, wake - time.monotonic()))
        if ready:
            while True:                  # drain every reply that is waiting
                try:
                    d = s.recv(64, socket.MSG_DONTWAIT)
                except BlockingIOError:
                    break
                if len(d) >= 8:
                    last = time.monotonic()
                    good += 1
                    if not armed and good >= a.arm_after:
                        armed = True
                        log["t_armed_ns"] = time.monotonic_ns()
        if armed and time.monotonic() - last >= hold:
            log["t_detect_ns"] = time.monotonic_ns()
            rc = subprocess.run(a.on_down, shell=True).returncode
            log["t_repair_done_ns"] = time.monotonic_ns()
            log["repair_rc"] = rc
            break
    with open(a.log, "w") as f:
        json.dump(log, f)
    print(json.dumps(log))


if __name__ == "__main__":
    main()
