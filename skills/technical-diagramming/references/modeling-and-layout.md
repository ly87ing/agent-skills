# Modeling And Layout

Use this reference after the diagram's question and evidence boundary are known.

## Evidence Model

- Assign stable IDs from domain meaning, not display order or coordinates. A later
  layout move must not look like a new component.
- Record the evidence that supports each node and relationship while authoring. For
  repository evidence, prefer an exact revision plus repo-relative file and line when
  the line is stable enough to cite. For runtime evidence, record the environment and
  observation time. Do not embed private source locations in an artifact whose
  audience should not receive them.
- A node proves existence only at the scope of its evidence. A class or manifest can
  prove declared structure; it does not prove deployment, traffic, health, ownership,
  or usage. Show those only from matching evidence.
- Every arrow asserts at least direction and relationship. Label protocol, action,
  asynchronous behavior, trust crossing, or fallback when an endpoint pair alone
  cannot recover that meaning.

## Model Router

### Architecture

Show components, stores, external systems, deployment or trust boundaries, and the
few relationships needed to answer the question. Keep logical ownership, physical
placement, and observed runtime state visually distinct instead of mixing them into
one unlabeled container hierarchy.

### Workflow

Show the start condition, ordered actions, decision gates, responsible lane when
known, exceptions, rollback or recovery, and terminal outcomes. Do not connect steps
merely because they appear next to each other in a checklist.

### Sequence

Order participants by the main interaction. Preserve calls, returns, asynchronous
handoffs, retries, timeouts, and alternatives that change the request's meaning.
Chronology is the model; spatial proximity must not imply a call that was not authored.

### Data Flow

Show sources, transformations, stores, sinks, and boundary crossings. Label data kind,
sensitivity, batching or streaming, and retention only when evidence supplies them.
Do not present a control call as data movement or infer lineage from shared field names.

### Lifecycle

Show initial, active, waiting, failed, recoverable, cancelled, and terminal states that
actually exist, then label the event or condition for every transition. A retry is a
real transition back to an active state, not a decorative loop around a failure node.

### Comparison

Normalize both snapshots to the same question, boundary, level of detail, and stable
IDs before comparing them. Separate changed facts from layout movement. Describe
added, removed, changed, moved, and rerouted elements literally; assess consequences
from code or operational evidence outside the visual diff.

## Layout Decisions

- Start with one primary path and place secondary branches beside their attachment
  point. If no path is primary, group peers on one explicit logic such as ownership,
  trust boundary, phase, or layer.
- Use automatic layout for a small graph whose coordinates carry no meaning. Use
  authored geometry when elements must retain position across states, multiple states
  coexist in one frame, boundaries nest, or several connection classes must remain
  visually distinct.
- Route edges around unrelated nodes and labels. Avoid shared corridors that make two
  relationships indistinguishable. Endpoint sides and arrowheads must agree with the
  authored direction.
- Use color only for a semantic category or focus and pair it with text, shape, or
  pattern. Keep the meaning complete in a static, reduced-motion view.
- Move supporting inventories and long evidence into adjacent detail cards or a named
  detail layer. Do not shrink the primary graph until labels become unreadable merely
  to keep every fact on one screen.
