#!/usr/bin/env python3
"""Constant-rate UDP sender. Payload = seq (u64) + send CLOCK_MONOTONIC ns (u64) + padding."""
import argparse, json, socket, struct, time

HDR = struct.Struct("!QQ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dst")
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--pps", type=int, default=1000)
    ap.add_argument("--duration", type=float, default=6.0)
    ap.add_argument("--size", type=int, default=100, help="UDP payload bytes (>=16)")
    ap.add_argument("--out", help="write summary JSON here")
    a = ap.parse_args()

    ai = socket.getaddrinfo(a.dst, a.port, type=socket.SOCK_DGRAM)[0]
    s = socket.socket(ai[0], socket.SOCK_DGRAM)
    pad = bytes(max(0, a.size - HDR.size))
    interval = 1_000_000_000 // a.pps
    total = int(a.duration * a.pps)
    start = time.monotonic_ns() + 200_000_000
    sent = errors = 0
    for i in range(total):
        due = start + i * interval
        while True:
            now = time.monotonic_ns()
            if now >= due:
                break
            if due - now > 2_000_000:
                time.sleep((due - now - 1_000_000) / 1e9)
        try:
            s.sendto(HDR.pack(i, now) + pad, ai[4])
        except OSError:
            errors += 1
        sent += 1
    summary = {"sent": sent, "send_errors": errors, "pps": a.pps, "start_ns": start,
               "interval_ns": interval, "size": a.size}
    if a.out:
        with open(a.out, "w") as f:
            json.dump(summary, f)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
