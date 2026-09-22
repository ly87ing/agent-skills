---
name: solution-shaping
description: Shape a solution before anything is built or edited — an architecture or migration scheme, a service split, merge, or retirement, an upgrade plan, a fix approach with several candidates, or a comparison of approaches. Use when asked to analyse how something should be changed, to think from zero about the right design, to compare options and say which to follow, to judge whether a scheme is complete or has gaps, or to turn a many-constraint discussion into one plan. Collects every constraint first, inventories live versus dead capabilities, names the deployment model each argument assumes, walks a blast-radius checklist, grades claims as observed, inferred, or unverified, and briefs the implementer. Not for editing the code once the scheme is agreed, nor for proving a built change works.
---

# Solution Shaping

A scheme is a set of constraints, a target that satisfies all of them, and a path from here to there, with every claim carrying its evidence grade. This skill exists because requests such as "analyse how to migrate this service", "think from zero about how these services should be architected", or "is this scheme complete" had no owner: `change-discipline` starts when existing code is edited and `verification` when something built is proved. In the sessions it is distilled from, seven successive schemes were produced by re-arranging the previous one each time a new constraint arrived, and the user asked eight separate times for a dimension the scheme had left out.

## Workflow

1. **Collect the constraints into one table before proposing anything.** Columns: constraint, source (the user's words, code, an environment, a policy), what it rules out. Every later turn adds to this table first. When a new constraint invalidates a premise of the current scheme, re-derive from the table instead of patching the scheme. Case: after seven locally re-arranged versions, the user asked for a review of the whole discussion; the retrospective found each version had answered the latest constraint alone, and a scheme built from the full table came out different from all seven.
2. **Inventory what is live before deciding what to move.** For a migration, merge, split, or retirement, list each capability, interface, job, and data set with a status and its evidence: live (traffic, callers, config that names it), dead (absence with a same-period baseline that shows the probe would have caught use), or unknown. A zero hit count with no baseline is not evidence of absence. Case: an architecture database listed three callers of a service from a static URL scan; opening the repositories showed one was a retired project and another a vendored copy of old code, so the real caller count was one.
3. **Fix the target state in one sentence and name the deployment model every argument assumes.** An argument that holds under independent deploys can fail under bundled upgrades where customers skip intermediate versions, under single-replica sites, or on shared hosts; write the model next to the target. Use one argument in one direction only. Case: "independent failure domain" was used to reject merging a service and, in the same scheme, to justify adding a deployment for it; under the real bundled-upgrade model neither use held, and the deployment was dropped.
4. **Walk the blast-radius checklist and mark every row.** Record affected, not affected, or unknown for each row of the table below; an unknown row names who can answer it. Detail per row lives in [references/blast-radius-checklist.md](references/blast-radius-checklist.md). Case: in one migration discussion the user asked, one question at a time, about gateway routes, path prefixes, the shared volume, the inspection job, environment-varying config keys, and the actions other teams had to take; each was a row this table would have filled the first time.
5. **Grade every load-bearing claim.** Observed (with where), inferred (from what), or unverified. Keep a number's qualifier with it when it is compressed into a table. Never fill in a name, an owner, a presenter, or a date the source does not give; write TBD. Case: a meeting outline assigned presenters no one had named, and the user's reply was that unknown things are not to be invented.
6. **Choose the scope of a fix or change on a ladder and say which rung.** No special case for the reported sample; a generic rule inside the component you own; never a contract imposed on producers you do not control. The case behind this rule is in `change-discipline`.
7. **Close with the decision and the first step, then hand off.** State the decision the reader has to make, the smallest step that proves the direction, and the brief for whoever implements it, per [references/delegation-brief.md](references/delegation-brief.md). Acceptance of the built result belongs to `verification`.

## Blast-radius checklist

| Row | Question to answer | Evidence that answers it |
| --- | --- | --- |
| Entry routes and path prefixes | Which gateway locations, prefixes, and allow-lists reach the component, and which must change? | Gateway config, ingress rules, allow-list files |
| Environment-varying configuration | Which keys change per environment, and do they live in the config repository or in code? | Config repository diff, deployment templates, rendered values |
| Storage and shared volumes | What does the component mount, who else mounts it, and what breaks if the mount goes? | Manifests, mount lists, init-container arguments |
| Monitoring, inspection, scheduled jobs | Which probes, inspections, crons, and dashboards name the component? | Monitoring config, inspection lists, cron definitions |
| Multi-replica consistency | With more than one replica, how do caches, files, and notifications stay consistent? | Replica counts, refresh mechanisms, event paths |
| Upgrade path and rollback | Does the change survive a skipped intermediate version, and what is the rollback unit? | Upgrade scripts, migration ordering, bundle definition |
| Other teams' actions | What must another team do, by when, and what blocks if they do not? | Interface inventory, ownership list |
| External interfaces | Which callers outside this scheme use the component's interfaces, and what do they see after? | Access logs with a same-period baseline, client inventories |

## Completeness check

| Before calling the scheme complete | Passes when |
| --- | --- |
| Constraints table | Every row has a source |
| Live-dead inventory | Every item has evidence, and every "dead" has a baseline |
| Target state | One sentence, with the deployment model named |
| Blast-radius rows | Every row marked; every unknown names who answers |
| Claims | Every load-bearing claim graded |
| Open decisions | Listed with who decides |
| First step | Named, and it proves the direction |

A scheme missing a row is reported as incomplete, not padded to look complete.

## Example

Request: retire service X and fold its two capabilities into services Y and Z.

> **Constraints**
>
> | Constraint | Source | Rules out |
> | --- | --- | --- |
> | Customers upgrade the whole bundle and may skip versions | User | Any step that needs an intermediate version to have run |
> | No database schema changes this release | User | Moving tables; dual writes |
> | Y and Z are single-replica at most sites | Deployment manifests | Designs that rely on replica-local caches staying in sync |
>
> **Inventory**
>
> | Capability | Status | Evidence |
> | --- | --- | --- |
> | Version lookup | Live | 13,000 requests/day in gateway logs |
> | Legacy upload endpoint | Dead | 0 requests in 30 days against 95,000 for the sibling endpoint |
> | Grey-release mapping | Unknown | Read from a file with no access log; owner of the file TBD |
>
> **Target:** Y serves version lookup and Z serves uploads, reading X's tables in place, deployed as one bundle in which every migration step runs in the final version.
>
> **Blast radius:** routes affected (two prefixes move to Y); shared volume affected (X's mount goes, Z writes through the gateway instead); other teams unknown (client team must confirm the old prefix can close).
>
> **Decision needed:** whether the old prefix stays for one release. **First step:** serve version lookup from Y behind the old prefix and diff responses against X on real requests for a week.

## Ownership

`change-discipline` owns the edit once the scheme is agreed: history, callers, symptom-is-not-spec. `verification` owns proving the result and accepting delegated work. `reader-facing-writing` owns the document the scheme is written into, including the design-doc skeleton. `safe-merge-review` owns merges.
