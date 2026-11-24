#!/usr/bin/env python3
"""UDP echo used as the liveness peer for the failure detector (runs on r2)."""
import argparse, socket


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bind")
    ap.add_argument("--port", type=int, default=7777)
    a = ap.parse_args()
    ai = socket.getaddrinfo(a.bind, a.port, type=socket.SOCK_DGRAM, flags=socket.AI_PASSIVE)[0]
    s = socket.socket(ai[0], socket.SOCK_DGRAM)
    s.bind(ai[4])
    while True:
        data, peer = s.recvfrom(256)
        s.sendto(data, peer)


if __name__ == "__main__":
    main()
