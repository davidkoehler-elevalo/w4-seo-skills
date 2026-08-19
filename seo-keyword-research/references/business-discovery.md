# Phase 0: Business discovery

Runs before anything touches Ahrefs. Purpose: the seed quality (Phase 2) and the pruning rubric (Phase 6) are only as good as the understanding of what the client actually sells, to whom, and what is explicitly out of scope. Guessing this from the homepage is the root cause of bad keyword lists.

## Sources, worked in this order

1. **Briefing material from the user.** Ask once, concretely: positioning documents, sales decks, persona documents, existing keyword lists, known exclusions, priority product lines. If nothing exists, say so in the brief and continue; do not stall.
2. **The website, read properly.** Fetch and read, not skim: homepage, product overview plus every product line page, application pages, industry pages, service pages, 2-3 case studies or references, about page. Note the client's own terminology per page.
3. **How the market currently finds them.** Ahrefs organic-keywords for the domain, top ~100 by traffic, plus GSC top queries if access exists. This shows the demand language, which often differs from the client's in-house language (the site says "Auftragskopf", the market searches "hotmelt düse").
4. **Adjacent context.** Once competitors are known: how they position the same product space, which terms they own. One pass, not a full analysis; the full competitor harvest comes later.

## Output: business_brief.md

Fixed structure. Every substantive statement carries its source in brackets: a URL, a briefing document, an explicit user answer, or the marker `[inferred]`. Inferred statements are the ones the user must look at.

1. **What the company sells.** Concrete list: product lines, systems, services, consumables. No marketing language.
2. **What it does NOT sell / out of scope.** The single most valuable section for pruning, and the one the website never states. Ask the user directly: adjacent product categories the client does not serve, customer types they do not want (e.g. consumers, hobbyists), applications they cannot deliver. If the user cannot answer for the client, mark the section open and treat affected keywords as borderline later, never as relevant.
3. **Who buys.** Roles, industries, company types, and the buying situations (new line, retrofit, replacement parts, service contract). Distinguish the searcher from the decision maker where they differ.
4. **Markets and languages actually served.** Not where the website has language versions; where the business sells.
5. **Commercial priorities.** Which product lines or segments matter most, if the user knows. Determines nothing in the harvest (relevance stays volume- and priority-agnostic) but everything in later prioritisation.
6. **Terminology map.** Synonym pairs and DE/EN pairs for the core entities, in-house term vs market term, spelling variants worth harvesting separately. This feeds directly into the seed table.
7. **Open questions.** Whatever the sources could not answer.

## Checkpoint

Present the brief. **Hard stop until the user confirms or corrects it.** Corrections are edited into the brief with source `[user, <date>]`. Every downstream artefact (scope map groups, seeds, pruning rubric sections 1-2 and 4) cites this document rather than restating the business from memory.

If during a later phase something contradicts the brief (e.g. rankings reveal a product line the brief missed), stop, raise it, update the brief with the user, then continue.
