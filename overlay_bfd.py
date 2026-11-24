#!/usr/bin/env python3
"""Silent-failure experiment (netem loss on r1-r2) with real BFD registered with OSPFv3.
Adds overlay_off (plain IPv6 over OSPFv3). Output: results_bfd/
Usage (root, after scripts/overlay_up.sh and scripts/bfd_up.sh):  sudo python3 overlay_bfd.py --runs 10"""
import sys
import overlay_experiment as oe

oe.MODES["overlay_off"] = ("off", None)
if "--out" not in sys.argv:
    sys.argv += ["--out", str(oe.ROOT / "results_bfd")]
oe.main()
