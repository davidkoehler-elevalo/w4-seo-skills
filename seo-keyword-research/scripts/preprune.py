#!/usr/bin/env python3
"""Deterministic pre-prune pass. Conservative by design: when in doubt, keep.

Usage:
  python preprune.py --master master_raw.csv --rules rules.csv \
      --kept kept_prepass.csv --removed removed_prepass.csv [--sample 20]

rules.csv columns: rule_id,pattern,match_type,note
  match_type: 'word'   -> pattern must appear as a whole word (regex \\b)
              'regex'  -> pattern is a raw regex
              'exact'  -> keyword equals pattern

Prints per-rule counts and a random sample of matches per rule for human review.
Rows removed by any rule land in --removed with the first matching rule_id.
Counts always reconcile: kept + removed == input.
"""
import argparse
import csv
import random
import re
import sys
from collections import defaultdict


def load_rules(path):
    rules = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            pat = r["pattern"].strip()
            mt = r.get("match_type", "word").strip()
            if mt == "word":
                rx = re.compile(r"\b" + re.escape(pat) + r"\b", re.IGNORECASE)
            elif mt == "regex":
                rx = re.compile(pat, re.IGNORECASE)
            elif mt == "exact":
                rx = re.compile(r"^" + re.escape(pat) + r"$", re.IGNORECASE)
            else:
                sys.exit(f"Unknown match_type '{mt}' for rule {r['rule_id']}")
            rules.append((r["rule_id"].strip(), rx, r.get("note", "")))
    return rules


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--master", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--kept", required=True)
    ap.add_argument("--removed", required=True)
    ap.add_argument("--sample", type=int, default=20)
    args = ap.parse_args()

    rules = load_rules(args.rules)
    hits = defaultdict(list)
    n_in = n_kept = n_removed = 0

    with open(args.master, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        with open(args.kept, "w", encoding="utf-8", newline="") as fk, \
             open(args.removed, "w", encoding="utf-8", newline="") as fr:
            wk = csv.DictWriter(fk, fieldnames=fields)
            wr = csv.DictWriter(fr, fieldnames=fields + ["rule_id"])
            wk.writeheader()
            wr.writeheader()
            for row in reader:
                n_in += 1
                kw = row["keyword"]
                matched = None
                for rid, rx, _ in rules:
                    if rx.search(kw):
                        matched = rid
                        break
                if matched:
                    n_removed += 1
                    hits[matched].append(kw)
                    row["rule_id"] = matched
                    wr.writerow(row)
                else:
                    n_kept += 1
                    wk.writerow(row)

    print("=== PRE-PRUNE ===")
    print(f"Input: {n_in}  Kept: {n_kept}  Removed: {n_removed}")
    assert n_in == n_kept + n_removed, "Counts do not reconcile"
    for rid, _, note in rules:
        kws = hits.get(rid, [])
        print(f"\nRule {rid} ({note}): {len(kws)} matches")
        for kw in random.sample(kws, min(args.sample, len(kws))):
            print(f"  {kw}")
    print("\nReview the samples above. A rule that caught a relevant keyword "
          "gets narrowed and the pass re-run before anything continues.")


if __name__ == "__main__":
    main()
