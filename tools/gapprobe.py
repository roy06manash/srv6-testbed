#!/usr/bin/env python3
"""Diagnostic: probe the echo responder at a fixed interval and report reply gaps."""
import argparse, select, socket, struct, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--port", type=int, default=7777)
    ap.add_argument("--bind")
    ap.add_argument("--interval-ms", type=float, default=20.0)
    ap.add_argument("--seconds", type=float, default=4.0)
    a = ap.parse_args()
    ai = socket.getaddrinfo(a.target, a.port, type=socket.SOCK_DGRAM)[0]
    s = socket.socket(ai[0], socket.SOCK_DGRAM)
    if a.bind:
        s.bind((a.bind, 0))
    interval = a.interval_ms / 1000.0
    end = time.monotonic() + a.seconds
    next_send = time.monotonic()
    last, gaps, sent = None, [], 0
    while time.monotonic() < end:
        now = time.monotonic()
        if now >= next_send:
            s.sendto(struct.pack("!Q", sent), ai[4])
            sent += 1
            next_send += interval
            if next_send < now:
                next_send = now + interval
        ready, _, _ = select.select([s], [], [], max(0.0, next_send - time.monotonic()))
        if ready:
            while True:
                try:
                    s.recv(64, socket.MSG_DONTWAIT)
                except BlockingIOError:
                    break
                t = time.monotonic()
                if last is not None:
                    gaps.append((t - last) * 1000)
                last = t
    gaps.sort()
    n = len(gaps)
    print("probes sent %d, replies %d | max gap %.1f ms | p99 %.1f ms | gaps>40ms: %d | gaps>60ms: %d"
          % (sent, n + 1, gaps[-1] if n else 0, gaps[int(0.99 * (n - 1))] if n else 0,
             sum(g > 40 for g in gaps), sum(g > 60 for g in gaps)))


if __name__ == "__main__":
    main()
