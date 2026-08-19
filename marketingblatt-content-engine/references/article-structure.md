# Article structure & outline rules (binding)

Lifted from the n8n STEP3 (brief/outline), Intro+Title+Meta, and STEP8 (image) prompts.

## Length — MEASURED from the SERP, never a fixed number
Do NOT invent a word-count target and do NOT default to a fixed range. **Measure the actual article
length of the top-ranking results** and derive the target from that data. In step 3, curl each top
content URL and count the words inside the article body (text within `<p>`, `<li>`, `<h1-4>` tags is a
good proxy):
```
curl -sL -A "Mozilla/5.0 ..." "<url>" | python3 -c "import sys,re,html; t=sys.stdin.read(); \
b=re.findall(r'<(?:p|li|h[1-4])[^>]*>(.*?)</(?:p|li|h[1-4])>',t,re.S|re.I); \
print(len(html.unescape(' '.join(re.sub(r'<[^>]+>',' ',x) for x in b)).split()))"
```
Then set the target to **match or slightly beat the STRONGEST relevant content competitor**, not the
median and not a made-up number. Measured example (LinkedIn Marketing DE): HubSpot ~3,800, Sprout
~3,900, lexware ~2,000, OMR ~1,100 → target ~3,000-3,500. If the strong results are long, the article
is long; if the SERP is genuinely thin, it can be short. Section count follows the SERP-format match +
the consensus assets. Never trim to save tokens; report the measured competitor lengths at Checkpoint 1.

## Tool-solution section (house strategy) — MANDATORY relevance check
**Every article runs a HubSpot-relevance check** (and any other W4 tool the user names): can the topic
genuinely be solved, automated, or run with HubSpot? HubSpot is a CRM + marketing/sales-automation
platform, so most CRM, marketing, sales, lead, data, content, or automation topics qualify.

**House strategy (why this section exists):** Marketingblatt is W4's subtle lead-gen. Wherever the
relevance is genuine, the article quietly shows how OUR solution, HubSpot implemented by W4, makes the
reader's problem or process easier. This is a positioning goal, not a frequency mandate: it lives in
ONE natural section (or a woven example), never across the whole article, and never forced where the
fit is weak. Proof cases stay separate and OFF by default (see `brand-voice.md`); this is about the
helpful HubSpot angle, not client stories.

If YES:
1. **Research the tool's ACTUAL capabilities in that area** before writing — WebFetch the HubSpot
   knowledge base / product docs (`knowledge.hubspot.com`, `hubspot.com/products`) for the real
   features, editions, and automation for this specific topic. Never write generic tool claims from
   memory; ground it in current, accurate capabilities.
2. **Position HubSpot as the solution, in ONE of two shapes** (choose by topic):
   - (a) **Dedicated section** when the topic is HubSpot-near: one section like "X mit HubSpot" that
     shows concretely how it works, the practical value, why it beats a stand-alone/spreadsheet
     approach, tied back to the article's own concepts (fit+engagement score maps to our matrix, decay
     maps to negative scoring).
   - (b) **Woven example** for ADJACENT topics that are not literally "HubSpot X": show HubSpot as the
     concrete example inside an already-planned section. E.g. an article on "CRM Implementierung" names
     HubSpot in a "leicht implementierbare CRMs" section and shows how it makes the process easier. The
     topic stays neutral, HubSpot appears as the natural, helpful example, never a pitch.
   Either shape: educational, specific, useful, never a marketing blurb. HubSpot lives in the BODY, W4
   (agency) stays in the closing CTA.

This is also where the one "HubSpot Diamond Partner + we implement it" mention can live, but Diamond
Partner still appears at most once in the whole article (here OR in the closing CTA, not both).
If the topic genuinely has no HubSpot angle, note that in the brief and skip the section. **The check
must have teeth to say NO:** e.g. on-shop e-commerce SEO (shops run on Shopify / WooCommerce / Shopware,
HubSpot is not a shop system), pure consumer/B2C topics, or anything W4 has no real offer for — force
nothing, skip the section, and (per the strategic-fit gate, Golden Rule 7) reconsider whether the topic
even fits Marketingblatt at all. Record the chosen positioning shape (dedicated section vs woven
example) and the concrete problem→HubSpot-solution angle in the brief, so it is decided at Checkpoint 1.

The Fazit counts toward this number. Sections are pure content sections — NOT meta items like Title,
Meta-Description, Intro, FAQ, or a classifier checklist. Those never appear in the outline array.

## Per-section fields
Each outline section has:
- `h2` — heading containing the section entity. **50-80% of H2s are real user W-questions**, but not
  mechanically every one.
- `opening_technique` — one of **Prinzip | Szenario | Frage | Datenpunkt | Kontrast**. No technique
  repeats while an unused one remains.
  - Prinzip = general truth first, then explanation.
  - Szenario = "Stellt euch vor: ein [Rolle] bei einem [Unternehmenstyp] in [Ort] …".
  - Frage = one targeted rhetorical question, then the answer.
  - Datenpunkt = open with the assigned number.
  - Kontrast = the usual assumption, then the better practice.
- `lead_line` — a unique first-sentence idea (inspiration, not copied verbatim).
- `assigned_stat` — one stat object `{value, source, year, url}` from the verified set, or `null`.
  Each stat is used **exactly once** article-wide. Never more sections with a stat than there are
  stats; surplus sections get `null`. If the stat set is empty, ALL sections get `null` and no section
  uses industry percentages or market numbers (not even "erfahrungsgemäss X %").
- `scenario_angle` — only 1-2 sections get a concrete scenario (Rolle + Unternehmenstyp + Ort +
  Verhalten, never "ein Kunde aus der Industrie"). All others `null` and argue with data, mechanics,
  and a CHF calculation example.
- `gain_point` — set on the 1-3 sections that best fit a `beyond_insight` (≤100 chars); at least one
  section carries one; others omit the field. This is the article's information gain.
- `assigned_proof` — **DEFAULT is none.** Include a W4 proof case ONLY when one genuinely fits the
  section's argument and can be woven in naturally; if in doubt, leave every section `null`. Most
  articles carry NO proof. A case that reads as squeezed in or bolted on is a defect, not a
  requirement. There is no per-article quota. Never force a proof in and never invent one.
- `internal_link_hint` — a thematic anchor note (links are placed later).
- `subpoints` — max 3 keywords / H3s.
- `reintroduce_topic` — exactly ONE section may be `true` (the definition section). The overall topic
  is introduced once; after that it is assumed, never re-introduced.

One section must carry a clear prioritisation or NOT-to-do message (what to drop or do first) as a
subpoint. Definitions (term and type explanations) go ONLY into FAQ entries, never as section
subpoints.

## Fazit (separate top-level field, not in the outline array)
`fazit` object, same shape as an outline entry, `h2: "Fazit"`, `assigned_stat: null`. Bundles the 2-3
core takeaways WITHOUT Erstens/Zweitens counting. The CTA after it begins with a question that ties
back to the article's core question. In the Fazit and in FAQ answers the word "sondern" is forbidden —
phrase affirmatively.

## FAQ
**At least 5 items** (min 5), each `{question, answer}`. Draw them from the PAA questions and real
community questions; more is fine when the SERP is rich. Each answer is a real, self-contained answer in 2-3 sentences —
not a placeholder, not a restatement of the question. This is where definitions live. Pull real
questions from PAA + community mining.

## Title & meta
- `title` — keyword front, thesis-driven, readiness hook.
- `meta` — ≤155 chars, promise + keyword.
- Generate **3 title options and 3 meta options** with a one-line rationale each, then pick the best
  (Paoli method). Keep the winners; discard the rest.

## Intro (Intro+Title+Meta step)
HTML, 1-2 `<p>`. **Hook first:** open with a concrete pain point the reader recognises and the value
the topic delivers, in short, easy-to-read sentences. NO convoluted openers ("Über den Erfolg von X
entscheidet selten Y, sondern der Moment, in dem …" is exactly what to avoid). Then land the
definition, so the core question is still answered in the **first two-three sentences** (AI-Overview
citable). **Zero promotional wording in the intro** (no agency or partner mention). Then end the intro with a box:
`<p><strong>Das Wichtigste in Kürze:</strong></p><ul>` with 3-4 bullets (each ≤15 words, each citable
on its own). This is the ONE place the overall topic is defined/placed. No `<h1>`, no heading. Max one
colon in the whole intro, never as an announcement.

**Intro flow (Paoli lesson):** ideas must connect, not sit side by side. No reassurance-then-caution
whiplash ("X ist gut. X ist unzuverlässig."), and no disconnected meta-roadmap sentence ("Dieser
Beitrag zeigt euch …"). Bridge one thought into the next so the opening reads as one thought, not an
assembled list of moves.

## Citation format (binding, inline)
Weave the stat inline, source NAME spoken in the sentence, and link a **descriptive phrase of the
claim that includes the number** — NOT the bare number. The anchor should read as a meaningful clause
on its own.
- ✅ `<a href="{url}">geben 56 Prozent der befragten B2B-Unternehmen an, ihre Leads noch von Hand zu bewerten</a>`
- ✅ `<a href="{url}">halten 37 Prozent der Unternehmen es für nützlich, kaufbereite Leads automatisch an den Vertrieb zu übergeben</a>`
- ❌ `<a href="{url}">56 Prozent</a>` (bare number as anchor — too thin, not descriptive)

NO bracket citations like "(Quelle: X, Jahr)", NO `rel="nofollow"`, NO sources block at the end. Each
stat used at most once article-wide. A stat anchor never overlaps an internal-link anchor in the same
sentence; move the internal link to another phrase if they collide.

Without an assigned stat: no industry percentages or market numbers. Allowed instead: (a) qualitative
statements, (b) concrete single project observations without percentage generalisation, (c) a
calculation example with values explicitly marked as assumptions ("Rechnet konkret: bei 50'000
Kontakten und 3 Minuten pro Datensatz …").

## Tables must be styled inline (HubSpot renders bare tables broken)
HubSpot's blog theme shows a bare `<table>` with no borders and no header styling, which looks broken
live. Always add inline styles. **The table text must be the SAME size as the body text** (like the
graphics) — never larger. Use `font-size:inherit` on the table AND on every `th`/`td` so the cells
inherit the body/paragraph size instead of the theme's default table size. Never hardcode a px size:
- `<table style="border-collapse:collapse;width:100%;margin:18px 0;font-size:inherit">`
- `<th style="background:#1f2d3d;color:#fff;text-align:left;padding:10px 14px;border:1px solid #cbd5e1;font-weight:600;font-size:inherit">`
- `<td style="padding:10px 14px;border:1px solid #e2e8f0;vertical-align:top;font-size:inherit">`
Every `<table>`, `<th>` and `<td>` carries inline styling before publishing, and no table text is
larger than the surrounding paragraphs.

## Match the dominant SERP format (decide BEFORE you outline)
The article's FORMAT must match what already ranks in **Google Germany** for the keyword, because
Google rewards the format it has chosen for that query. In step 1, look at the top ~8 organic result
titles and structures and classify the dominant format:
- **Listicle / Tipps / Schritte** — titles like "11 Tipps", "10 Schritte", "5 Tipps für …". If most
  top results are numbered tip/step listicles, the article MUST adopt that format: numbered, actionable
  H2s ("1. …", "2. …"), each a concrete, do-this tip. Do NOT impose a thematic-guide structure on a
  SERP that rewards a listicle. This is one of the strongest, most-ignored ranking signals.
- **Guide / definitional** ("Was ist X") → thematic sections.
- **Comparison / vs** → comparison table + criteria.
- **How-to** → an explicit step sequence.
Our unique material (KPIs, the HubSpot section, the beyond-insights) is folded INTO that format, for a
listicle as additional numbered tips, never bolted on beside it. Record the chosen format at
Checkpoint 1. Matching the winning format is mandatory, not a stylistic preference.

## AI Overview optimization (rank to be CITED in the AIO)
The DE SERP for many B2B topics shows an AI Overview. To be pulled into it, mirror how it is built
(observed on the live SERP: definition sentence → labeled component categories → a best-practices
list → cited sources). Concretely:
- **Definition-first, quotable.** The first sentence of the intro and of each section is a crisp,
  self-contained subject-verb statement that answers the query on its own (extractable without
  context). Avoid opening a section with a story when the query wants a definition.
- **Labeled categories over prose.** Where the topic has parts (e.g. implizit vs explizit), present
  them as clearly labeled, parallel blocks or a short list. AIO pulls structured, labeled content.
- **A best-practices / rules cluster** that names the exact levers the AIO tends to surface (for
  scoring: negatives Scoring, MQL/SQL-Schwelle, Feedbackschleife).
- **Question H2s matching the PAA**, each answered in the first 1-2 sentences (already required).
- **Tables and tight lists** for anything comparative or enumerable (matrix, criteria, KPIs, B2B/B2C);
  the AIO and featured snippets extract these preferentially.
- Being cited in the AIO is the realistic head-term win, so treat citability as a first-class goal,
  not a side effect.

## Section HTML
Each section is exactly one `<h2>…</h2>` followed by `<p>` paragraphs, optional `<h3>` and
`<ul>`/`<ol>`. ~220-320 words. No intro, no overall title, no `<h1>`, no FAQ inside a section, no
repetition of the overall topic. Never write "in unserem Beitrag/Artikel/Guide zu X" or promises of
further content — internal links are added later onto existing phrasings.

## Image plan (STEP8)
- **cover — REUSE an existing W4 house header (do NOT generate by default).** The real Marketingblatt
  headers come from ONE specific flat-illustration series; an AI image is only a lookalike and never a
  pixel-perfect match, so the DEFAULT is to reuse a real house asset from the HubSpot File Manager.
  - Search Files for `W4_Header_image` / `Header_image` (Files v3 `/files/v3/files/search?name=...`).
    The relevant ones are the wide flat-illustration banners (~`3061x883` / `2800x770`, ~3.6:1). There
    are ~98 of them, many topic-specific (Video Marketing, Online Communities, B2B Content Marketing,
    Top 5 Marketing Trends, Workflow Automation, …).
  - Pick the **closest topic match**; if none fits, use a generic branded banner, e.g.
    `W4_Header_image_General_blog_post_image_red_2800x770px.png` or
    `W4_Header_image_B2B_Content_Marketing_2800x770px.png` (has magnet + envelope, good for lead/content
    topics). Set the chosen file URL as `featuredImage`. Reuse across posts is normal and fine.
  - Show the picked header at Checkpoint 2 so the user can swap it for another from the library.
  - **Generate a NEW banner ONLY if the user explicitly asks.** Then approximate the house style as
    closely as possible (flat vector "tiny people", soft blob backdrop, pastel clouds, four-point
    sparkle stars, fern/leaf plants in the corners, thin horizon line, **coral red `#E2231A` accent +
    navy `#1F2D3D` figures**, lots of white space, aspect ratio `21:9`, absolutely no text/logo) and
    tell the user it only approximates the stock series, it is not pixel-perfect.
  - Alt text is entity-aware, no keyword stuffing.
- **inbody** (from existing HubSpot assets only): max 2-3 images that give a section REAL value (e.g. a
  HubSpot-UI screenshot showing a described step). Decoration is not value; an empty array is the
  normal case. Each: `after_h2` = exact H2 text, `url` = exact URL from the HubSpot file search (never
  invented), `alt`, `caption`. Every `<img>` needs alt text.
