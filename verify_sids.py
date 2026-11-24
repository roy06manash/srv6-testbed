#!/usr/bin/env python3
"""Verify SID traversal from per-link pcaps and measure header overhead.

Usage: python3 verify_sids.py results      (reads results/pcaps/<mode>/<ns>_<if>.pcap)
Writes results/sid_traversal.md; exit status 1 if any check fails.
"""
import sys
from collections import Counter
from pathlib import Path

from pcap import data_packet, parse_frame, read_pcap

H2, PORT = "2001:db8:a5::2", 9000
PLAIN = "plain"
# capture point -> allowed (outer DA, segments-left, #SIDs) tuples, or PLAIN (no SRH, DA = h2)
SRV6_EXPECT = {
    "r1_toh1": [PLAIN],
    "r1_to2": [("fc00:2::1", 1, 2)],
    "r2_to5": [("fc00:5::d6", 0, 2)],
    "r1_to3": [("fc00:3::1", 2, 3)],
    "r3_to4": [("fc00:4::1", 1, 3)],
    "r4_to5": [("fc00:5::d6", 0, 3)],
    "r5_toh2": [PLAIN],
}
IPV6_EXPECT = {k: [PLAIN] for k in SRV6_EXPECT}
EXPECT = {"srv6": SRV6_EXPECT, "ipv6": IPV6_EXPECT}


def observe(pcap_path):
    seen, lens = Counter(), []
    for _, orig, frame in read_pcap(pcap_path):
        info = parse_frame(frame)
        if not data_packet(info, H2, PORT):
            continue
        key = PLAIN if info["srh"] is None and info["inner"] is None and info["dst"] == H2 else (
            (info["dst"], info["srh"]["sl"], info["srh"]["nseg"]) if info["srh"] else ("other",))
        seen[key] += 1
        lens.append(orig)
    return seen, lens


def main():
    res = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
    lines, ok, mean_len = ["# SID traversal verification", ""], True, {}
    for mode in ("ipv6", "srv6"):
        d = res / "pcaps" / mode
        if not d.is_dir():
            continue
        lines += [f"## Mode `{mode}`", "",
                  "| Capture point | Observed (outer DA, SL, #SIDs) | Packets | Mean frame B | Verdict |",
                  "|---|---|---|---|---|"]
        for point, allowed in EXPECT[mode].items():
            f = d / f"{point}.pcap"
            if not f.exists():
                lines.append(f"| {point} | (no capture) | 0 | - | FAIL |")
                ok = False
                continue
            seen, lens = observe(f)
            good = bool(seen) and all(k in allowed for k in seen)
            ok &= good
            mean_len[(mode, point)] = sum(lens) / len(lens) if lens else None
            obs = "; ".join(f"{k}: {v}" for k, v in seen.items()) or "none"
            m = f"{mean_len[(mode, point)]:.1f}" if lens else "-"
            lines.append(f"| {point} | {obs} | {sum(seen.values())} | {m} | {'PASS' if good else 'FAIL'} |")
        lines.append("")

    lines += ["## Header overhead (measured vs RFC 8754 expectation)", "",
              "| Link | Plain IPv6 frame B | SRv6 frame B | Measured overhead B | Expected B |",
              "|---|---|---|---|---|"]
    for point, n in (("r1_to2", 2), ("r1_to3", 3)):
        p, s = mean_len.get(("ipv6", point)), mean_len.get(("srv6", point))
        if p and s:
            exp = 40 + 8 + 16 * n
            meas = s - p
            ok &= abs(meas - exp) < 0.5
            lines.append(f"| {point} ({n} SIDs) | {p:.1f} | {s:.1f} | {meas:.1f} | {exp} |")
        else:
            lines.append(f"| {point} ({n} SIDs) | - | - | n/a (need both modes captured) | {40 + 8 + 16 * n} |")
    lines += ["", f"**Overall: {'PASS' if ok else 'FAIL'}**", ""]
    (res / "sid_traversal.md").write_text("\n".join(lines))
    print("\n".join(lines))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
