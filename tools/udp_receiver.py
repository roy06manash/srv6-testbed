#!/usr/bin/env python3
"""UDP receiver: logs (seq, send_ns, recv_ns) with CLOCK_MONOTONIC (shared by all namespaces)."""
import argparse, socket, struct, time

HDR = struct.Struct("!QQ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", default="::")
    ap.add_argument("--port", type=int, default=9000)
    ap.add_argument("--run-for", type=float, default=8.0, help="seconds to listen")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    ai = socket.getaddrinfo(a.bind, a.port, type=socket.SOCK_DGRAM, flags=socket.AI_PASSIVE)[0]
    s = socket.socket(ai[0], socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 << 20)
    s.bind(ai[4])
    s.settimeout(0.2)
    deadline = time.monotonic() + a.run_for
    recs = []
    while time.monotonic() < deadline:
        try:
            d = s.recv(2048)
        except socket.timeout:
            continue
        t = time.monotonic_ns()
        if len(d) >= HDR.size:
            seq, sent = HDR.unpack_from(d)
            recs.append((seq, sent, t))
    with open(a.out, "w") as f:
        f.write("seq,send_ns,recv_ns\n")
        for r in recs:
            f.write("%d,%d,%d\n" % r)
    print("received", len(recs))


if __name__ == "__main__":
    main()
