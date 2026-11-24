#!/usr/bin/env python3
"""List arrival gaps > 10 ms per run and classify them (outage / stall / before failure).
Usage: python3 tools/gap_report.py results_localrepair_plain [more result folders]"""
import csv, json, sys
from pathlib import Path

THR = 10e6  # ns
for folder in sys.argv[1:]:
    print(f"\n=== {folder}")
    n_pre = n_stall = n_out = 0
    for meta_p in sorted(Path(folder, "raw").glob("*.meta.json")):
        meta = json.loads(meta_p.read_text())
        tf = meta["t_fail_applied_ns"]
        rows = [(int(r["seq"]), int(r["recv_ns"])) for r in csv.DictReader(open(Path(folder, meta["recv_csv"])))]
        rows.sort(key=lambda x: x[1])
        found = []
        for (s0, t0), (s1, t1) in zip(rows, rows[1:]):
            g = t1 - t0
            if g > THR:
                lost = max(0, s1 - s0 - 1)
                rel = (t0 - tf) / 1e6
                kind = "BEFORE-FAILURE" if t1 < tf else ("outage" if lost > 0 else "stall")
                found.append((g / 1e6, lost, rel, kind))
                if kind == "BEFORE-FAILURE": n_pre += 1
                elif kind == "outage": n_out += 1
                else: n_stall += 1
        label = meta["label"]
        if found:
            for g, lost, rel, kind in found:
                print(f"  {label:26s} gap {g:8.1f} ms  lost {lost:5d}  starts {rel:9.1f} ms rel. failure  {kind}")
        else:
            print(f"  {label:26s} no gap over 10 ms")
    print(f"  totals: outage gaps {n_out}, stalls (no loss) {n_stall}, before-failure gaps {n_pre}")
