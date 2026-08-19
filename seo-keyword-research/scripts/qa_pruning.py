#!/usr/bin/env python3
"""QA checks on the merged pruning result.

Usage: python qa_pruning.py --pruned pruned.csv [--audit 200]

Checks:
1. Near-duplicate consistency: rows linked via near_dup_of must share a class.
2. Class distribution per group (spots empty or suspicious groups).
3. Emits a stratified audit sample (default 200 rows across the three classes)
   to audit_sample.csv for a fresh human/model review pass.
"""
import argparse
import csv
import random
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pruned", required=True)
    ap.add_argument("--audit", type=int, default=200)
    ap.add_argument("--audit-out", default="audit_sample.csv")
    args = ap.parse_args()

    with open(args.pruned, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    by_kw = {r["keyword"]: r for r in rows}

    conflicts = []
    for r in rows:
        for other in filter(None, (x.strip() for x in r.get("near_dup_of", "").split(";"))):
            o = by_kw.get(other)
            if o and o["class"] and r["class"] and o["class"] != r["class"] \
               and r["keyword"] < other:
                conflicts.append((r["keyword"], r["class"], other, o["class"]))
    print(f"=== NEAR-DUP CONSISTENCY: {len(conflicts)} conflicts ===")
    for a, ca, b, cb in conflicts[:50]:
        print(f"  {a} [{ca}]  vs  {b} [{cb}]")
    if len(conflicts) > 50:
        print(f"  ... and {len(conflicts) - 50} more")

    print("\n=== CLASS COUNTS PER GROUP ===")
    per_group = defaultdict(lambda: defaultdict(int))
    for r in rows:
        gid = r.get("class_group_id") or r.get("groups") or "(none)"
        per_group[gid][r.get("class") or "(unclassified)"] += 1
    for gid in sorted(per_group):
        c = per_group[gid]
        print(f"  {gid}: relevant={c.get('relevant', 0)} "
              f"borderline={c.get('borderline', 0)} irrelevant={c.get('irrelevant', 0)} "
              f"unclassified={c.get('(unclassified)', 0)}")

    by_class = defaultdict(list)
    for r in rows:
        if r.get("class"):
            by_class[r["class"]].append(r)
    per_class = max(1, args.audit // max(1, len(by_class)))
    sample = []
    for cls, rs in by_class.items():
        sample += random.sample(rs, min(per_class, len(rs)))
    with open(args.audit_out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(sample)
    print(f"\nAudit sample: {len(sample)} rows -> {args.audit_out}")
    print("Review the sample against the rubric in a fresh pass. Disagreement above "
          "~5% on relevant/irrelevant means a systematic problem: find the pattern, "
          "fix rubric or chunks, re-run affected material.")


if __name__ == "__main__":
    main()
