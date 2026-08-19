---
name: marketingblatt-content-engine
description: "Use this skill to research and write German B2B blog articles for Marketingblatt (blog.marketingblatt.com, the W4 Marketing agency blog) and deliver them as review-ready drafts in Google Drive. Two modes. GENERATE: turn a topic into a full SEO article (SERP + keyword + intent research, own-site cannibalization check, top-5 competitor entity-gap via Google NLP + Knowledge Graph, verified fresh DACH stats, section-by-section draft in the Marketingblatt voice, KB/brand gate, classifier scorecard, relevance-ranked internal links, cover image, quality gate, Google-Drive draft). REFRESH: update a declining existing post (reuses the seo-content-refresh skill in Marketingblatt voice). Triggers: 'schreib einen Marketingblatt-Artikel zu X', 'neuer Blogartikel für Marketingblatt', 'Marketingblatt content engine', 'refresh this Marketingblatt post', 'aktualisiere den Blogartikel', or any request to produce/refresh a Marketingblatt / W4 blog article. Replaces the n8n Marketingblatt Content Engine workflow."
---

# Marketingblatt Content Engine

Ports the 44-node n8n "Marketingblatt Content Engine v1.8.6" workflow into a Claude Code skill. Every
external call is an MCP tool; every writing/gating step is your own reasoning guided by the reference
files in `references/`.

**Author/byline:** David Koehler. **Blog:** blog.marketingblatt.com (W4 Marketing, HubSpot Diamond
Partner, DACH B2B). **Delivery:** finished drafts go to Google Drive; see `references/delivery.md`.

## Golden rules (never violate)

1. **Never auto-publish.** Output is always a **draft in Google Drive** the user reviews; a human
   moves it into the CMS.
2. **Two human checkpoints** in Generate mode: after the brief/outline, and before creating the draft.
3. **Invent no facts or numbers.** Every statistic needs source + year + a live, verified URL, cited
   inline (see `references/evidence-tiers.md` and `references/article-structure.md`).
4. **Voice is binding.** Swiss Hochdeutsch (always `ss`, never `ß`; money in CHF/Franken), address the
   reader as `ihr/euch` (never Sie, never du), no em dashes, no AI tells. Rules:
   `references/brand-voice.md`; **tone model** (Pipedrive craft, ihr-form): `references/tone.md`;
   sentence craft: `references/readability.md`. All three hold at once, for EVERY article; the
   Pipedrive-modeled tone in `references/tone.md` is the always-on default voice, no exceptions.
5. **Never skip or shortcut the competitor section + gap analysis (step 3) or the comprehensiveness /
   concrete-asset requirement, not even to save tokens.** Reading every top-5 competitor's sections,
   building the consensus tables, matching every consensus asset (points matrix, worked example,
   step-by-step, comparison table), and matching the SERP's length norm are mandatory. A definition-only
   or short piece against a rich SERP is a failure, not a lean option.
   **HARD GATE:** step 3 produces a written Gap Map artifact `./mb-articles/<slug>-gap.md` (INTENT +
   ENTITY + ASSET + wins, per `references/entity-gap.md`), and Checkpoint 1 / the Refresh brief is NOT
   reached until that file is filled from real tool output and shown. Presenting any brief, outline, or
   refresh plan WITHOUT the filled Gap Map is a hard failure — go back and do step 3. This applies in
   Refresh mode too (the "In ours?" column = the existing page).
6. Read the reference file before doing the step that cites it. Do not reinvent its rules.
7. **Strategic-fit gate (surface at Checkpoint 1).** Before committing to a topic, judge whether it
   actually fits Marketingblatt: (a) is the searcher OUR audience (DACH B2B decision-makers), or a
   mismatched crowd (B2C shop owners, consumers, job seekers …)? (b) is there a genuine W4 offer /
   funnel behind it so the traffic can convert? (c) does the HubSpot/tool angle fit honestly, or would
   it be forced? If the fit is weak, SAY SO at Checkpoint 1 and propose a better-aligned angle or
   adjacent keyword. Great content for the wrong audience is a failure, not a win.

## Data sources and mandatory fallbacks (Plan B is never optional)

Never stop a run because one data provider is down. Every research step has a documented second
source. Announce the switch in one line, run the fallback, and note the substitution at the checkpoint
so the user knows which provider produced the numbers.

| Need | Plan A | Plan B (when A fails) | Plan C |
| --- | --- | --- | --- |
| SERP + top results | `mcp__dfs-mcp__serp_organic_live_advanced` | `mcp__claude_ai_Ahrefs__serp-overview` (`select` incl. `type` — it exposes `ai_overview` / PAA rows) | claude-in-chrome on a live google.de search |
| Keyword volume / difficulty | `mcp__dfs-mcp__dataforseo_labs_google_keyword_overview` | `mcp__claude_ai_Ahrefs__keywords-explorer-overview` (`difficulty`, `traffic_potential`, `parent_topic`, `intents`) | `keywords-explorer-matching-terms` |
| Search intent | `mcp__dfs-mcp__dataforseo_labs_search_intent` | Ahrefs `intents` object on keywords-explorer-overview | read intent off the live SERP format |
| PAA / questions | DFS PAA | `keywords-explorer-matching-terms` with a question `terms` filter | AI-Overview sitelinks from Ahrefs `serp-overview` |
| Competitor page content | `WebFetch` | `mcp__plugin_context-mode_context-mode__ctx_fetch_and_index` + `ctx_search` | claude-in-chrome |

**DataForSEO returns HTTP 402 when the account is out of credit.** That is the signature — not a bug,
not a retry case. Switch to Ahrefs immediately and tell the user the DFS balance needs topping up.

**Search Console is a separate source and is checked in its own right, never inferred from Ahrefs
Site Explorer.** Site Explorer only sees keywords it has sampled, so a page ranking ~30+ or on
low-volume terms shows as "no keywords" while GSC shows thousands of impressions. Always pull GSC:
`gsc-page-history` + `gsc-keywords` on Ahrefs project `4425008` (Blog.marketingblatt), filtering
`where: {"field":"url","is":["substring","<slug-fragment>"]}`. If a page shows impressions but zero
clicks, that is a presentation/SERP-feature problem, not a content-depth problem, and the brief must
say so.

## Mode routing

- **Generate** — the user gives a topic / keyword and wants a new article. Run "Generate mode" below.
- **Refresh** — the user points at an existing post (URL, title, or slug) or says refresh / update /
  "declining". Run "Refresh mode" below.
- If ambiguous, ask which mode in one line.

Create a working folder `./mb-articles/` and save the final article markdown as `<slug>.md` alongside
the Drive upload, so there is always a local copy.

---

## Generate mode (topic → Google-Drive draft)

Track the run with a todo list. Steps 1-5 are research (silent), then CHECKPOINT 1, then draft, then
CHECKPOINT 2, then deliver.

### 1. SEO research
- `mcp__dfs-mcp__serp_organic_live_advanced` — keyword = topic, `location_name: "Germany"`,
  `language_code: "de"`, depth 20, include People-Also-Ask. Capture top-10 organic (title, url,
  snippet), PAA questions, and SERP features (featured snippet, AI overview, PAA, **video pack**). A
  strong video pack on a how-to topic is a real sub-intent — note it for a possible embed and for video
  mining in step 3.
  **Classify the dominant SERP format** from the top titles/structures (numbered Tipps/Schritte
  listicle vs guide/definition vs comparison) — this DRIVES the article format later
  (`article-structure.md` → Match the dominant SERP format). Titles like "11 Tipps"/"10 Schritte"
  dominating means the article is a numbered tips listicle.
- `mcp__dfs-mcp__dataforseo_labs_google_keyword_overview` — topic, `location_name: "Germany"`,
  `language_code: "de"`. Capture volume, difficulty, related terms.
- `mcp__dfs-mcp__dataforseo_labs_search_intent` — topic + 2-3 variants, `language_code: "de"`. Capture
  the **main AND secondary intents plus any navigational split** (e.g. 50/50 informational/commercial
  with a navigational brand/tool share). Do not just record the top label — the split is
  **operationalised** in the Gap Map: each meaningful sub-intent maps to a section or the CTA.

### 2. Cannibalization (own site)
- `mcp__claude_ai_Ahrefs__site-explorer-organic-keywords` — target `blog.marketingblatt.com`,
  country `de`, top ~50 by best_position. Identify existing pages that already rank for this keyword
  universe. Decide: **NEW** (distinct angle) or the piece should defer to an existing page. Record
  competing URLs, a differentiator angle, and internal-link targets. This mirrors STEP2 in the n8n.
- **Strategic fit (Golden Rule 7):** record a one-line verdict on audience match + real W4 funnel +
  honest tool fit for Checkpoint 1; if weak, propose a better-aligned angle.
- **Head-term architecture (QDP):** if the topic is a broad head term whose sub-queries deserve their
  own pages (e.g. "SEO für Online-Shops" → Shopify-SEO, technisches Shop-SEO, Produktseiten), plan a
  **pillar + cluster** instead of one flat article: the new piece is the pillar linking down to
  existing/planned sub-pages and must NOT cannibalise an existing sub-page (here MB already ranks with
  `/de/seo-in-shopify`). Record the cluster map in the Gap Map.

### 3. Competitor section + entity gap (MANDATORY — the Paoli method, never skip)
Follow `references/entity-gap.md` in full. This step is not optional and must not be shortcut.
**BLOCKING GATE:** the deliverable of this step is the written Gap Map `./mb-articles/<slug>-gap.md`
(INTENT / ENTITY / ASSET / wins). You may NOT move to step 5 or Checkpoint 1 until that file exists,
is filled from real tool output, and every competitor asset + must-cover entity + SERP intent thread
(incl. price/alternatives if in PAA) has a row with an explicit Action. Run the `entity-gap.md`
BLOCKING self-check before presenting anything.
- **TEN results is the floor, and it is NON-NEGOTIABLE.** Not "5 if they look similar", not "8 to save
  tokens", not "3 deep-reads and infer the rest". Fetch the **full pool of the top 10 organic results
  plus every content page cited in the AI Overview**, because a large share of any pool is unusable for
  depth analysis: pure vendor landing pages (Esker: 667 words, 21 lists, no argument), pages that
  return 403 to a plain user agent (SAP), pages rendered client-side that come back as 1 word
  (erp-4-business), and navigational/glossary stubs. You only find out which ones are useless *after*
  fetching. **If pages drop out, pull replacements from deeper in the SERP until you have ten usable
  pages.** A conclusion drawn from three pages is not a consensus, it is an anecdote — and it will be
  wrong in a specific, expensive way (see the measurement rule below).
  `WebFetch` each result for its H2/H3 AND concrete ASSETS (matrix / worked example / calculator,
  step-by-step, comparison table, checklist, FAQ). **Explicitly identify the single most comprehensive
  content piece regardless of rank and beat it.** Keep vendor landing pages out of the depth read but
  in the winability read.
- **MEASURE, never assert.** Word counts, asset counts (`<table>`, `<ol>`, `<ul>`, `<img>`, FAQPage
  schema) and entity coverage are counted across the whole pool with a script, then reported as
  `n/10`. Never write "competitors are longer" or "all competitors have X" without the number behind
  it. The length target is derived from the measured strong-content cohort, never from a fixed range.
- **Coverage decides table stakes vs differentiator.** An asset or entity present in most of the pool
  is table stakes and MUST be matched. One present in 0-1 of the pool is a **differentiator** — an
  opportunity to lead, not a gap to close. Getting this backwards inverts the whole brief: it makes
  you copy an outlier's niche vocabulary while missing what everyone actually covers. Some consensus
  content types are deliberately NOT worth copying (e.g. a page padded with 41 bullet lists and 38
  images); note them as consensus, then say plainly why we are not matching that particular pattern.
- **Entities:** the AI Overview + the deep-read + the platform's own canon are the entity source of
  truth. `mcp__nl-seo__analyze_page_entities` is **near-useless for German (kg_known_count 0) — skip it
  by default**; run it only for English pages or as a last-resort supplement.
- **Ground + find the "why":** `mcp__google-kg__search_google_kg` on the head + key entities; look for
  the unifying mechanism that turns competitors' disconnected lists into understanding (info gain).
- **Measure competitor article lengths** (curl + body word count, see `article-structure.md` → Length)
  and set the article's length target from the strongest content competitors, not a fixed range.
- **Winability read (be honest whether we can rank).** Do not stop at the content gap. Take the keyword
  difficulty from step 1 and a quick authority read on the incumbents (competitor domain rating /
  referring domains via Ahrefs, plus incumbent freshness, e.g. an incumbent from 2019 is beatable).
  State a realistic verdict at Checkpoint 1: low KD + stale/thin incumbents = go; high KD +
  strong-authority incumbents = reconsider or target a longer-tail sub-query.
- **Video mining (strong video pack only).** For how-to topics, skim the top YouTube results and use
  `mcp__dfs-mcp__serp_youtube_video_subtitles_live_advanced` on the strongest one for steps the text
  competitors miss; decide whether to embed a video.
- **Build BOTH tables:** (A) consensus SECTION/ASSET table (section/asset | in top set? | ours? |
  ahead/behind) and (B) consensus ENTITY table. **Comprehensiveness is a hard rule:** any asset most/all
  competitors have (matrix, worked example, step-by-step, comparison table) MUST appear in the article;
  match the SERP's length norm; note who's winning, HOW, and WHY (content depth AND authority/freshness).
  The `ahead` rows are the `beyond_insights`.

### 4. Fresh stats + community mining (NEW)
Follow `references/evidence-tiers.md`.
- `WebSearch` for 3-5 recent (2024-2026) DACH/B2B statistics with **primary** sources; tier them.
  Prefer the original publisher (Bitkom, HubSpot Research, etc.); a reputable secondary source is OK
  only if the primary is not public. No paywall/login URLs. Invent nothing; an empty set beats a fake.
- `WebSearch` Reddit / LinkedIn / practitioner forums for the real questions and pains behind the
  topic; fold genuine ones into `must_answer_questions` and the FAQ.
- Verify every candidate stat URL:
  `bash scripts/verify_stat_urls.sh '<json-array of {claim,value,year,source_name,source_url}>'`
  Keep only stats whose URL is live, non-redirecting, and non-paywall (fail-open: keep the solid ones).

### 5. Intent-led brief + outline
Follow `references/article-structure.md`. Proof cases are **optional and off by default**: only glance
at `references/proof-library.json` if the topic has an obvious, natural fit, and even then include one
only if it can be woven in without feeling forced. Most articles carry no proof. Build:
- **First pick the FORMAT to match the SERP** (`article-structure.md` → Match the dominant SERP
  format). If the top German results are numbered Tipps/Schritte listicles, the outline is a numbered
  tips listicle; fold our unique material (KPIs, HubSpot, beyond-insights) in as additional tips.
- **Turn the consensus SECTION/ASSET table from step 3 into the outline.** Every asset most/all
  competitors have (points matrix / worked example, step-by-step build, comparison table, checklist)
  becomes its own concrete section or tip. Then add the `beyond_insights` where you lead.
- **Run the QDP check** (`entity-gap.md`, Query Deserves a Page): decide per query variation whether
  it is a section of THIS page or a future cluster page (4 metrics: demand, new weighted entity, low
  similarity, pattern). Cover future-page variations only briefly here to avoid self-cannibalization;
  map each outline section to the augmented query it answers.
- Section count is driven by that table and the SERP length norm, NOT by a fixed small cap. Match the
  top competitors' depth (often 6-8 content sections, ~2,000-2,800 words); go shorter only if the SERP
  genuinely is (a pure narrow definition). Never trim to save tokens.
- Each section: unique H2 (50-80% as real W-questions), a distinct opening technique
  (Prinzip | Szenario | Frage | Datenpunkt | Kontrast, none repeated while unused ones remain), one
  assigned stat at most (each stat used exactly once article-wide), a proof only if one genuinely fits
  naturally (usually none), `beyond_insights` distributed as `gain_point`s.
- **HubSpot-relevance check (mandatory):** decide whether HubSpot (or a W4 tool the user named) genuinely
  helps with this topic (most CRM/marketing/sales/lead/data/automation topics qualify). If yes, WebFetch
  HubSpot's real capabilities for this area (`knowledge.hubspot.com`, `hubspot.com/products`) and plan a
  grounded "X mit HubSpot" section per `article-structure.md` → Tool-solution section. If no genuine
  angle, note it and skip.
- A `fazit` section, a `faq` with **at least 5 items** (each answer 2-3 real sentences), title (keyword front, thesis),
  meta (≤155 chars), intro brief. Fold in the entity-gap must-cover list and internal-link map.

> **CHECKPOINT 1** — Show the user, in this order: (1) the filled **Gap Map** (INTENT gap, ENTITY/
> feature gap, ASSET gap, wins + beyond-insights) from `./mb-articles/<slug>-gap.md`, built from real
> tool output — this comes FIRST; (2) the **strategic-fit verdict** (audience / W4 funnel / honest tool fit, Golden Rule 7), the chosen
> angle + cannibalization decision, a realistic **winability** verdict, and any **pillar/cluster** plan; (3) the surviving
> verified stats (with tiers); (4) the full outline (H2s, opening techniques, assigned stats/proofs).
> **If you are about to present without the filled Gap Map, STOP — you skipped step 3.** Wait for OK or
> edits before drafting.

### 6. Draft (section by section)
Follow `references/tone.md` + `references/brand-voice.md` + `references/article-structure.md` +
`references/readability.md` precisely. `tone.md` is the target voice (Pipedrive's craft in ihr-form) —
every article must read in that same consistent tone. For each outline section, write ONE `<h2>` block (~220-320 words) with the assigned opening
technique, the direct answer to the H2 in the first 1-2 sentences (AI-Overview-citable), the assigned
stat cited inline (source name in the sentence, a **descriptive phrase of the claim including the
number** is the `<a>` anchor to the stat URL — never the bare number), and ONLY if the section has a
proof assigned (usually none), weave it in with a link to its `w-4.ch` case URL. Maintain a running
ledger (used openings, used stats, used scenarios, covered points, `sondern` count ≤2, "Aus unserer
Sicht" count ≤2, topic introduced once). Then:
- **Read-aloud pass** (`readability.md`): read every sentence out loud; split anything long, nested, or
  convoluted; vary sentence length; verbs over nominalizations. This is where "AI-sounding" text dies.
- **Cohesion pass**: vary the opening sentences so no two sections start with the same pattern.
- **Intro + title + 3 meta options**: intro = thesis lead + core answer in the first two sentences +
  a `<p><strong>Das Wichtigste in Kürze:</strong></p><ul>` box with 3-4 citable bullets (the ONE place
  the topic gets defined). Generate 3 title and 3 meta-description options with one-line rationale each,
  then pick the best (Paoli method).

### 7. Voice audit vs a real exemplar (NEW default)
Fetch the blog post sitemap (`https://blog.marketingblatt.com/sitemap.xml`) → pick a recent
published post, WebFetch it, and do a head-to-head: heading architecture, register, closing structure, drug/product
naming, de-AI compliance. Adjust the draft to match the real house voice, keeping wording that already
works rather than replacing for its own sake.

### 8. KB / brand gate
Self-audit against `references/kb-strategy.md` (two rounds: alignment + do-no-harm). Apply only clear
style/KB fixes (bounded patches; never delete stats, sources, links, or headings; never insert a dash).

### 9. Section + entity double-check, chunk read + classifier scorecard (NEW)
- **Double-check against BOTH tables from step 3.** Every consensus ASSET is present (matrix, worked
  example, step-by-step, comparison table) and every must-cover ENTITY appears, ideally in a heading.
  A missing asset or entity is a blocker; close it with a targeted addition, never keyword stuffing.
- **Chunk-level read (Paoli ClusterUplift/NsrChunks).** Treat each section as an independently scored
  chunk: it must answer its heading self-containedly (no "wie oben erwähnt") and earn its place. A short
  section is fine only if it makes a specific, non-obvious point, never generic filler.
- Score the draft on the influenceable levers in `references/classifier-scorecard.md` (/10 each) and
  compute the composite. If the composite is weak, an asset/entity gap remains, or any chunk is thin,
  revise before continuing.

### 10. Internal links + link audit
Collect all published post URLs from the blog sitemap (`https://blog.marketingblatt.com/sitemap.xml`),
WebFetch titles/metas for the plausible candidates. Score candidates by topic/keyword term hits
(title 3 / slug 2 / meta 1, cluster terms +1) per
`references/delivery.md`; take the top ~16. Then pick **5-6** internal links (reasonable-surfer rules in
`references/delivery.md`): first half of the section, max 1 per H2, none in headings or the FAQ.
**ANCHOR RULE (KB `factors/internal-links/internal-anchor-text.md`, 7/10, non-negotiable): the anchor
text must carry the TARGET page's main terms — "link with the terms you want the target to rank for"
(Williams-Cook), not a phrase that merely reads well in our sentence.** "Anchors that literally occur
in the body" is necessary but NOT sufficient: if the surrounding sentence has no natural phrase naming
the target's topic, REWRITE the sentence until one exists, then link that. Test per link: could a
reader (and Google) predict the target page's topic from the anchor alone? An anchor like "im
führenden System" pointing at a Datenpflege article fails; "eurer Datenpflege" passes.
**No brand names in anchors, CTAs, or offer phrasing where they narrow the audience** (David, 3x on
the ERP refresh): "fertige Apps im HubSpot-Marktplatz" as anchor or "die ERP-Anbindung an HubSpot" as
offer makes every non-HubSpot reader self-select out. Brand belongs in the surrounding context
sentence ("HubSpot etwa liefert mit Data Sync ..."); the anchor and the offer name the capability.
**Anchors must also read natural**: the sentence makes a real claim first and the anchor occurs
inside it organically; a sentence constructed to hold target terms is a defect ("kept natural" is
part of the KB rule itself). Prefer fewer, exact-fit links over a forced 5-6.
Insert them. Also list **inbound** recs:
existing posts that should later link TO this new one (report to the user, do not edit them here).
- **Link audit (Paoli):** any external link points to a primary or authoritative source and sits on the
  specific claim it supports; clean neighbourhood only (no forums, no SEO-spam). Internal anchors are
  descriptive topic matches, distributed across sections (max 1 per H2), reinforcing the MB cluster.

### 11. Cover image
Follow the image plan in `references/article-structure.md`. Generate the cover with
`mcp__nano-banana-2__generate_image` (aspectRatio "16:9", brand style, **no text in the image**,
`returnInlineImage: false`). Keep the image as a local file next to the article; it is uploaded to
Google Drive with the draft in step 13 and attached in the CMS by the reviewer.

### 12. Quality gate
- **Invisible-Unicode pass (run FIRST, before the other checks).** Write the final `postBody` to
  `./mb-articles/<slug>.body.html` and run
  `bash scripts/clean_invisibles.sh ./mb-articles/<slug>.body.html`, then use the cleaned file as the
  body from here on. This strips zero-width characters, soft hyphens, word joiners and bidi controls
  that survive from model output into published HTML, where they break search-and-replace, corrupt
  slugs, and read as machine-written to detectors. It is deterministic and never changes visible copy.
  Report the returned counts at Checkpoint 2; `nbsp_to_space` is expected on German copy (see
  `references/quality-checklist.md` → LOW issues). Fails open if the cleaner is missing: say so and
  continue, it is not a blocker.
- Run the deterministic checks in `references/quality-checklist.md` against the final `postBody`
  (links valid + in-body, stats cited, no em dashes / `ß`, `sondern` ≤2, FAQ answers ≥120 chars, one
  "Häufige Fragen" H2, "Das Wichtigste in Kürze" box present, images have alt text). Fix any HIGH issue;
  do not publish with an open HIGH issue.

> **CHECKPOINT 2** — Show the final title, chosen meta, full body (rendered), cover image, and the
> inbound-link recommendations. Wait for OK.

### 13. Deliver to Google Drive
- Assemble the deliverable set in `./mb-articles/`: `<slug>.md` (article markdown incl. title + meta
  options), the cleaned `<slug>.body.html` (paste-ready HTML), and the cover image.
- Upload the set to a Drive folder named after the slug, per `references/delivery.md`: import the
  HTML as a Google Doc so reviewers can comment, and keep the raw `.body.html` beside it for a
  lossless CMS paste.
- If no Drive access is configured, fail open: keep the local files and report their paths.
- Report the Drive folder link plus the local paths.

---

## Refresh mode (declining post → refreshed draft)

1. Resolve the target post from the URL/slug/title (blog sitemap lookup if needed) and WebFetch the
   live post for its current body.
2. Diagnosis: if Marketingblatt GSC is connected in Ahrefs, pull it
   (`mcp__claude_ai_Ahrefs__gsc-keywords` / `gsc-page-history` / `gsc-performance-history` for the URL);
   otherwise fall back to SERP (`serp_organic_live_advanced`) + Ahrefs organic-keywords.
3. **Entity-gap Gap Map FIRST (BLOCKING).** Before any refresh brief, run `references/entity-gap.md`
   in full against the live top competitors AND the existing page: deep-read the competable results'
   substance, capture PAA + intent, and write `./mb-articles/<slug>-gap.md` where the "In ours?" column
   reflects the CURRENT page. The refresh additions come straight from that map (what the SERP covers
   that our page lacks: entities, features, assets, intent threads). Do not present a refresh plan
   without the filled Gap Map — same hard gate as Generate.
4. **Invoke the `seo-content-refresh` skill** (or apply its methodology directly when you already hold
   the context) for the heavy lifting (page-type classification, keep-vs-rewrite, editor brief). Pass
   it the Marketingblatt context so its output is in-voice and German: `references/brand-voice.md`,
   `references/article-structure.md`, and `references/delivery.md`. Do not reimplement what it does.
5. Run the **step 12 quality gate** on the refreshed body — including the invisible-Unicode pass, which
   matters more here than in Generate: the existing live body may already carry zero-width junk from
   earlier drafts or from a paste through the editor. Then apply the two checkpoints (refreshed brief,
   then final).
6. Deliver the refreshed body to Google Drive exactly like Generate step 13 (Google Doc +
   paste-ready HTML). **Never publish** — the user reviews and moves it into the CMS. Save a local
   copy too.

---

## Prerequisite

Drive delivery needs Google Drive access (e.g. `gcloud auth application-default login` with a Drive
scope, or a Drive integration available in the session). Without it, step 13 fails open: the
finished files stay local and their paths are reported.
