#!/usr/bin/env bash
# Send 2 s of 1000 pps UDP from h1 to h2 and report how many packets arrived.
T="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(mktemp -d)"
ip netns exec h2 python3 "$T/tools/udp_receiver.py" --run-for 4 --out "$OUT/rx.csv" &
sleep 0.5
ip netns exec h1 python3 "$T/tools/udp_sender.py" 2001:db8:a5::2 --pps 1000 --duration 2
wait
echo "--- first rows of the receiver log"
head -4 "$OUT/rx.csv"
echo "rows: $(($(wc -l < "$OUT/rx.csv") - 1))"
