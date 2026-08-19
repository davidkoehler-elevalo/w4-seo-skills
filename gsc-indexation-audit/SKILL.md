---
name: gsc-indexation-audit
description: Check which URLs of a site are actually in Google's index and get the missing ones indexed. Use whenever David asks "are these pages indexed", "warum ist die Seite nicht im Index", "Indexierung prüfen/anfordern", "index check", "indexation audit", "request indexing", "wie viele Seiten sind indexiert", or after a relaunch / new page batch / sitemap change. Covers the bulk URL Inspection API sweep over a sitemap, the results Sheet, the hard 11-requests-per-day GSC cap and how it is driven from Chrome, and the nightly verification job. Contains the API non-determinism trap that produces false "orphan page" diagnoses.
origin: agent-created
created: 2026-08-12
updated: 2026-08-16
---

# Indexation audit and indexing requests (Google Search Console)

Verified end to end on `https://www.w-4.ch/` on 2026-08-11: 668 sitemap URLs inspected in ~10 min,
546 indexed / 122 not, 0 API errors; 11 requests submitted, 9 of them indexed the same day.
Reference implementation lives in `~/.w4-indexbot/` (W4-specific constants at the top of each file).

## Phase 1 — bulk inspection

Pull every URL from `sitemap.xml` (follow sitemap indexes, dedupe via a set), then one call per URL:

```
POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect
Authorization: Bearer $(gcloud auth application-default print-access-token)
{"inspectionUrl": "<url>", "siteUrl": "<property, exactly as in GSC>", "languageCode": "de"}
```

Rules that matter:

- **`verdict == "PASS"` is the only reliable "is in the index" flag.** Never infer indexation from
  impressions or from a coverageState string alone.
- `languageCode` localises the `coverageState` strings. Pin it, or your string matching breaks
  between runs.
- Quota is **2000/day per property, 600/min**. 8 threads is the sweet spot (668 URLs ≈ 10 min).
  Add exponential backoff for 401/429/500/503 and refresh the token every ~45 min.
- Property must be the exact GSC property string (`https://www.w-4.ch/`), not a normalised variant.
- macOS python3 has no CA store: `export SSL_CERT_FILE=$(python3 -c "import certifi;print(certifi.where())")`.
- Persist the raw JSON per URL (verdict, coverageState, robotsTxtState, indexingState,
  pageFetchState, lastCrawlTime, crawledAs, userCanonical, googleCanonical, sitemapListed,
  referringUrls). The re-runs are cheap only if you never have to re-fetch.

### The trap: the API is non-deterministic for non-indexed URLs

Measured with 366 calls (122 URLs × 3): **60% of non-indexed URLs flap** between
`"URL is unknown to Google"` (referringUrls = 0) and `"Discovered - currently not indexed"`
(referringUrls = 3-5) between identical calls seconds apart. The degraded response returns an empty
`referringUrls` array, which reads exactly like an orphan page and produces a confident, wrong
"these pages have no internal links" diagnosis.

- **Never assert a non-indexed URL's referring-link count from one snapshot.** Take best-of-3 and
  require agreement, or verify internal links by crawling the live hub pages.
- Indexed URLs (`PASS`) never flap (0/122). Flipping a row to "indexed" is safe to automate.

## Phase 2 — results Sheet

Owner must be `dkohler@w-4.com` via gcloud ADC (the Drive MCP account cannot own multi-tab sheets).
Three tabs: `Übersicht` (summary + documentation rows), `Nicht indexiert` (the work queue),
`Alle URLs` (raw). Queue columns A-M are David's; the workflow state lives in
**L** (`Offen` / `Angefordert` / `Nicht anfordern`) and **M** (request date).
Automation only ever writes L, M and N-R — never clears cells, never touches `Nicht anfordern` rows.

Prioritise the queue by business value before anything else: service pages, then products, then the
rest. Downloads and paginated news last.

## Phase 3 — requesting indexing

There is **no API for this**. The Search Console API is read-only for inspection, and the Indexing
API only covers JobPosting and BroadcastEvent (non-approved quota has not triggered crawls since
Oct 2025; using it for other page types risks revocation). IndexNow is Bing-only. The sitemap ping
endpoint has been dead since Dec 2023. So the GSC UI button is the only lever.

- The cap is **11 requests per property per day** (measured 2026-08-11: the 12th returns "Quota
  Exceeded"). It is not perfectly stable: on 2026-08-14 the **11th** was refused after 10 successes,
  in a run where an accidental TEST LIVE URL had fired — assume live tests can eat a slot, plan for
  10-11 and treat the refusal as normal. Hard-stop on the first quota error, never retry the same URL
  — Google states a repeat request does not speed anything up.
- Deep links to `/search-console/inspect?id=...` 404. Drive the "Inspect any URL" omnibox at the top
  of the property, and `cmd+a` before typing or the previous URL sticks and you re-submit it.
- **Getting into the property: never deep-link `?resource_id=`.** Any URL carrying `resource_id`
  (or a stale `authuser=N`) bounces to `/search-console/not-verified`, which looks exactly like "this
  account has no access" and is not. Measured 2026-08-16: `authuser=4` now redirects to a sign-in
  page although the same account is signed in as Chrome's default. Working path every time:
  `/search-console/index` (no parameters) → the "Search property" picker top-left → click the
  property. The picker lists the properties even while the page says "not verified".
- The daily counter runs on the **US Pacific day, not the local one**. Measured 2026-08-12/13:
  11 requests at 23:45 CEST (= 14:45 PT) all succeeded, and the next one at 00:12 CEST (= 15:12 PT,
  still the same Pacific day) returned "Quota Exceeded". So the reset is midnight PT = **09:00 CEST**
  in summer, 09:00 CET → 08:00 in winter. Schedule the daily job after that, not after local
  midnight; the launchd job at 09:30 is deliberately just past the rollover.
- A quota error costs nothing but the attempt — the URL stays `Offen` and can go out the next day.
- UI loop per URL, ~45s: omnibox → `cmd+a` → type URL → Return → wait ~10s for the inspection panel
  → click `REQUEST INDEXING` (right side of the result card) → wait ~30s → a green **"Indexing
  requested"** overlay appears → click `Dismiss`. Confirmation that it took: the card's right side
  changes to `✓ Indexing requested   REQUEST AGAIN`. Never click REQUEST AGAIN.
- Batch the loop, but **keep every `browser_batch` under ~35s of waits**. Measured 2026-08-16: a
  batch with ~55s of waits plus two screenshots exceeds the MCP tool timeout, and the failure is
  nasty — the actions still run, but the tab's content script is left wedged and every later
  screenshot / `get_page_text` returns "Script injection timed out", including after a fresh
  navigation. Recovery is a **new tab** (`tabs_create_mcp`), then re-enter via the property picker.
  Two calls per URL is the stable rhythm: (a) dismiss → wait 3 → **click inert page area** → wait 2 →
  omnibox → wait 3 → `cmd+a` → type → Return → wait 18 → screenshot, (b) click `REQUEST INDEXING` →
  wait 25-30 → screenshot. The inert click between `Dismiss` and the omnibox is not optional:
  measured 2026-08-17, dismiss → omnibox with only waits between them still wedged the page into the
  document-wide selection state on URL 2, and adding the inert click carried the remaining 9 URLs
  without a single miss.
- **No overlay at ~28s does not mean the request failed.** Measured 2026-08-17: 4 of 11 requests
  showed a completely unchanged card at 28s and the green "Indexing requested" overlay appeared by
  ~48s. So when the screenshot looks unchanged, spend one more `browser_batch` of wait 20 →
  screenshot before doing anything else. Only if that is also empty, re-inspect the URL. Never
  re-click `REQUEST INDEXING` on a silent card — that is how you burn two slots on one page.
- **The overlay can lie in both directions.** On 2026-08-17 one URL showed
  `Oops! Something went wrong — We had a problem submitting your indexing request` while the card
  behind it already read `✓ Indexing requested   REQUEST AGAIN`, and the URL was accepted. The card
  is the truth, the overlay is not.
- **A batch that errors out ("did not respond in time", "extension is not connected") has usually
  already executed its actions.** Never re-click `REQUEST INDEXING` to "make sure" — re-inspect the
  URL instead (inspection is free and does not touch the quota) and read the card: `URL is on Google`
  or `✓ Indexing requested` means it landed. On 2026-08-16 both interruptions had gone through, and
  one of them was indexed within 20 minutes.
- **The waits around the omnibox click are load-bearing.** Clicking it immediately after `Dismiss`
  silently fails to focus, and then `cmd+a` selects the whole *document*, the typed URL goes nowhere,
  and `Return` fires the focused card control — measured 2026-08-14: it started a **TEST LIVE URL**
  run. Symptom in the screenshot: the entire page is blue-highlighted. Recovery: `Cancel` the live
  test, click inert page area, click the omnibox, screenshot to confirm the caret + history dropdown,
  only then type. A blind `Dismiss` click is safe; a blind omnibox click is not.
- The window can resize between batches (1568x784 → 1470x679 seen). Coordinates are per-screenshot:
  re-read `REQUEST INDEXING` / `Dismiss` positions from the newest screenshot, never carry them over.
- Screenshots of the GSC Overview page routinely time out for 20-30s after navigation
  ("Script injection timed out"). Wait and retry rather than treating it as a broken session.
- Automate via **CDP against a dedicated Chrome profile**, not a launched browser:
  `~/.w4-indexbot/start-chrome.sh` (port 9333, `--user-data-dir=$HOME/.w4-indexbot/chrome-profile`),
  then `node submit.js --submit --max 11`. Since Chrome 136 `--remote-debugging-port` is ignored on
  the default profile, hence the dedicated one; `connectOverCDP` also avoids `navigator.webdriver`.
  Log into that profile by hand once (headful); the session then persists, headless is fine after.
- **BROKEN since Chrome 151.0.7922.109 (measured 2026-08-14).** `connectOverCDP` against the bot
  profile dies on `Protocol error (Browser.setDownloadBehavior): Browser context management is not
  supported` — playwright-core 1.62.1 is already the newest release, and a *fresh* user-data-dir on
  the same Chrome connects fine, so it is that profile, not the Playwright version. `launchPersistent
  Context` on the same dir starts but lands on `/search-console/about`, i.e. the persisted login is
  gone too. Diagnose in this order: raw TCP to 9333 → `/json/version` over plain HTTP → connectOverCDP
  (only the last one shows the real error; `submit.js` swallows it as "no Chrome listening").
- **Fallback that works: the claude-in-chrome extension against David's own Chrome work profile**,
  which is already signed in. Same UI loop as above, ~1 `browser_batch` per URL. After the run, mark
  the rows yourself — `submit.js` normally writes L/M, and nothing else does. Use
  `python3 ~/.w4-indexbot/mark_requested.py --apply <url> ...` (dry run without `--apply`): it writes
  L/M only on rows still `Offen`, so `Nicht anfordern` and `Indexiert` rows cannot be clobbered.
  Pick the URLs with `node submit.js --queue-only --max 11`, which ranks by business value without
  opening a browser.
- **Two Chromes may be paired with the extension.** `tabs_context_mcp` then refuses to act and
  demands a choice; ask, and expect `switch_browser` (the Connect-prompt path) rather than guessing a
  deviceId. The signed-in one on David's machine is named "Work".
- `submit.js` modes: default = dry run (inspect, no click), `--submit`, `--queue-only`.

## Phase 4 — nightly verification

`/usr/bin/python3 ~/.w4-indexbot/w4_index_verify.py` — stdlib only, dry run by default,
`--apply` writes, `--notify` for macOS notifications, `--limit N` for a smoke test.
`W4_CREDS=adc` (default) or a service-account key path (RS256 JWT signed via openssl).
Re-inspects the queue, writes N-R (Status, Zuletzt geprüft, Indexiert am, Tage bis Indexierung,
Interne Links) and appends a daily row to the `Verlauf` tab. Idempotent within a day.

`run-daily.sh` is the driver and the **order is load-bearing: verify first, submit second**, so the
11 daily slots are never spent on URLs Google already indexed. launchd at 09:30
(`ch.w4.indexbot.daily.plist`), systemd units in `systemd/` for the VPS. `caffeinate -i` wraps the
run on macOS — it prevents idle sleep but does not wake a sleeping Mac, so a closed laptop skips.

**ADC tokens die after 7 days** on a Testing-mode OAuth app. For unattended runs use a service
account granted access to both the GSC property and the Sheet, or publish the OAuth app.

## What actually gets pages indexed

Requesting indexing works (82% same-day here) but is a trigger, not a fix, and 11/day means 113 URLs
take ~10 working days. Before blaming internal links, check whether Google is simply declining the
content: at W4 the biggest unindexed cluster (41 `/en/downloads` pages) was fully internally linked.
Report both levers honestly — link gaps behind deep pagination are real, thin/duplicate content is
the more common answer.
