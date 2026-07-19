# Data Sources And Landing Procedures

Facts below were last verified 2026-07-19; re-verify counts and layouts at run time (vendor data layouts move between versions).

## Claude Code

| Source | Path | Notes |
|---|---|---|
| Auto-memory files | `~/.claude/projects/<project>/memory/*.md` | Distilled facts with frontmatter; `MEMORY.md` is the index. Richest distilled layer. |
| Prompt history | `~/.claude/history.jsonl` | One JSON per user submission: `display`, `project`, `timestamp`. Interactive sessions only; retention may start later than transcripts. |
| Full transcripts | `~/.claude/projects/<project>/<session-id>.jsonl` | Complete conversations. User messages: `type=="user"`, skip `isMeta`, skip `userType != "external"`, skip tool_result-only content. Contains non-interactive runs absent from history. |
| Skill-eval sessions | project dirs whose name maps to a skills repo | Synthetic "simulate the skill-selection step" prompts; exclude after sampling. |

## Codex

| Source | Path | Notes |
|---|---|---|
| Session rollouts | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | `payload.type=="message" && role=="user"`; also `event_msg`/`user_message`. Skip `<`-prefixed environment wrappers and `data:image` pastes. Same message can appear twice per file; identical rollout copies exist — dedupe. |
| Session index | `~/.codex/session_index.jsonl` | Thread names + updated timestamps; cross-check rollout coverage. |
| Prompt history | `~/.codex/history.jsonl` | Sparse; sessions are the real corpus. |
| Automatic memories | `~/.codex/memories/` and `memories_1.sqlite` (`stage1_outputs.raw_memory`, `rollout_summary`) | Feature is off by default (`[features] memories = true` in `~/.codex/config.toml` enables it); empty store usually means feature off. |
| Goals | `~/.codex/goals_1.sqlite` (`thread_goals`) | Often empty; check, do not assume. |

## ChatGPT (desktop app)

`~/Library/Application Support/com.openai.chat/` holds only app-pairing data; conversation history and Memory live server-side. Report this and offer the user paths: Settings → Personalization → Memory (copy the list), or Settings → Data Controls → Export data.

## Extraction

`scripts/extract_user_messages.py --out <dir>` writes per-project delta files (transcript user messages not present in prompt history) plus a stats line: files scanned, messages found, delta count, interrupt count. Options: `--claude-dir`, `--codex-dir` override defaults; stdlib only, read-only.

## Dedupe Baseline

Before proposing any candidate, grep for its concept in:

- shared core rules: `~/agent-manager/agent-rule/rules/src/shared/core.md`
- managed skill bodies: `~/Documents/github/agent-skills/*/SKILL.md`
- prior governance decisions: agent-manager project memory (records rejected promotions — do not re-litigate them)

## Landing

- Core rule: edit `agent-rule/rules/src/shared/core.md` → `make rules-build` (token-budget test lives in `tests/test_rule_budgets.py`; a raise must be documented there with its delete-test rationale and symmetric-rollback note) → `make rules-apply` → diff the distributed files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, Antigravity plugin rules) against dist.
- Skill amendment: edit the skill in the dev repo → add an eval case → run the repo contract tests → commit per repo convention (no AI attribution).
- After the user approves pushing: push, then `make bump` + apply in agent-manager, and spot-check what each agent actually loads.
