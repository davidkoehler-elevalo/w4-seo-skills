#!/usr/bin/env python3
"""Merge all harvest exports into one deduplicated master list with provenance.

Usage:
  python merge_dedupe.py --project <project-dir> [--out master_raw.csv]

Expects the layout from references/harvest.md:
  <project>/raw/expansion/*.csv     appended cols: group_id, seed, country, source
  <project>/raw/rankings/*.csv      appended cols: source, source_domain, country
  <project>/raw/gsc/*.csv           appended col:  source

Handles Ahrefs UTF-16 tab-separated exports and UTF-8 comma/semicolon CSVs.
Normalisation: strip, collapse whitespace, lowercase, unicode NFC. Nothing else.
Umlaut/ASCII variants are flagged (near_dup_of), never merged.
Prints a reconciliation block; copy it into status.md and the Uebersicht sheet.
"""
import argparse
import csv
import glob
import os
import sys
import unicodedata
from collections import defaultdict

KEYWORD_HEADERS = {"keyword", "keywords", "search query", "query", "term", "top queries"}
VOLUME_HEADERS = {"volume", "search volume", "avg. monthly searches", "sv"}
KD_HEADERS = {"kd", "difficulty", "keyword difficulty"}
CPC_HEADERS = {"cpc"}
POSITION_HEADERS = {"position", "current position", "pos", "average position"}
URL_HEADERS = {"current url", "url", "ranking url", "page"}
CLICKS_HEADERS = {"clicks"}
IMPR_HEADERS = {"impressions"}
PARENT_HEADERS = {"parent topic", "parent keyword"}

UMLAUT_FOLD = str.maketrans({"ä": "a", "ö": "o", "ü": "u"})


def normalise(kw: str) -> str:
    kw = unicodedata.normalize("NFC", kw).strip().lower()
    return " ".join(kw.split())


def fold_key(kw: str) -> str:
    """Key for near-duplicate detection only. ae/oe/ue and ä/ö/ü collapse; ss==ss already."""
    k = kw.translate(UMLAUT_FOLD)
    return k.replace("ae", "a").replace("oe", "o").replace("ue", "u")


def sniff_open(path):
    """Return (rows, header) for UTF-16 or UTF-8 files with tab/comma/semicolon separators."""
    with open(path, "rb") as fb:
        head = fb.read(4)
    if head.startswith(b"\xff\xfe") or head.startswith(b"\xfe\xff"):
        enc = "utf-16"
    else:
        enc = "utf-8-sig"
    with open(path, encoding=enc, newline="") as f:
        sample = f.read(8192)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        except csv.Error:
            dialect = csv.excel_tab if "\t" in sample else csv.excel
        reader = csv.reader(f, dialect)
        rows = list(reader)
    if not rows:
        return [], []
    header = [h.strip().lower() for h in rows[0]]
    return rows[1:], header


def col(header, names):
    for i, h in enumerate(header):
        if h in names:
            return i
    return None


def to_float(v):
    if v is None:
        return None
    v = str(v).strip().replace(",", ".")
    if v in ("", "-", "n/a", "na", "null"):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    proj = args.project
    out_path = args.out or os.path.join(proj, "master_raw.csv")

    files = []
    for sub in ("expansion", "rankings", "gsc"):
        files += sorted(glob.glob(os.path.join(proj, "raw", sub, "*.csv")))
    if not files:
        sys.exit(f"No input files found under {proj}/raw/. Nothing to merge.")

    # keyword -> aggregate dict
    agg = {}
    source_counts = defaultdict(int)
    total_rows = 0

    for path in files:
        rows, header = sniff_open(path)
        if not header:
            print(f"WARNING: empty file skipped: {path}", file=sys.stderr)
            continue
        kw_i = col(header, KEYWORD_HEADERS)
        if kw_i is None:
            print(f"WARNING: no keyword column in {path} (header: {header}); skipped",
                  file=sys.stderr)
            continue
        idx = {
            "volume": col(header, VOLUME_HEADERS), "kd": col(header, KD_HEADERS),
            "cpc": col(header, CPC_HEADERS), "position": col(header, POSITION_HEADERS),
            "url": col(header, URL_HEADERS), "clicks": col(header, CLICKS_HEADERS),
            "impressions": col(header, IMPR_HEADERS), "parent": col(header, PARENT_HEADERS),
            "group_id": col(header, {"group_id"}), "seed": col(header, {"seed"}),
            "country": col(header, {"country"}), "source": col(header, {"source"}),
            "source_domain": col(header, {"source_domain"}),
        }

        def get(r, key):
            i = idx[key]
            return r[i].strip() if i is not None and i < len(r) and r[i] is not None else ""

        fallback_source = os.path.basename(os.path.dirname(path))
        for r in rows:
            if kw_i >= len(r):
                continue
            kw = normalise(r[kw_i])
            if not kw:
                continue
            total_rows += 1
            source = get(r, "source") or fallback_source
            sdom = get(r, "source_domain")
            skey = f"{source}:{sdom}" if sdom else source
            source_counts[skey] += 1

            a = agg.setdefault(kw, {
                "keyword": kw, "sources": set(), "groups": set(), "seeds": set(),
                "countries": set(), "volume": None, "kd": None, "cpc": None,
                "own_position": None, "own_url": "", "comp_best_position": None,
                "comp_best_domain": "", "gsc_clicks": 0.0, "gsc_impressions": 0.0,
                "parent_topic": "", "volume_conflict": False,
            })
            a["sources"].add(skey)
            if get(r, "group_id"):
                a["groups"].add(get(r, "group_id"))
            if get(r, "seed"):
                a["seeds"].add(get(r, "seed"))
            if get(r, "country"):
                a["countries"].add(get(r, "country"))
            if get(r, "parent") and not a["parent_topic"]:
                a["parent_topic"] = get(r, "parent")

            vol = to_float(get(r, "volume"))
            if vol is not None:
                if a["volume"] is not None and vol != a["volume"]:
                    a["volume_conflict"] = True
                a["volume"] = max(a["volume"], vol) if a["volume"] is not None else vol
            kd = to_float(get(r, "kd"))
            if kd is not None:
                a["kd"] = max(a["kd"], kd) if a["kd"] is not None else kd
            cpc = to_float(get(r, "cpc"))
            if cpc is not None:
                a["cpc"] = max(a["cpc"], cpc) if a["cpc"] is not None else cpc

            pos = to_float(get(r, "position"))
            if source == "gsc":
                a["gsc_clicks"] += to_float(get(r, "clicks")) or 0.0
                a["gsc_impressions"] += to_float(get(r, "impressions")) or 0.0
            elif pos is not None:
                if sdom:  # competitor or own tagged by domain
                    is_own = source in ("own", "ahrefs_rankings_own") or "own" in os.path.basename(path)
                else:
                    is_own = "own" in os.path.basename(path)
                if is_own:
                    if a["own_position"] is None or pos < a["own_position"]:
                        a["own_position"] = pos
                        a["own_url"] = get(r, "url")
                elif sdom:
                    if a["comp_best_position"] is None or pos < a["comp_best_position"]:
                        a["comp_best_position"] = pos
                        a["comp_best_domain"] = sdom

    # near-duplicate flagging via folded key
    fold_map = defaultdict(list)
    for kw in agg:
        fold_map[fold_key(kw)].append(kw)
    for kws in fold_map.values():
        if len(kws) > 1:
            for kw in kws:
                agg[kw]["near_dup_of"] = "; ".join(k for k in sorted(kws) if k != kw)

    all_sources = sorted({s for a in agg.values() for s in a["sources"]})
    fields = (["keyword", "groups", "seeds", "countries", "volume", "kd", "cpc",
               "own_position", "own_url", "comp_best_position", "comp_best_domain",
               "gsc_clicks", "gsc_impressions", "parent_topic", "near_dup_of",
               "volume_conflict"] + [f"in_{s}" for s in all_sources])

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for kw in sorted(agg):
            a = agg[kw]
            row = {
                "keyword": kw,
                "groups": "; ".join(sorted(a["groups"])),
                "seeds": "; ".join(sorted(a["seeds"])),
                "countries": "; ".join(sorted(a["countries"])),
                "volume": a["volume"], "kd": a["kd"], "cpc": a["cpc"],
                "own_position": a["own_position"], "own_url": a["own_url"],
                "comp_best_position": a["comp_best_position"],
                "comp_best_domain": a["comp_best_domain"],
                "gsc_clicks": a["gsc_clicks"] or "", "gsc_impressions": a["gsc_impressions"] or "",
                "parent_topic": a["parent_topic"],
                "near_dup_of": a.get("near_dup_of", ""),
                "volume_conflict": "yes" if a["volume_conflict"] else "",
            }
            for s in all_sources:
                row[f"in_{s}"] = "1" if s in a["sources"] else ""
            w.writerow(row)

    print("=== RECONCILIATION ===")
    print(f"Input files:        {len(files)}")
    print(f"Input rows total:   {total_rows}")
    for s in sorted(source_counts):
        print(f"  {s}: {source_counts[s]}")
    print(f"Unique keywords:    {len(agg)}")
    print(f"Duplicates merged:  {total_rows - len(agg)}")
    near = sum(1 for a in agg.values() if a.get("near_dup_of"))
    print(f"Near-dup flagged:   {near}")
    print(f"Output:             {out_path}")


if __name__ == "__main__":
    main()
