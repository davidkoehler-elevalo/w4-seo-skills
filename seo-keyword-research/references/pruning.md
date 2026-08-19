# Phase 6: Relevance pruning in detail

Input: `master_raw.csv` from Phase 5. Output: a kept/borderline/removed split where every removed row carries a reason.

Governing rule, repeated because it is the one that gets violated: **volume is not a pruning criterion.** Not as a floor, not as a tiebreaker, not as a "well, it's borderline AND zero volume". Relevance only. Volume re-enters at prioritisation after clustering, not here.

## Pass 1 — Deterministic pre-prune

Purpose: remove only what needs no judgement, so the LLM pass spends effort where judgement is needed. Conservative by design; a rule that could catch a relevant keyword does not get written.

Build the rule set per project into config.md. Standard rule families:

| Rule ID | Family | Example patterns | Notes |
|---|---|---|---|
| R1 | Competitor brand | competitor names, product line names, obvious typos of them | From the confirmed competitor list plus their main product brands. A query like "nordson vs robatech" is NOT removed: comparison queries are relevant. The rule only fires on queries that are purely navigational to the competitor. |
| R2 | Jobs/careers | "jobs", "karriere", "gehalt", "ausbildung", "praktikum", "stellenangebote" | Fires only when combined with nothing product-relevant. |
| R3 | Wrong language | script detection (cyrillic, CJK), unambiguous other-language function words | Only unambiguous cases. "gluing machine" in a DE list stays; the LLM decides. |
| R4 | Consumer/DIY mismatch | project-specific; for industrial adhesive systems e.g. "bastelkleber", "sekundenkleber entfernen haut" | Write these from actually reading the list, not speculatively. |
| R5 | Adult/junk | standard patterns | |
| R7-R9 | Query-Artefakte | GSC operator junk (site:, quote/paren fragments, symbol-only strings), digits-only rows (phone numbers), URLs/bare domains as query | Regex-only, ordered BEFORE brand rules (first match wins). Never match a lone trailing "?": real question queries are often relevant. Python re has no POSIX classes; use \W not [[:punct:]]. [David + run findings, 2026-08-12] |

Implementation: `scripts/preprune.py` applies the rules, writes matched rows to `removed_prepass.csv` with `rule_id`, and prints per-rule counts. Read the per-rule sample output (20 random matches per rule) yourself before accepting the pass; a rule that matched something it should not have gets narrowed and the pass re-runs.

## Pass 2 — LLM relevance classification

### Step 1: Write the rubric

One page, project-specific, saved as `rubric.md`. Structure:

1. **What the client sells, in two sentences.** Taken from the confirmed business_brief.md, not restated from memory. Concrete: machines, systems, service, for whom.
2. **Who searches and buys.** Roles, company types, purchase context.
3. **Relevant means:** a searcher with this query could plausibly be served by a page this client should own. Includes: product/solution queries, application and process queries ("wellpappe verkleben"), problem queries the product solves, comparison queries including competitor comparisons, standards/specs relevant to the product space, informational queries a buyer researches pre-purchase.
4. **Irrelevant means:** everything in the brief's out-of-scope section, consumer/DIY intent, other industries sharing a homonym, academic-only queries with no commercial adjacency, pure navigational queries to other companies, geography-mismatched queries.
5. **Keep/kill examples: at least 10 of each, taken from the actual master list**, with one-line reasons. This anchors the classifier far better than abstract criteria.
6. **Borderline definition:** plausible arguments both ways, or intent unclear from the string alone. Borderline is a real class, not a dumping ground; if more than ~15% of a calibration chunk lands there, the rubric is too vague and gets revised.

Present the rubric to the user. **Hard stop until confirmed.**

### Step 2: Calibration

Classify one stratified sample of ~100 keywords (drawn across groups and sources, including zero-volume rows) using the rubric. Show the user the full sample with classifications and reasons. Adjust the rubric from their corrections. Only then run the full list. Every rubric change after calibration invalidates prior chunks; if the user changes the rubric mid-run, re-run affected chunks rather than living with a split-brain list.

### Step 3: Full classification run

- Chunk the remaining list into batches of 200-400 keywords (`scripts/chunk_for_pruning.py`). Larger chunks degrade per-row attention; smaller chunks waste context on the repeated rubric.
- Every chunk prompt contains: the full rubric verbatim, the group list, and the instruction to return one line per input keyword as `keyword<TAB>class<TAB>group_id<TAB>reason` with class in {relevant, borderline, irrelevant} and reason under 15 words. No summarising, no skipping, no re-ordering.
- Validate every returned chunk mechanically: row count equals input count, every keyword from the input present exactly once, class values legal. A chunk that fails validation is re-run, not patched by hand.
- In Claude Code, parallelise chunks across subagents (see `agent-orchestration.md`). In a single-context session, process sequentially and persist after every chunk so an interruption loses at most one chunk.
- Reasons are working notes, not deliverable prose; they may be terse. They still must be true: the reason names what the query is about, not a restatement of the class.

### Step 4: QA

- Sample audit: 200 rows stratified across the three classes, reviewed against the rubric in a fresh pass. Disagreement above ~5% on relevant/irrelevant (borderline excluded) means a systematic problem; find the pattern, fix rubric or chunks, re-run affected material.
- Near-duplicate consistency: rows flagged `near_dup_of` each other must carry the same class; the script `scripts/qa_pruning.py` checks this and lists conflicts for manual resolution.
- Group sanity: per-group kept counts against the scope map. A group with near-zero kept keywords either had bad seeds (report it) or is genuinely thin (also report it). Do not quietly backfill.

## Deliverable

`deliverables/<client>_keywords_pruned.xlsx`:

1. `Uebersicht` — methodology, counts (input, removed per rule, removed by LLM, borderline, kept), QA results, sheet index.
2. `Keywords` — kept rows, all provenance and metric columns, proposed group.
3. `Borderline` — same columns plus reason; the user decides these.
4. `Entfernt` — every removed row with rule ID or LLM reason.
5. `Rubrik` — the rubric as used, verbatim.
6. `Tone of Voice` — not applicable to keyword lists; replace with `Konfiguration` (run config).

Report: the counts, the top 5 patterns among removed rows, anything that surprised you, and open borderline volume. Then stop; clustering (Phase 7) is a separate go.
