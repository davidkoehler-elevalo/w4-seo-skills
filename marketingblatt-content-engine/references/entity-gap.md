# Competitor section + entity gap & comprehensiveness (MANDATORY — never skip)

This is the Paoli-Vetcare method, and it is **not optional and must never be shortcut to save tokens**.
An article that has not been measured section-by-section against the live top 5 is not finished. The
goal: match consensus on every core section and entity, and lead on several (real information gain).

## REQUIRED OUTPUT ARTIFACT — the "Gap Map" (write to file, then show at Checkpoint 1)

This step is not done in your head. You **write** `./mb-articles/<slug>-gap.md` filled from ACTUAL tool
output, and you **show it at Checkpoint 1 as the first block** (Generate) or in the Refresh brief. The
file has five parts, all filled — a `TODO`/empty row means the step is not finished:

```
# Gap Map — <topic>

## 0. FIT, WINABILITY & CLUSTER (decide FIRST — Golden Rule 7)
- Strategic fit: is the searcher OUR audience (DACH B2B decision-makers)? real W4 funnel behind it? honest HubSpot/tool fit? -> GO / WEAK (+ better-aligned angle)
- Winability: keyword difficulty + incumbent authority (competitor DR / referring domains) + incumbent freshness -> realistic GO / AUTHORITY-WALL / target longer-tail
- Cluster (head terms only): pillar + sub-pages map; existing MB pages NOT to cannibalise: ...

## A. INTENT gap (operationalise the split, do not just label it)
- Main + secondary intent + navigational share (dfs search_intent + volumes): ...
- ALL PAA questions captured: ...
- Intent threads in the SERP (informational / how-to / commercial / navigational / PRICE / ALTERNATIVES / video / ...): ...
- **Each meaningful sub-intent -> the section or CTA that serves it:** ...
- Which our angle already serves / which the SERP wants but we MISS -> action (section / FAQ / note)

## B. ENTITY / feature gap
(For German, the reliable entity sources are, in order: the PLATFORM'S OWN canonical feature/tool list
 e.g. the HubSpot KB, then competitor headings, then the AI Overview, then PAA. nl-seo mids are a weak
 supplement for German — do NOT rely on them as the source of truth.)
| Entity / feature | In top set? | In OUR draft/page? | Action (add / keep / lead) |

## C. ASSET gap
| Asset (definition, use-case list, step-by-step, comparison table, worked example, KPIs, visual/diagram, FAQ) | In top set? | In ours? | Action |

## D. Who wins & how + OUR beyond-insights
- Top-3 domains and the angle they lead with: ...
- Our 2-3 information-gain points (what we cover that the SERP does not): ...
```

**Every competitor asset, every must-cover entity/feature, and every SERP intent thread gets a row
with an explicit Action.** If any is missing a row, step 3 is not finished and you have NOT reached
Checkpoint 1.

## Inputs
- Top 8-10 CONTENT URLs from the SERP step (skip pure agency/nav landing pages for depth, keep them for
  the winability read), plus the AI Overview text if present.

## Procedure (do all of it, every time)

1. **Deep-read every competitor's full SUBSTANCE, not just headings.** `WebFetch` each of the top 8-10
   CONTENT results (the richest guide often ranks BELOW the top 5, e.g. Doofinder at #11 for shop SEO;
   name the single most comprehensive piece regardless of rank and beat it) and extract, per section: the key substantive points/claims, and the ACTUAL CONTENT of every
   asset (the exact point values in a scoring table, the worked example with its numbers, the formula,
   the matrix quadrants, the comparison-table rows, the checklist items), plus any unique/non-obvious
   point and how the article opens its answer. The goal is a master element inventory: take everything
   valuable from every competitor. `WebFetch` returns processed output, so a substance-level read of
   all of them is affordable; use `mcp__dfs-mcp__on_page_content_parsing` for a raw body when needed.
   The article must then reproduce the best version of every valuable asset and beat the deepest
   competitor, not merely tick that "an asset exists".
2. **Entity sources.** The AI Overview + the deep-read + the platform's own canon are the source of
   truth. `mcp__nl-seo__analyze_page_entities` is near-useless for German (kg_known_count 0) — **skip it
   by default**; run it only for English pages or as a last-resort supplement.
3. **Ground the head entities + find the unifying "why".** `mcp__google-kg__search_google_kg` on the
   head term and key related entities. Paoli lesson ("mechanism depth"): the entity often supplies a
   single unifying reason that turns the competitors' disconnected bullet lists into understanding.
   Explaining that "why" once is a real information-gain lever.
4. **Winability read.** Take the keyword difficulty (step 1) + a quick incumbent-authority read
   (competitor domain rating / referring domains via Ahrefs) + incumbent freshness. Write a realistic
   GO / authority-wall / go-longer-tail verdict into Gap Map part 0.
5. **Video mining (strong video pack only).** For how-to topics, skim the top YouTube results and pull
   the strongest one's subtitles (`mcp__dfs-mcp__serp_youtube_video_subtitles_live_advanced`) for steps
   the text competitors miss; decide whether to embed a video.

## Build TWO tables (both required)

**(A) Consensus SECTION / ASSET table** — one row per recurring section or asset:

| Section / asset | In top set? | In our article? | Ahead / behind |
|---|---|---|---|
| e.g. Konkrete Punkte-Matrix | 5/5 | must add | match |
| e.g. Schritt-für-Schritt-Aufbau | 3/5 | must add | match |
| e.g. Negatives Scoring als Fokus | 1/5 | yes | **ahead** |

**(B) Consensus ENTITY table** — one row per consensus entity: entity | in top-5? | must cover? |
our angle / beyond.

## Hard comprehensiveness rules (the failure this prevents)

- **Match every consensus asset.** If most or all top competitors include a concrete asset (a points
  matrix, a worked example, a step-by-step guide, a comparison table), the article **MUST** include an
  equivalent. A definition-only piece against a SERP full of worked examples is under-baked and will be
  rejected at the double-check. (This is the exact gap that made the first Lead-Scoring draft too thin.)
- **Match every core entity, lead on several.** Cover every "must cover = yes" entity, ideally in an
  H2/H3. Then go beyond on 2-3 points the top pages miss (contrarian, from project practice, the
  unifying mechanism). Those become the `beyond_insights` / `gain_point`s.
- **Length matches the SERP norm.** Do not ship short. If the top competitors run ~2,000-2,800 words
  with assets, the article lands in that range too. Depth is driven by what the SERP rewards, not by a
  fixed minimum, and never by token-saving.
- **"Who's winning and how."** Note which 1-2 domains hold top-3 and what angle they lead with, so the
  article matches their strengths and adds genuine gain rather than re-telling the commodity baseline.
- **Match VISUAL assets, not just text.** If the ranking pages use graphics, diagrams, matrices,
  charts, or infographics (a scoring matrix, a funnel, a process diagram), the article needs an
  equivalent, rebuilt natively: prefer clean inline **SVG/HTML** (crisp, on-brand, renders in HubSpot,
  no dependency on the image model) for diagrams/matrices; use generated images only for photographic
  covers. A wall of text against pages full of diagrams loses.
- **Re-create worked EXAMPLES with fresh scenarios.** Where competitors teach with an example
  (a scored sample lead, a persona comparison), build our own with a NEW scenario and NEW numbers,
  never copied. Concrete examples are a core value driver.
- **Standing principle:** always know exactly WHAT ranks and WHY it works for Google (structure,
  assets, examples, sections), then take the best of it and make it better. The article's job is not to
  match the SERP but to beat it on coverage, clarity, and usefulness.

## Query Deserves a Page (QDP — Koray Tuğberk Gübür, SEL 2026-07)
Before the outline, decide for every query variation in the network: **own page or section of this
page?** A variation deserves its OWN page only if it clears most of these four metrics:
1. **Search demand** — the variation has meaningful volume of its own.
2. **Different entities** — it introduces a new weighted entity (term weighting: in "HubSpot Lead
   Scoring" the added entity HubSpot is heavy; in "Lead Scoring Modell" the head term stays heaviest,
   so it is the SAME page).
3. **Low similarity** — weighted (entity + demand) similarity to the head query is low.
4. **Pattern** — it spawns its own attribute-query family (price, setup, comparison, problems …).

Everything below the threshold becomes a **section, table, FAQ item, or component of THIS page** —
never its own thin page (unnecessary pages = micro-cannibalization + retrieval cost). Record
variations that DO clear the bar as **future cluster pages**: cover them here only briefly and leave
room, so this article does not cannibalize them later. For a broad HEAD term, output an explicit
**pillar + cluster map** into Gap Map part 0 (this page = the pillar; the sub-pages it links down to),
and never cannibalise an existing MB sub-page (check the cannibalization step first). Map each section of the outline to the
augmented query it answers (query augmentation → the section/asset that serves it: matrix ↔ "modell/
beispiel", steps ↔ "einrichten", FAQ ↔ PAA …). Since the Helpful-Content era "helpful = functional":
prefer sections with a working asset (table, calculation, comparison) over prose-only.
Re-verify against BOTH tables: every consensus asset is present, every must-cover entity appears
(ideally in a heading), and the article leads on its stated `beyond_insights`. Any missing consensus
asset or entity is a blocker, closed with a targeted addition, never keyword stuffing.

## BLOCKING self-check (before you present Checkpoint 1 / the Refresh brief)
Answer YES to all, or you have skipped the step and must go back:
1. Does `./mb-articles/<slug>-gap.md` exist with all five parts (FIT/WINABILITY/CLUSTER, INTENT, ENTITY, ASSET, WINS+beyond) filled?
2. Did I deep-read the SUBSTANCE (not just headings) of the top competable results, and for a REFRESH
   also read OUR existing page, so the "In ours?" column is real?
3. Does every competitor asset, every must-cover entity/feature, and every SERP intent thread (incl.
   price / alternatives if present in PAA) have a row with an explicit Action?
4. Are the entity sources the platform's own canonical feature list + headings + AIO + PAA (not just
   nl-seo mids)?
5. Have I named 2-3 concrete information-gain points where WE lead?

If any answer is NO, the brief is not ready. Presenting an outline/brief without this filled Gap Map is
the exact failure this file exists to prevent.
