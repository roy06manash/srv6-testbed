#!/usr/bin/env python3
"""Interruption = the largest arrival gap in which packets were lost (minus the nominal packet
interval). Gaps with no loss (VM/receiver stalls) are ignored; a run with no lost packets has
interruption 0. Also reports total lost packets per run and runs whose loss gap starts more
than 50 ms away from the recorded failure time.
Usage: python3 tools/outage_summary.py results_linkdown results_localrepair ..."""
import csv, json, statistics as st, sys
from collections import defaultdict
from pathlib import Path

for folder in sys.argv[1:]:
    if not Path(folder, "raw").is_dir():
        print(f"\n=== {folder}: no raw/ folder, skipped"); continue
    ints, lost_tot, off, skipped = defaultdict(list), defaultdict(list), defaultdict(list), []
    for mp in sorted(Path(folder, "raw").glob("*.meta.json")):
        try:
            m = json.loads(mp.read_text()); tf = m["t_fail_applied_ns"]
            rows = sorted(((int(r["seq"]), int(r["recv_ns"])) for r in
                           csv.DictReader(open(Path(folder, m["recv_csv"])))), key=lambda x: x[1])
            sent = m["sender"]["sent"]
        except Exception as e:
            skipped.append((mp.name, str(e)[:40])); continue
        iv = 1e3 / m["pps"]
        best, start = 0.0, None
        for (s0, t0), (s1, t1) in zip(rows, rows[1:]):
            if s1 - s0 - 1 > 0 and (t1 - t0) / 1e6 - iv > best:
                best, start = (t1 - t0) / 1e6 - iv, (t0 - tf) / 1e6
        mode = m["mode"]
        ints[mode].append(best)
        lost_tot[mode].append(sent - len({s for s, _ in rows}))
        if start is not None and abs(start) > 50:
            off[mode].append((m["label"], round(start, 1), round(best, 1)))
    print(f"\n=== {folder}  (interruption = largest loss-bearing gap, ms; lost = sent - received)")
    for mode in ints:
        for name, v in (("interruption ms", ints[mode]), ("lost packets", lost_tot[mode])):
            sd = st.stdev(v) if len(v) > 1 else 0.0
            print(f"  {mode:22s} {name:16s} n={len(v):2d} mean={st.mean(v):9.2f} median={st.median(v):9.2f}"
                  f" sd={sd:8.2f} min={min(v):8.2f} max={max(v):9.2f}")
        for o in off[mode]:
            print(f"     note: {o[0]} loss gap starts {o[1]} ms from the failure time, length {o[2]} ms")
    for s in skipped:
        print("  skipped:", *s)
