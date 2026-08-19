# Delivery & internal-link rules (Marketingblatt)

## Blog facts
- **Blog:** blog.marketingblatt.com, language `de`, ~345 published posts.
- **Post inventory:** the blog sitemap `https://blog.marketingblatt.com/sitemap.xml` lists every
  published post URL. WebFetch individual posts for titles/metas when scoring candidates.

## Google-Drive delivery (final step, both modes)
1. Assemble locally in `./mb-articles/`: `<slug>.md` (article markdown incl. title + meta options),
   the cleaned `<slug>.body.html` (paste-ready HTML), and the cover image.
2. Create (or reuse) a Drive folder named after the slug and upload all three files
   (Drive API with `gcloud auth application-default print-access-token`, or whatever Drive
   integration the session has).
   - Import the HTML as a **Google Doc** (`files.create` with
     `mimeType: application/vnd.google-apps.document`) so reviewers can read and comment.
   - Keep the raw `.body.html` beside it: the Doc is for review, the HTML file is the lossless
     source for the CMS paste (re-exporting HTML from a Google Doc mangles markup).
3. **Slug derivation:** from the title: strip a leading "[REVIEW] ", lowercase,
   ä→ae ö→oe ü→ue ß→ss, non-alnum→`-`, trim leading/trailing `-`, ≤80 chars.
4. **Never publish to the CMS from this skill.** The reviewer moves the approved draft into the
   blog manually.
5. Fail open without Drive access: keep the local files and report their paths.

## Internal-link candidate scoring (Filter Cluster Links port)
From all published post URLs in the blog sitemap (all ~345):
- Build dynamic terms from the topic + target keyword (drop stopwords; keep words >3 chars and 2-6
  letter uppercase acronyms lowercased).
- Base cluster terms (always considered): breeze, ki, künstliche intelligenz, hubspot, crm,
  datenpflege, lead-scoring, leadscoring, lead scoring, automatisierung, automation.
- Score each post with **boundary-aware** term matching (a term must not sit inside a longer letter
  run — "ki" must not match "Skizze"): title hit +3, slug hit +2, meta hit +1; any base-term hit +1.
- Drop posts with score 0 and no base hit. Sort by score, then newest publish date. Keep top ~16,
  each with title, meta description, url, relevance score.

## Internal-link selection (reasonable-surfer, STEP7 port)
Pick **5-6** links, ONLY from the scored candidates' exact URLs (never invent a URL; a non-candidate
URL is allowed only if it is on blog.marketingblatt.com):
1. Anchor = a descriptive 3-7 word passage that occurs EXACTLY as a substring in the article body
   (so it can be replaced safely). Never "hier"/"diesem Beitrag"; never an invented sentence.
2. Prefer placement in the first half of the section and the first two thirds of the article.
3. Max 1 link per H2 section; no anchors in headings (h1/h2/h3); no links in the FAQ block.
4. The link must serve the next information need at that spot (contextual relevance over keyword
   match); descriptive German anchor carrying the target page's main term.
5. Don't link topically-distant candidates even if they share generic marketing terms. Fewer, exactly
   fitting links beat 5-6 mediocre ones.
Prefer candidates that also appear in the cannibalization step's `internal_link_targets`.

## Inbound links (Paoli addition)
Separately, identify existing published posts that should link TO the new article (inbound), with a
suggested descriptive anchor. Report these to the user at checkpoint 2 — do not edit those posts here.

## Cover image
Generate with `mcp__nano-banana-2__generate_image` (16:9, no text). Keep it as a local file; it goes
to the Drive folder with the draft and is attached in the CMS by the reviewer.

## In-body images
Optional (empty is the norm) per `article-structure.md`; reuse an existing blog asset by URL only
when one clearly fits.
