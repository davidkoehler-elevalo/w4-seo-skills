# Phase 7: Clustering — NOT YET SPECIFIED

The user has explicitly deferred the clustering specification ("I'll get to that"). Do not improvise a clustering method.

When the pipeline reaches this phase:

1. Confirm the pruned list is signed off (kept + resolved borderline rows).
2. Ask the user how they want to cluster. Known options in this environment, for the conversation:
   - **Keyword Insights API** via the existing `keyword-insights` skill: SERP-overlap clustering plus intent classification. Costs credits per keyword; on a 2,000-3,000 keyword list, check the credit balance and estimate cost before proposing it as the default.
   - **Ahrefs parent topic** grouping: free with existing data, coarser, no intent layer.
   - **Custom SERP-overlap clustering** via DataForSEO SERP exports: full control, more work.
3. Record their answer, then extend this file with the confirmed procedure so future runs do not ask again.

Until then, this phase ends with the question, not with output.
