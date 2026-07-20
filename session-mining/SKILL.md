---
name: session-mining
description: Mine local AI-agent memory and session transcripts (Claude Code, Codex, ChatGPT) for recurring user corrections, preferences, and reusable workflows, dedupe them against currently managed rules and skills, and promote survivors into agent-manager rules or skill amendments under governed budgets. Use when asked to harvest, extract, or promote rules/skills from memory and past sessions, or to review what recent sessions should feed back into agent-manager, when a recurring workflow that no existing skill owns might warrant proposing a new one, and when a harvest has to account for its own coverage — per-source totals, exclusions, and stores that are missing or empty rather than silently skipped. Not for editing one known skill directly.
---

# Session Mining

One run = one full pass over all vendors' local memory and session data, producing deduped promotion candidates plus an auditable coverage account. The run only proposes; the user decides what lands.

## Workflow

### 1. Inventory the corpus — never sample silently

- Enumerate every source in `references/data-sources.md`. Before mining, report per source: file count, size, oldest/newest timestamps, and anything unreadable or empty.
- The failure this prevents: mining only the distilled layer (memory files + prompt history) and calling it "all sessions". Full transcripts additionally hold task books for non-interactive runs, mid-session corrections, and interruption signals.
- A documented path that is missing or empty is a finding to verify and report (layouts move between versions; some stores are off by default), not a license to skip the vendor.

### 2. Extract with the script, not by hand

- Run `scripts/extract_user_messages.py` (execute it; no need to read it into context). It pulls genuine user messages from Claude project transcripts and Codex rollouts, filters machine-injected content (tool results, meta entries, synthetic eval prompts, image pastes), truncates long pastes, and diffs against prompt history so only unmined messages remain.
- Excluded classes (for example machine-generated eval sessions) must be sampled to confirm they are synthetic before being dropped, and must appear in the coverage account with counts.

### 3. Mine with read-only subagents

- Fan out one subagent per corpus slice (memory files / prompt history / transcript delta), each returning candidates with verbatim evidence quotes, source paths, repetition counts, and a confidence level.
- Have each subagent list user-correction utterances exhaustively ("don't...", "I told you...", "why did you...") — a correction marks a rule that failed to fire, the highest-value signal.
- Give every subagent the dedupe baseline (step 4) inside its prompt so it reports increments, not restatements.

### 4. Dedupe before proposing — the false-new gate

- Grep the current shared core rules and every managed SKILL.md for each candidate's concept before calling it new. Recent harvests found roughly half of "new" findings already landed; a second-pass dedupe by the orchestrator is mandatory even when subagents were given the baseline.
- Sort every candidate into exactly one bucket: already covered / governance previously rejected (do not re-litigate) / project-specific (stays in project memory) / company-side skill territory / genuinely new.

### 5. Classify survivors and propose landings

- Always-on cross-agent habit → one line in the shared core rules; it must pass the delete test, and any token-budget raise is a deliberate documented decision recorded next to the budget check, never a green-making edit.
- Recurring craft inside one domain → amendment to the owning skill, plus an eval case in that skill's `evals/evals.json`.
- A repeated multi-step workflow with no owning skill → new-skill proposal; requires the user's explicit approval before scaffolding.
- Landing procedures, budget checks, and verification commands are in `references/data-sources.md` under Landing.

### 6. Report coverage and wait

- Deliver a coverage table (source × total × mined × excluded, with reasons) alongside the candidate list with promote/ignore recommendations and evidence.
- Local absence of a vendor's data (for example chat memory kept server-side) is itself a reported finding with the export path the user could take.
- The promote/ignore call belongs to the user. Never land rule or skill changes, and never push a repo, without explicit consent.

## Gotchas

- Emptiness is a data point, not an error: some vendor memory stores ship disabled by default, so an empty database usually means "feature off", and the sessions themselves remain the minable source.
- Exported transcript lines can duplicate messages or whole rollout files; dedupe before counting repetitions, or frequency-based confidence is inflated.
- Filter subagent report-backs and resumed-session summaries out of "user messages" — they quote the user and masquerade as new evidence.
- Verify time ranges before claiming completeness: prompt-history files and transcript retention can start on different dates.
