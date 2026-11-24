#!/usr/bin/env python3
"""One-off patch: let analyze.py handle runs repaired by a routing protocol (no detector)."""
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "analyze.py"
src = p.read_text()
old = '''    if d["t_detect_ns"] is None:
        err.append("failure not detected")
    else:
'''
new = '''    if d is None:
        pass  # repaired by a routing protocol: no detector or scripted switch in this mode
    elif d["t_detect_ns"] is None:
        err.append("failure not detected")
    else:
'''
assert src.count(old) == 1, "expected block not found; analyze.py differs from what I sent"
p.write_text(src.replace(old, new))
print("patched analyze.py")
