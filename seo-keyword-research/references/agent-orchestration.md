# Agent orchestration (Claude Code / Cowork)

Only relevant where subagents exist. In claude.ai chat, run everything sequentially in one context and skip this file.

Design principle: the orchestrator holds the config and the status file; subagents hold one bounded task each and write results to disk, never back into a shared conversational state. All coordination happens through the filesystem.

## What parallelises and what does not

| Phase | Parallel? | Unit of work per subagent |
|---|---|---|
| 0 Business discovery | No | orchestrator only, reads sources and needs the user |
| 1 Scope map | No | orchestrator only, needs the user |
| 2 Seeds | Partially | one subagent per group family (applications / products / industries), each producing seed candidates; orchestrator merges the table for the human checkpoint |
| 3 Expansion | Yes, with care | one subagent per batch of 5-10 seeds. CARE: all subagents draw on the same Ahrefs API allowance. The orchestrator checks `subscription-info-limits-and-usage` first, computes a per-subagent row budget, and passes it in the task prompt. Subagents stop at their budget and report, never negotiate limits themselves. |
| 4 Rankings | Yes | one subagent per domain (client + 3 competitors + GSC = up to 5), each paginating its export to completion |
| 5 Merge | No | single deterministic script run by the orchestrator |
| 6 Pre-prune | No | single script run |
| 6 LLM pruning | Yes | one subagent per chunk file. Every subagent receives the identical rubric verbatim. Orchestrator validates each returned chunk (row count, coverage, legal classes) before accepting; failed chunks re-queue. |
| 6 QA | No | orchestrator, or one fresh subagent that did not classify, for the audit sample |
| 7 Clustering | Unspecified | stop and ask |

## Subagent task prompt skeleton (pruning chunk)

```
Task: classify keywords for relevance. Read nothing outside the paths below.
Rubric: <project>/rubric.md  (follow it verbatim; do not add criteria)
Input:  <project>/chunks/chunk_017.csv
Output: <project>/chunks_out/chunk_017.tsv
Format: keyword<TAB>class<TAB>group_id<TAB>reason  — one line per input row,
        same order, class in {relevant, borderline, irrelevant}, reason <15 words.
Do not use search volume in any decision. Do not skip or merge rows.
If a keyword is not classifiable from the string, class it borderline with reason "intent unclear".
```

## Failure handling

- A subagent that errors or times out gets its unit re-queued once; a second failure goes into status.md and to the user. No third silent retry.
- The orchestrator owns status.md exclusively; subagents report via their output files and completion messages.
- Rate limiting: if Ahrefs returns rate-limit errors, halve the parallelism, do not tighten per-call retries.

## Practical notes

- Chunk size 200-400 for pruning; 5-10 seeds per expansion subagent; adjust down if outputs show degraded per-row quality (generic reasons, class drift within a chunk).
- Keep subagent count modest (4-6 concurrent). The bottleneck is API allowance and validation, not model throughput.
