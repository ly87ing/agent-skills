# Blast-radius checklist

Read this when filling the checklist rows in SKILL.md. Each row lists the questions that decide "affected / not affected / unknown" and the evidence that settles them. An unknown row is a valid answer only when it names who can answer it.

## Entry routes and path prefixes

- Which gateway locations, ingress rules, or reverse-proxy blocks route to the component today? Read the gateway configuration, not the service's own docs.
- Which path prefixes do clients use, and do any clients hard-code the old prefix? Check client inventories and the access log for the prefix.
- Is the component on an allow-list (anonymous paths, WAF exceptions, internal-only routes) that the new owner must inherit?
- After the change, which prefixes must keep answering, for how long, and who closes them?

## Environment-varying configuration

- Which of the component's keys take different values per environment or customer? Diff the config repository across environments.
- Which of those keys are rewritten by deployment tooling (host, scheme, port substitution) rather than set directly?
- Where will each key live after the change: the config repository, a template, or code? A key that moves into code stops varying.
- Which keys become orphans and must be removed from the config repository, and in which release?

## Storage and shared volumes

- What does the component mount, and does any other component mount the same volume or path?
- Which init containers, scripts, or command arguments name the path (a literal-string search, not only a manifest field)?
- If the mount is removed, who else reads what the component wrote there, and through which path do they read it afterwards?
- On multi-node sites, is the path node-local or shared, and does the change alter that?

## Monitoring, inspection, scheduled jobs

- Which probes, health checks, and dashboards name the component or its endpoints?
- Which inspection or audit jobs list it, and must they stop, move, or be rewritten?
- Which scheduled jobs (cron, timers, refresh loops) run inside the component, and where do they run afterwards?

## Multi-replica consistency

- How many replicas can the new owner run, and does any state (a cache, a file, an in-memory map) need to agree across them?
- Does a "refresh on publish" notification reach every replica, or only the one that received it? Prefer a bounded refresh interval to a notification that cannot reach all replicas.
- Does the refresh have a cost bound (CPU, IO, requests per interval)?

## Upgrade path and rollback

- If a customer skips every intermediate version, does the final version still migrate correctly on its own? Migration logic must live in the final version, be idempotent, and be guarded by a marker.
- Are upgrade scripts cumulative and additive in this release, with deletions deferred to a later one?
- What is the rollback unit: the whole bundle, one service, or one script? Design for the real unit.

## Other teams' actions

- What must another team change (a client, a gateway, an inventory, a certificate), and by when?
- What blocks if they do not, and is that a stop for the release or a degradation?
- Is each action written where that team will read it, with an owner?

## External interfaces

- Which interfaces does the component expose, and which callers outside this scheme use each one? Count from access logs with a same-period baseline for a known-live interface.
- What does each external caller see after the change (same path, redirect, deprecation window, hard removal)?
- Who signs off that the removal of an interface is safe?
