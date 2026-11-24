#!/usr/bin/env python3
"""One-off patch: start the UDP sender before the detector in run_experiment.py."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "run_experiment.py"
src = p.read_text()
old = r'''    det = subprocess.Popen(ns("r1", "python3", TOOLS / "detector.py", R2_LINK, "--bind", R1_LINK,
                              "--interval-ms", a.detect_interval_ms, "--mult", a.detect_mult,
                              "--on-down", f"{ROOT / 'scripts' / 'set_policy.sh'} {mode}-backup",
                              "--log", det_log, "--max-seconds", a.duration + 1))
    time.sleep(0.3)
    snd = subprocess.Popen(ns("h1", "python3", TOOLS / "udp_sender.py", H2, "--port", 9000,
                              "--pps", a.pps, "--duration", a.duration, "--out", snd_json))
    time.sleep(a.fail_at + 0.5)  # 0.5 s = sender start offset (0.2 s) + interpreter start-up
'''
new = r'''    # Start traffic first. With an idle VM, timer wake-ups were delayed by 60-95 ms, which
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
'''
assert src.count(old) == 1, "expected block not found; run_experiment.py differs from what I sent"
p.write_text(src.replace(old, new))
print("patched run_experiment.py")
