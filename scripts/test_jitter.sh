#!/usr/bin/env bash
# Compare echo-reply gaps with the network idle vs. with 1000 pps UDP load running.
T="$(cd "$(dirname "$0")/.." && pwd)"
echo "CPUs in this VM: $(nproc)"
ip netns exec r2 python3 "$T/tools/echo_responder.py" 2001:db8:12::2 &
ECHO=$!
sleep 0.5
echo "--- idle"
ip netns exec r1 python3 "$T/tools/gapprobe.py" 2001:db8:12::2 --bind 2001:db8:12::1 --seconds 4
echo "--- with 1000 pps UDP load h1 -> h2"
OUT="$(mktemp -d)"
ip netns exec h2 python3 "$T/tools/udp_receiver.py" --run-for 7 --out "$OUT/rx.csv" >/dev/null &
sleep 0.3
ip netns exec h1 python3 "$T/tools/udp_sender.py" 2001:db8:a5::2 --pps 1000 --duration 5 >/dev/null &
sleep 1
ip netns exec r1 python3 "$T/tools/gapprobe.py" 2001:db8:12::2 --bind 2001:db8:12::1 --seconds 4
wait %2 %3 2>/dev/null
kill $ECHO
