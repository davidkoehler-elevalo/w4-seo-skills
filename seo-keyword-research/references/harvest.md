# Phases 2-5: Harvest procedure in detail

Read this file completely before starting Phase 2. It assumes Phase 0 (business brief) and Phase 1 (scope map, config.md) are confirmed.

## Working directory layout

```
project-<client>/
├── config.md              # scope map, languages/countries, competitors, caps, rules
├── status.md              # running log: counts, failures, caps hit
├── raw/
│   ├── seeds.csv                      # confirmed seed table
│   ├── expansion/<seed-slug>.csv      # one file per seed, straight from Ahrefs
│   ├── rankings/own_<country>.csv
│   ├── rankings/<competitor>_<country>.csv
│   └── gsc/queries_16m.csv
├── master_raw.csv         # output of merge_dedupe.py
└── deliverables/          # XLSX files for the user
```

Keep raw exports untouched. Every transformation happens downstream so any step can be re-run.

## Phase 2 — Seed generation

Goal: 3-6 seeds per group per language. Seeds are short head terms (1-3 words) that a Matching Terms query can meaningfully expand. "hot melt gerät" is a seed; "hot melt gerät für faltschachtelklebung mit sensor" is not (that is a keyword the expansion should find, not produce).

Source seeds in this order, and record the source per seed:

1. **Own rankings per group URL.** For each group, take its URL(s) from the scope map and pull the client's ranking keywords for exactly those URLs: `Ahrefs:site-explorer-organic-keywords` with a URL filter (check `Ahrefs:doc` for the exact filter syntax in the current API version). The 5-15 highest-relevance terms per URL usually contain 2-3 good seeds.
2. **GSC queries per page.** If GSC access exists: query report filtered by page for the same URLs. GSC surfaces queries Ahrefs has no volume for, which matters because zero-volume relevance is explicitly in scope.
3. **Domain knowledge / SERP check.** Fill gaps for groups where the site does not rank yet. Mark these seeds `source: constructed` so the user looks at them hardest.

Rules:

- Seeds must be in the target language of their group row. Do not translate mechanically; "Kaschieren" and "laminating" are separate seeds sourced separately.
- Do not seed with the client's own brand or product line names (Vision, Concept) as standalone seeds; brand harvest comes in via the rankings export anyway. Product names combined with a generic ("hotmelt auftragskopf") are fine.
- Ambiguous seeds are a known failure mode. A seed like "coating" or "verpackung" alone will expand into a mostly-irrelevant universe and eat the row cap. Prefer the two-word version that carries the industrial context ("adhesive coating", "verpackung verkleben").

Deliverable: `raw/seeds.csv` with columns `group_id, group_name, language, country, seed, source`. Present it as a table in chat. **Hard stop. Do not expand unconfirmed seeds.**

## Phase 3 — Expansion via Matching Terms

**Seed packs [David, 2026-08-12]:** Submit seeds to Matching Terms in thematic packs of 2-5 similar seeds per report, never one seed alone; a pack defines the topic universe as a union, single seeds underdefine it. Exception: through the claude.ai Ahrefs MCP the server caps every response at 250 rows, so per-seed calls retrieve more there (250 per seed instead of 250 per pack); keep the pack structure for universe definition, group attribution and any UI or direct-API export, and fall back to per-seed calls only on that capped transport.

For every confirmed seed:

1. Call `Ahrefs:keywords-explorer-matching-terms` with the seed and its configured country. Take exact parameter names, available columns and pagination mechanics from `Ahrefs:doc` at run time; do not rely on remembered schemas.
2. Request at minimum: keyword, volume, keyword difficulty, CPC, and parent topic if the endpoint exposes it. No volume filter, no KD filter.
3. Paginate until exhausted or until the per-seed cap (default 5,000 rows, configurable in config.md) is reached. If the cap is hit, write the seed into status.md under "caps hit" with the total available count if the API reports one, and propose 2-3 narrower replacement seeds to the user at the end of the phase. Capped seeds mean the topic is under-harvested, not that the job is done.
4. Save each result verbatim to `raw/expansion/<seed-slug>.csv` and append `group_id, seed, country, source=matching_terms` columns.

Optional second pass (only if the user wants maximum coverage and API rows allow it): `keywords-explorer-related-terms` ("also rank for") per seed, same handling, `source=related_terms`. Ask before spending the rows; on a 100+ seed run this can double consumption.

Between seeds, keep a running total of exported rows in status.md. Check `Ahrefs:subscription-info-limits-and-usage` before starting and once mid-run on large jobs; if the remaining allowance will not cover the plan, stop and tell the user rather than delivering a half-harvest that looks complete.

## Phase 4 — Ranking harvest

### 4a. Own domain + competitors via Ahrefs

For the client domain and each of the 3 confirmed competitors, per configured country:

- `Ahrefs:site-explorer-organic-keywords`, positions 1-100, all keywords, paginated to completion. Include per row: keyword, position, volume, KD, ranking URL, and traffic if available.
- Do not filter branded terms out at this stage. Competitor brand queries get tagged and removed deterministically in pruning, where the removal is logged. Filtering here would silently distort the source counts.
- Save to `raw/rankings/<host>_<country>.csv` with `source=ahrefs_rankings, source_domain=<host>` appended.

If a competitor ranks mainly in a country you are not harvesting (visible in `site-explorer-metrics-by-country`), note it in status.md; the user may want to extend the country set.

### 4b. Google Search Console

Prefer the direct GSC tools (`google-search-console:gsc_search_analytics`) over the Ahrefs GSC mirror when both exist, because the direct export is complete and the mirror may be sampled. Check the tool's actual parameters via tool_search before calling.

- Dimension: query. Date range: last 16 months (GSC maximum). Paginate with the API's row limit and start-row mechanism until exhausted.
- Keep clicks, impressions, CTR, position per query. GSC rows with zero Ahrefs volume are exactly the long-tail the volume-agnostic policy exists for; never drop them.
- Save to `raw/gsc/queries_16m.csv` with `source=gsc`.

If no GSC access: one line in status.md and in the Uebersicht sheet. Do not substitute anything for it.

## Phase 5 — Merge and dedupe

Run `scripts/merge_dedupe.py` (see its `--help`). What it does and why:

- **Normalisation:** trim, collapse internal whitespace, lowercase, unicode NFC. Nothing else. No stemming, no umlaut folding, no plural merging: "klebstoffauftrag" and "klebstoffauftragssystem" are different queries with different SERPs, and "duese" vs "düse" are different real query strings. The script flags umlaut/ASCII pairs in a `near_dup_of` column so pruning sees them side by side, but keeps both rows.
- **Deduplication:** exact match on the normalised string. One output row per keyword.
- **Provenance aggregation:** boolean flags `in_expansion`, `in_own_rankings`, `in_gsc`, plus one flag per competitor host; `groups` and `seeds` as semicolon lists (a keyword can arrive via several seeds); per-source metrics kept in separate columns (ahrefs volume/KD/CPC, own position, best competitor position, GSC clicks/impressions). Where the same metric arrives twice with different values (e.g. volume from two seed exports), keep the maximum and flag the row.
- **Reconciliation:** prints input rows per source, unique keywords, and duplicates removed. Copy that block into status.md and the Uebersicht sheet. If the numbers do not reconcile, stop and debug; do not deliver.

Deliverables of Phase 5:

1. `master_raw.csv` (the working file for pruning; CSV because 100k+ rows in XLSX is slow to process).
2. `deliverables/<client>_keyword_harvest_raw.xlsx` following house format: sheet 1 `Uebersicht` (methodology in 5-10 lines, run date, countries, seed count, per-source row counts, caps hit, failed calls, sheet index), sheet 2 the merged master (or a note pointing to the CSV if above ~200k rows), then one sheet per raw source summarised (top rows + count), last sheet `Konfiguration` with the config.md content.

Report to the user: total unique keywords, per-source counts, list of capped seeds with proposed splits, any failed calls. Then wait for the go for Phase 6.
