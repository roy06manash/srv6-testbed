#!/usr/bin/env python3
"""Compute loss, interruption time and repair delays per run; summarise per mode.

Usage: python3 analyze.py results   -> results/runs.csv, results/summary.md
Definitions (all times CLOCK_MONOTONIC, same host):
  lost         = packets sent - unique packets received
  interruption = largest gap between consecutive arrivals - nominal send interval
  detect       = detector decision time - failure-applied time
  repair       = repair-command completion - detector decision
  recovery     = first arrival after the outage - failure-applied time
"""
import csv, json, math, statistics, sys
from pathlib import Path

METRICS = [("lost", "Lost packets"), ("loss_pct", "Loss (%)"), ("interruption_ms", "Interruption (ms)"),
           ("detect_ms", "Detection delay (ms)"), ("repair_ms", "Repair command (ms)"),
           ("recovery_ms", "Failure -> traffic restored (ms)")]


def compute(m, res):
    first = {}
    with open(res / m["recv_csv"]) as f:
        for r in csv.DictReader(f):
            first.setdefault(int(r["seq"]), int(r["recv_ns"]))
    sent = m["sender"]["sent"]
    arr = sorted(first.values())
    interval_ms = 1000.0 / m["pps"]
    lost = sent - len(first)
    d, err = m["detector"], []
    out = {"mode": m["mode"], "run": m["label"], "sent": sent, "received": len(first),
           "lost": lost, "loss_pct": 100.0 * lost / sent if sent else float("nan")}
    if d is None:
        pass  # repaired by a routing protocol: no detector or scripted switch in this mode
    elif d["t_detect_ns"] is None:
        err.append("failure not detected")
    else:
        out["detect_ms"] = (d["t_detect_ns"] - m["t_fail_applied_ns"]) / 1e6
        out["repair_ms"] = (d["t_repair_done_ns"] - d["t_detect_ns"]) / 1e6
        if out["detect_ms"] <= 0:
            err.append("detected before failure (false positive)")
        if d["repair_rc"] != 0:
            err.append("repair command failed")
    if len(arr) >= 2:
        gap, i = max((arr[k + 1] - arr[k], k) for k in range(len(arr) - 1))
        out["interruption_ms"] = max(0.0, gap / 1e6 - interval_ms) if lost > 0 else 0.0
        out["recovery_ms"] = (arr[i + 1] - m["t_fail_applied_ns"]) / 1e6
        if arr[i + 1] < m["t_fail_applied_ns"]:
            err.append("largest gap precedes failure")
    else:
        err.append("too few packets received")
    out["error"] = "; ".join(err)
    return out


def stats(v):
    v = sorted(x for x in v if x is not None and not math.isnan(x))
    if not v:
        return None
    return {"n": len(v), "mean": statistics.fmean(v), "median": statistics.median(v),
            "stdev": statistics.stdev(v) if len(v) > 1 else 0.0, "min": v[0],
            "p95": v[max(0, math.ceil(0.95 * len(v)) - 1)], "max": v[-1]}


def main():
    res = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    runs = []
    for p in sorted((res / "raw").glob("*.meta.json")):
        m = json.loads(p.read_text())
        if not m.get("verify"):
            runs.append(compute(m, res))
    if not runs:
        sys.exit("no measured runs found in %s/raw" % res)

    cols = ["mode", "run", "sent", "received", "lost", "loss_pct", "interruption_ms",
            "detect_ms", "repair_ms", "recovery_ms", "error"]
    with open(res / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(runs)

    md = ["# Results summary", ""]
    bad = [r for r in runs if r["error"]]
    for mode in sorted({r["mode"] for r in runs}):
        rs = [r for r in runs if r["mode"] == mode and not r["error"]]
        md += [f"## Mode `{mode}` ({len(rs)} valid runs of {sum(r['mode'] == mode for r in runs)})", "",
               "| Metric | n | mean | median | stdev | min | p95 | max |", "|---|---|---|---|---|---|---|---|"]
        for key, name in METRICS:
            s = stats([r.get(key) for r in rs])
            if s:
                md.append(f"| {name} | {s['n']} | {s['mean']:.2f} | {s['median']:.2f} | {s['stdev']:.2f} "
                          f"| {s['min']:.2f} | {s['p95']:.2f} | {s['max']:.2f} |")
        md.append("")
    if bad:
        md += ["## Excluded runs", ""] + [f"- {r['run']}: {r['error']}" for r in bad] + [""]
    md += ["## Header overhead (RFC 8754, theoretical)", "",
           "| Path | SIDs | Outer IPv6 | SRH | Total overhead |", "|---|---|---|---|---|",
           "| A (primary) | 2 | 40 B | 8 + 32 B | 80 B |", "| B (backup) | 3 | 40 B | 8 + 48 B | 96 B |", "",
           "Measured overhead comes from `verify_sids.py` (see sid_traversal.md).", ""]
    (res / "summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
