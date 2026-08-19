---
name: seo-keyword-research
description: "Run the full W4 keyword research pipeline for a client domain: understand the business, build a scope map, generate seed keywords per group, expand every seed via Ahrefs Matching Terms, harvest all ranking keywords for the client and 3 competitors from Ahrefs and Google Search Console, merge into one deduplicated master list with provenance, then prune it keyword by keyword on relevance (not volume). Use whenever the user asks for keyword research, a keyword harvest, seed keywords, a keyword universe, a master keyword list, competitor keyword exports, or keyword pruning, or says 'find all keywords for this site', 'build the keyword list for [client]', 'run the keyword pipeline', 'expand these seeds', 'prune this list'. Also trigger when the user names a client domain plus competitors and wants to know what to target in search. NOT for clustering-only jobs on a pruned list (keyword-insights) or writing a single page (seo-new-page)."
---

# SEO Keyword Research Pipeline

Multi-phase pipeline that produces a complete, relevance-pruned keyword universe for one client domain. Built for B2B / industrial clients in DACH, works for any market.

The pipeline is deliberately sequenced so that cheap human corrections happen early (business brief, seeds, rubric) and expensive automated work happens after sign-off (expansion, pruning). Do not skip the checkpoints: a wrong assumption about the business poisons every phase; a wrong seed multiplies into thousands of wrong rows; a wrong rubric mis-classifies the whole list.

**Phases:**

| Phase | What | Detail file | Human checkpoint |
|---|---|---|---|
| 0 | Business discovery | `references/business-discovery.md` | Confirm business_brief.md |
| 1 | Scope map + run config | below | Confirm groups, competitors, languages |
| 2 | Seed generation per group | `references/harvest.md` | Confirm seed table BEFORE expansion |
| 3 | Seed expansion (Ahrefs Matching Terms) | `references/harvest.md` | none (report caps hit) |
| 4 | Ranking harvest (own + 3 competitors + GSC) | `references/harvest.md` | none |
| 5 | Merge and dedupe | `references/harvest.md` + `scripts/merge_dedupe.py` | Master list delivered |
| 6 | Relevance pruning | `references/pruning.md` | Rubric + calibration sample BEFORE full run |
| 7 | Clustering | `references/clustering.md` | Not yet specified. STOP and ask. |

In Claude Code with subagents available, read `references/agent-orchestration.md` before Phase 3 and Phase 6 — those phases parallelise.

## Non-negotiable rules for every phase

1. **Relevance beats volume.** Never apply a search volume floor. A keyword with zero or missing Ahrefs volume stays in the list if it is relevant. Volume is metadata for later prioritisation, not a harvest or pruning criterion.
2. **Never invent data.** Every metric in the deliverables must come from an actual tool response. If an Ahrefs, GSC or other tool call fails or returns nothing, write exactly that into the output and the status sheet. Do not fill gaps with plausible numbers or "estimated" volumes. The same applies to business facts: every statement in the business brief carries its source or the marker `[inferred]`.
3. **Provenance on every row.** Every keyword carries: which group, which seed (if expanded), which sources contained it (matching_terms / own_ahrefs / competitor domain / gsc), and the country of the metric. A keyword without provenance cannot be audited and does not ship.
4. **Nothing is silently deleted.** Pruning moves rows to a "removed" sheet with the rule or reason that removed them. The counts must reconcile: input = kept + removed, per phase.
5. **Ahrefs API discipline.** Before the first Ahrefs call of a session, call the `Ahrefs:doc` tool for the endpoints you will use (matching-terms, organic-keywords, organic-competitors) and take field names, filter syntax and pagination from there. Do not guess parameter schemas from memory. Respect the subscription: check `subscription-info-limits-and-usage` before large export runs and report estimated row consumption to the user if the harvest will be large (>50k rows).
6. **Language mechanics.** German keyword material is data, leave it untouched. But everything you write yourself (sheet names, column headers, reasons, briefs) follows house style: Swiss "ss", no em/en dashes in prose, no emojis.

## Phase 0 — Business discovery (full procedure in references/business-discovery.md)

Before anything touches Ahrefs: read the briefing material, read the website properly (products, applications, industries, cases), pull the top currently ranking terms as a demand-language sample, and write `business_brief.md` with a fixed structure: what the company sells, what it explicitly does NOT sell, who buys and in which situations, markets and languages actually served, commercial priorities, terminology map (in-house term vs market term, DE/EN pairs), open questions. Every statement sourced or marked `[inferred]`. **Hard stop until the user confirms the brief.** Groups, seeds and the pruning rubric all cite this document instead of restating the business from memory.

## Phase 1 — Scope map and run config

Collect or derive, and write into `config.md` in the project folder:

- **Client domain** (exact host to query, e.g. `www.robatech.com`) and whether to query as domain or prefix mode.
- **Groups.** The semantic buckets that structure the whole run. Derive from: the confirmed business brief, the site's own navigation (applications, products, industries), the sitemap. Each group gets a stable ID (`G01`, `G02`, ...), a name, and the site URL(s) it corresponds to. Applications, products and industries are usually separate group families; a keyword can later belong to only one group.
- **Languages and Ahrefs countries.** One country code per language (e.g. DE keywords → country `de`, EN keywords → `us` or `gb`). This is a real decision, not a default: volumes differ heavily between `de`, `ch`, `at`. If the briefing does not fix it, ask one question and wait.
- **Competitors.** Exactly 3 for the harvest. Propose candidates from `Ahrefs:site-explorer-organic-competitors` for the client domain, but let the user confirm or replace them. SEO competitors and business competitors are not the same thing; say which type each candidate is.
- **GSC property** name if Search Console access exists (via the google-search-console tools or the Ahrefs GSC endpoints).

Show the scope map as a table and get explicit confirmation before Phase 2. This is a hard checkpoint.

## Phases 2-5 — Harvest (summary; full procedure in references/harvest.md)

1. **Seeds:** 3-6 seeds per group per language. Source them in this order: the client's already-ranking keywords for the group's URLs (Ahrefs organic-keywords filtered by URL, plus GSC queries per page), then the terminology map from the business brief, then SERP knowledge. Seeds are short head terms (1-3 words). Present the full seed table (group, seed, language, source of the seed) and stop for confirmation.
2. **Expansion:** run every confirmed seed through Ahrefs Matching Terms in its configured country. Export all rows up to the per-seed cap (default 5,000). If a seed hits the cap, flag it as too broad in the status sheet and propose splitting it; do not silently truncate the topic.
3. **Ranking harvest:** full organic-keywords export (positions 1-100) for the client domain and each of the 3 competitors, per configured country, paginated to completion. Full GSC query export (16 months, paginated). Tag every row with its source.
4. **Merge:** run `scripts/merge_dedupe.py`. It normalises (trim, lowercase, whitespace, unicode NFC), deduplicates exact matches, aggregates provenance flags and per-source metrics into one row per keyword. It never merges umlaut/ASCII variants ("förderband" vs "foerderband" are different queries); it flags them as near-duplicate pairs instead.

Deliverable of Phase 5: `master_raw.csv` plus an XLSX with sheet 1 "Uebersicht" (methodology, row counts per source, caps hit, failed calls, sheet index), then the master sheet, then one raw sheet per source. Expect 40k-150k rows; that is fine.

## Phase 6 — Pruning (summary; full procedure in references/pruning.md)

Two passes, in this order:

1. **Deterministic pre-prune.** Rule-based removals only for unambiguous junk: competitor brand terms and their typos, job/career queries, wrong-language rows, adult/irrelevant boilerplate. Every rule is listed in the config, every removed row lands on the removed sheet with its rule ID. When in doubt, a rule does not fire; the LLM pass decides.
2. **LLM relevance pass, keyword by keyword.** Write a project-specific rubric first (sections 1-2 and the out-of-scope section come from the confirmed business brief; keep/kill examples from the actual list), get it and a ~100-row calibration sample confirmed by the user, then classify every remaining keyword as `relevant` / `borderline` / `irrelevant` with a short reason and a proposed group. Volume is not an argument in either direction. Borderline rows are kept and flagged, never dropped.

Deliverable: pruned master XLSX (Uebersicht, kept list, borderline list, removed list with reasons, rubric sheet). Target size is whatever relevance produces; 2,000-3,000 is typical, but the number is an outcome, not a goal.

## Phase 7 — Clustering

Not yet specified by the user. Read `references/clustering.md` for the current state, then stop and ask how they want to cluster before doing anything. The `keyword-insights` skill (SERP-based clustering API) is the likely vehicle but this is not confirmed.

## Failure and status reporting

Maintain `status.md` in the project folder throughout the run: per phase, per tool call batch, row counts, failures, retries, caps hit. When reporting to the user, lead with what is missing or broke, not with what worked.
