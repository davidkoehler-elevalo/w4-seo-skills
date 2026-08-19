#!/usr/bin/env python3
"""Split the pre-pruned list into classification chunks, validate returned chunks,
and merge results.

Split:     python chunk_for_pruning.py split --input kept_prepass.csv \
               --outdir chunks --size 300
Validate:  python chunk_for_pruning.py validate --chunk chunks/chunk_001.csv \
               --result chunks_out/chunk_001.tsv
Merge:     python chunk_for_pruning.py merge --input kept_prepass.csv \
               --results chunks_out --out pruned.csv

Result TSV format per line (no header):
  keyword<TAB>class<TAB>group_id<TAB>reason
class in {relevant, borderline, irrelevant}. Validation is strict on purpose:
a chunk that fails is re-run, never patched by hand.
"""
import argparse
import csv
import glob
import os
import sys

LEGAL = {"relevant", "borderline", "irrelevant"}


def read_master(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def cmd_split(a):
    fields, rows = read_master(a.input)
    os.makedirs(a.outdir, exist_ok=True)
    n = 0
    for i in range(0, len(rows), a.size):
        n += 1
        path = os.path.join(a.outdir, f"chunk_{n:03d}.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["keyword", "groups", "seeds"])
            w.writeheader()
            for r in rows[i:i + a.size]:
                w.writerow({k: r.get(k, "") for k in ("keyword", "groups", "seeds")})
    print(f"{len(rows)} keywords -> {n} chunks of <= {a.size} in {a.outdir}/")


def read_result(path):
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for ln, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                return None, f"line {ln}: expected 4 tab-separated fields, got {len(parts)}"
            kw, cls, gid, reason = parts[0].strip().lower(), parts[1].strip().lower(), \
                parts[2].strip(), "\t".join(parts[3:]).strip()
            if cls not in LEGAL:
                return None, f"line {ln}: illegal class '{cls}'"
            if kw in out:
                return None, f"line {ln}: duplicate keyword '{kw}'"
            out[kw] = (cls, gid, reason)
    return out, None


def cmd_validate(a):
    _, rows = read_master(a.chunk)
    expected = {r["keyword"].strip().lower() for r in rows}
    result, err = read_result(a.result)
    if err:
        print(f"FAIL {a.result}: {err}")
        sys.exit(1)
    missing = expected - set(result)
    extra = set(result) - expected
    if missing or extra:
        print(f"FAIL {a.result}: missing={sorted(missing)[:5]}"
              f"{'...' if len(missing) > 5 else ''} extra={sorted(extra)[:5]}"
              f"{'...' if len(extra) > 5 else ''}")
        sys.exit(1)
    print(f"OK {a.result}: {len(result)} rows")


def cmd_merge(a):
    fields, rows = read_master(a.input)
    results = {}
    for path in sorted(glob.glob(os.path.join(a.results, "*.tsv"))):
        res, err = read_result(path)
        if err:
            sys.exit(f"Refusing to merge, invalid chunk {path}: {err}")
        overlap = set(res) & set(results)
        if overlap:
            sys.exit(f"Refusing to merge, keyword(s) in two chunks: {sorted(overlap)[:5]}")
        results.update(res)
    out_fields = fields + ["class", "class_group_id", "class_reason"]
    unclassified = 0
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for r in rows:
            kw = r["keyword"].strip().lower()
            if kw in results:
                cls, gid, reason = results[kw]
            else:
                cls, gid, reason = "", "", ""
                unclassified += 1
            r.update({"class": cls, "class_group_id": gid, "class_reason": reason})
            w.writerow(r)
    counts = {}
    for cls, _, _ in results.values():
        counts[cls] = counts.get(cls, 0) + 1
    print(f"Merged {len(results)} classifications over {len(rows)} keywords -> {a.out}")
    print(f"relevant={counts.get('relevant', 0)} borderline={counts.get('borderline', 0)} "
          f"irrelevant={counts.get('irrelevant', 0)} UNCLASSIFIED={unclassified}")
    if unclassified:
        print("UNCLASSIFIED rows exist. Missing chunks must be run before delivery.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("--input", required=True)
    s.add_argument("--outdir", required=True)
    s.add_argument("--size", type=int, default=300)
    v = sub.add_parser("validate")
    v.add_argument("--chunk", required=True)
    v.add_argument("--result", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--input", required=True)
    m.add_argument("--results", required=True)
    m.add_argument("--out", required=True)
    a = ap.parse_args()
    {"split": cmd_split, "validate": cmd_validate, "merge": cmd_merge}[a.cmd](a)


if __name__ == "__main__":
    main()
