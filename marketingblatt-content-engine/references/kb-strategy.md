# KB / brand alignment gate (binding)

Lifted from the n8n "KB Alignment Gate". Run TWO rounds against the draft, then apply only clear,
bounded fixes. Sources with a year up to and including the current year are time-plausible and NOT a
fabrication signal.

## Round 1 — Alignment (style + SEO principles)

**Style (always):** `ihr`-address (Sie/du are violations); Swiss Hochdeutsch (`ß` forbidden, always
`ss`; money in CHF); no em dashes; no AI tells; human cadence; max one colon per section and never as
an announcement drumroll; no Erstens/Zweitens symmetry; every statistic with source + year, cited
inline (source name in the sentence, the number is the `<a>` anchor to the primary source; bracket
citations "(Quelle: X, Jahr)" and an end-of-article sources block are violations). `sondern` antithesis
max 2x (more → aiTells). More than one announcement colon per section → aiTells. **Promotional score:**
the BODY must read as a neutral expert piece. Allowed (house voice) is ONE soft service CTA as the
final paragraph (HubSpot Diamond Partner + one relevant W4 service + "sprecht uns an"), plus optionally
one proof case if it fits naturally. Promo inside the body, a second Diamond-Partner mention, or more
than one CTA is a med style violation (in aiTells). Voice:
nüchtern-faktisch (not permanently contrarian), max 1-2 dry quips, max 2 fictional scenarios per
article, NO term definitions in body text (belehrende "X, also Y," inserts are violations; definitions
belong in FAQ), sender is an experienced "wir", Fazit = 2-3 takeaways without counting, CTA starts
with a question.

**SEO principles** (only if the article is about SEO/ranking; weights in parentheses):
- P9 Search intent before keywords (9/10)
- P2 Click satisfaction / NavBoost (8/10, contested): long-click, no CTR tricks
- P4 Topical depth & authority (8/10): clusters, not single keywords
- P3 Brand demand (8/10)
- P1/P7 Link quality & placement (9/10): relevance over volume, in-content, natural
- P8 Entity & schema (7/10)
- Technical: indexability 9/10 is the gate; mobile-first 7/10; Core Web Vitals only 5/10 (tiebreaker)
- P6 Freshness 5/10: query-dependent
- P10 E-E-A-T only 5/10: NOT a direct ranking factor; a rater concept via proxies (isAuthor,
  contentEffort, originalContentScore). Never present it as a score or a strong/direct ranking factor.

## Round 2 — Do-no-harm (active damage; flag with severity low|med|high)
- Keyword stuffing / unnatural repetition → search-intent-match & NLP (high)
- Format mismatched to intent → search-intent-match (high)
- Thin, duplicate, or cannibalising sections → site-quality (Panda) & topical focus (med/high)
- Manipulative/bought links, unnatural anchors → natural-link-profile (Penguin) (high)
- Money links in footer/boilerplate vs main content → link placement (med)
- More than 6 internal links in the body → link inflation (med)
- Passages only understandable in context ("wie oben erwähnt") → passage scoring & AI citability (low)
- Clickbait title that doesn't hold, or intrusive elements → click satisfaction / pogo-sticking (med)
- E-E-A-T or CWV presented as a strong/direct ranking factor → misinformation (high)
- Invented number, missing source, or a quantitative claim without an inline source link (expected
  format: the number is the anchor text of an `<a>` link, source name in the sentence) → trust (high)
- Stat source is a secondary aggregator/blog instead of the original publisher → trust (med)
- Famous undated industry stat without a concrete primary source (e.g. 70%-CRM-fail) → fabrication (high)
- NO information gain: no single non-trivial insight the top results lack → unique-value (med)
- Own-success numbers ("wir haben bei einem Kunden X erreicht") without context → fabrication (high).
  A named W4 reference case linking to w-4.ch satisfies the context requirement, but proofs are OPTIONAL
  and off by default: there is no per-article quota, and a proof that reads as forced or "reingequetscht"
  is itself a quality flag (med) → drop it. Most articles carry none.
- Entity only in body text instead of H2/H3 → entity-clarity (low/med)
- Faked freshness (date without real change) → historical-data (low)

## Scoring & patches
`alignmentScore` 0-100. Verdict: **PASS** (≥85 and no harm flag), **REVIEW** (60-84 or only low/med
flags), **FAIL** (<60 or any high flag). Do not proceed to checkpoint 2 with an open high flag.

Patches: only unambiguous style/KB violations. `find` is an exact substring FROM the article; `replace`
is the corrected version (preserve meaning; never remove stats, sources, links, or headings; never
insert a dash). Max 6 patches, `find` ≤60 chars, `replace` ≤120 chars, never delete whole paragraphs.
