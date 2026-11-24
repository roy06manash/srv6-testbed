#!/usr/bin/env bash
# Start echo (r2) + detector (r1), inject a silent failure on r1-r2, show detector log.
T="$(cd "$(dirname "$0")/.." && pwd)"
LOG="$(mktemp -d)/det.json"
ip netns exec r2 python3 "$T/tools/echo_responder.py" 2001:db8:12::2 &
ECHO=$!
sleep 0.5
ip netns exec r1 python3 "$T/tools/detector.py" 2001:db8:12::2 --bind 2001:db8:12::1 \
    --interval-ms 50 --mult 3 --on-down "echo '>>> SWITCH TRIGGERED'" \
    --log "$LOG" --max-seconds 6 &
DET=$!
sleep 1
echo "--- injecting failure"
ip netns exec r1 tc qdisc add dev to2 root netem loss 100% || { kill $ECHO $DET; exit 1; }
ip netns exec r2 tc qdisc add dev to1 root netem loss 100%
wait $DET
ip netns exec r1 tc qdisc del dev to2 root
ip netns exec r2 tc qdisc del dev to1 root
kill $ECHO
