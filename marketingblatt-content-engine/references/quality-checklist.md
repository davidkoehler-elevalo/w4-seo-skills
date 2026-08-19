# Final quality gate (deterministic)

Lifted from the n8n "Quality Check" code node (v1.8.x). Run these checks against the FINAL `postBody`
before checkpoint 2. First normalize, then check. A HIGH issue must be fixed before publishing; do not
just prefix `[REVIEW]` and ship.

## Normalize first (belt and braces)
- **Invisible Unicode (deterministic, run before everything else).**
  `bash scripts/clean_invisibles.sh <body-file>` — strips zero-width space / non-joiner, soft hyphen,
  word joiner, bidi controls and Unicode tag characters, and normalizes exotic spaces. Emoji glue,
  flag sequences and script joiners are preserved, so visible copy never changes. Idempotent, so a
  second run on a clean body reports `changed: 0`. Fails open when the cleaner is not installed.
- Replace every `ß` → `ss`.
- Replace ` — ` / ` – ` (dash with surrounding spaces) → `, ` and any remaining `—`/`–` → `, `.
- Apply the same to the title.

## HIGH issues (block publish)
- **link_href** — any `<a>` whose `href` is not a valid `http(s)://` URL.
- **link_in_heading** — any link inside `<h2>`/`<h3>`.
- **dangling_promise** — "unserem Beitrag/Artikel/Guide/Leitfaden" with no `<a>` within ~120 chars.
- **stat_links** — stats were available but no `<a>` has a digit in its anchor text (no number-anchored
  citation exists).
- **zombie_stat** — the undated "70% … CRM/Projekte" classic without a source link within ~150 chars.
- **faq_answers** — a FAQ question whose following `<p>` answer is shorter than 120 chars.
- **sondern_antithesis (high)** — `sondern` used more than 4 times (budget is 2; >2 is med, >4 is high).
- **antithesis_without_sondern (high)** — the SAME rhetorical figure written without the word, which a
  `sondern` count silently misses. Budget is the same 2 total, counted together with `sondern`. Detect
  all of these, not just the literal word:
  - `nicht …, sondern …`
  - `ist kein/keine …, sie/es/er ist …` ("Diese Zahl ist keine Statistik, sie ist eure Ausgangsgrösse")
  - `ist nicht …, es ist …` ("ist keine technische Frage, es ist eine fachliche")
  - `… ist X und nicht Y` ("das Mittel und nicht das Ziel")
  - `braucht kein …, braucht nur …`
  Regexes that catch the family:
  `\bnicht\b[^.]{2,70}\bsondern\b` · `\b(kein|keine|keinen)\b[^.]{2,60},\s*(sie|es|er|das)\s+(ist|sind)\b`
  · `\bist\s+(keine?n?|nicht)\b[^.]{2,60},\s*(es|sie|er)\s+ist\b` · `\b(ist|sind)\s+\w+[^.]{0,40}\bund nicht\b`
  Rewrite affirmatively. `brand-voice.md` bans the "Das ist nicht A, das ist B" formula outright, so a
  clean `sondern` count is not evidence the figure is absent.
- **punchline_fragment (high)** — a short fragment closing a paragraph right after a benefit or list
  sentence ("Dieselbe E-Mail, ein völlig anderer Anlass."). Allowed only when it sharpens the sentence
  immediately before it and stands alone. Flag any sentence under 7 words that ends a `<p>`.
- **authority_trope (med)** — `die eigentliche …`, `im Kern`, `in Wahrheit`, `die wahre …`,
  `worauf es wirklich ankommt`, `letzten Endes`, plus aphorism formulas of the shape "X ist das Y von Z"
  and "X ist das Mittel und nicht das Ziel". Replace with the concrete claim.

## MED issues (fix if reasonable)
- **internal_link_count** — internal links to `blog.marketingblatt.com` not in the 5-6 range.
- **internal_links_per_section** — any H2 section with more than 1 internal link.
- **industry_pct_without_link** — a sentence with a percentage but no source link and no CHF/assumption
  context.
- **drumroll_colons** — any section with more than 2 colons.
- **aus_unserer_sicht_tic** — "Aus unserer Sicht" more than twice.
- **faq_h2** — not exactly one "Häufige Fragen" H2.
- **faq_count** — fewer than 5 FAQ questions (min 5).
- **fazit_h2** — no Fazit H2.
- **h2_count** — fewer than 4 content H2s.
- **intro_box** — "Das Wichtigste in Kürze" box missing.
- **img_alt** — any `<img>` without alt text.
- **ascii_umlaut_faq** — literal "Haeufige Fragen" instead of "Häufige Fragen".

## LOW issues (report only)
- `eszett_stripped`, `em_en_dash_stripped` — counts of what normalization removed (should be 0 if the
  draft already followed the rules).
- `invisible_unicode_stripped` — the `removed` counts from `clean_invisibles.sh`. Non-zero is normal
  for model-written HTML; it is fixed automatically, just report it.
- `nbsp_to_space` — literal U+00A0 rewritten to a plain space. Expected on German copy, because the
  house pattern for "25 %", "10 000" and "CHF 1'200" is the `&nbsp;` **entity**, which the pass leaves
  untouched. If a specific spot must not break across lines, put `&nbsp;` there rather than a literal
  non-breaking space.
- Triads count ("A, B und C") — informational.

## Comprehensiveness, chunk & link checks (Paoli — HIGH)
- **missing_consensus_asset** — an asset most/all top-5 competitors include (points matrix / worked
  example, step-by-step build, comparison table, checklist) is absent. Blocker.
- **missing_consensus_entity** — a must-cover entity from the step-3 table does not appear. Blocker.
- **too_short_vs_serp** — the article is materially shorter / shallower than the top competitors
  (e.g. a definition-only piece against a SERP full of worked examples). Blocker.
- **thin_chunk** — a section does not answer its own heading self-containedly, or is generic filler
  rather than a specific point. Fix or cut.
- **bad_link_neighbourhood** — an external link points to a forum, SEO-spam, or a non-authoritative
  source instead of a primary/authoritative one. Replace.

## Result
Pass = zero HIGH issues. If the deterministic script form is wanted, this logic is a straight port of
the n8n Quality Check node and can live as a small JS/Python helper; for the skill, apply it as a
review pass over the body and fix HIGH issues in place.
