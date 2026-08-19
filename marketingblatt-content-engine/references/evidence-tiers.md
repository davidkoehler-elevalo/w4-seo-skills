# Evidence tiers & fresh stats (binding)

Combines the n8n "Fresh Stats (Claude web_search)" rules with the Paoli evidence-tiering method.
Goal: 3-5 recent, real, verifiable statistics for DACH/B2B, plus real practitioner questions.

## Sourcing rules (from the n8n Fresh-Stats prompt)
- Recency: 2024-2026, relevant to B2B marketing in the DACH region (Germany, Austria, Switzerland;
  HubSpot, CRM, marketing automation, AI where it fits).
- Every stat needs a real, web-verified source. **Prefer the PRIMARY source** — ideally the original
  study publisher (e.g. bitkom.org itself, HubSpot Research). A reputable secondary source (trade
  media) is allowed only if the original is not publicly accessible; then format `source_name` as
  "Original-Herausgeber via Medium".
- **No URLs behind login or paywall.** Statista links on `/prognosen/` or `/statistik/studie/` often
  redirect to a login page — avoid unless the page is publicly readable.
- Avoid famous undated classic stats (e.g. "70% aller CRM-Projekte scheitern") UNLESS you find the
  concrete, dated primary study with a public URL. The quality gate flags the 70%-CRM zombie stat.
- **Invent no numbers.** Only use `source_url`s that came from your actual web-search results. Prefer
  2-3 solidly-sourced stats over a fabricated fifth. An empty set `[]` is the correct answer when
  nothing holds up.

## Output shape
JSON array, each item:
`{"claim":"Kernaussage","value":"konkrete Zahl","year":"Jahr","source_name":"Herausgeber/Studie","source_url":"URL"}`

## Tiering (Paoli method — record the tier per stat)
- **Tier 1 — primary & citable:** original study / dataset from the publisher. Anchor the article to
  these. (In Paoli this was the Kirby-Madden survey; here it is Bitkom, HubSpot Research, official
  statistics offices, etc.)
- **Tier 2 — reputable secondary:** established trade media reporting a named study. Use only if the
  primary is not public; name both.
- **Tier 3 — practitioner / community signal:** Reddit, LinkedIn, forums. NOT a citable statistic —
  use to surface real questions, pains, and angles, never as a numeric claim in the body.

## Community mining (Tier 3)
`WebSearch` Reddit (r/marketing, r/hubspot, German marketing subs), LinkedIn, and practitioner forums
for the real questions and frustrations behind the topic. Fold genuine ones into `must_answer_questions`
and the FAQ. This is where "what people actually ask" comes from, beyond the PAA box.

## Verification (mandatory before use)
Run the verifier on the candidate array:
```
bash scripts/verify_stat_urls.sh '<json-array>'
```
It GETs each `source_url` without following redirects and reports status + a paywall/login heuristic.
Keep only stats whose URL is live (2xx), non-redirecting, and not a login/paywall page. Fail-open:
drop the bad ones, keep the solid ones, proceed even if the set shrinks to 2-3 or 0.
