import csv, json, sys
from pathlib import Path
for mp in sorted(Path(sys.argv[1], "raw").glob("*.meta.json")):
    m = json.loads(mp.read_text()); sent = m["sender"]["sent"]
    rows = sorted((int(r["seq"]), int(r["recv_ns"])) for r in csv.DictReader(open(Path(sys.argv[1], m["recv_csv"]))))
    seqs = [s for s, _ in rows]; lost = sent - len(set(seqs))
    if lost > 20:
        tf = m["t_fail_applied_ns"]
        t_of = dict(rows)
        print(f"{m['label']}: lost {lost}, first seq {seqs[0]}, last seq {seqs[-1]} of {sent-1}, "
              f"last arrival {(rows[-1][1]-tf)/1e6:.0f} ms after failure")
