# Decisions and Migrations

Preserve why the system changed without turning current guidance into a history lesson.

## Use ADRs for durable decisions

Create or update an ADR when a choice has lasting architectural consequences, meaningful alternatives, or tradeoffs future maintainers may otherwise reopen. Follow the repository's template, status vocabulary, location, naming, and approval process; do not invent them.

Record at least:

- Context and forces at the time of the decision.
- Options actually considered.
- The decision and its status.
- Consequences, risks, and follow-up work.
- Links to superseded or superseding records when applicable.

Keep rejected alternatives in an ADR only when they were deliberately evaluated as part of the recorded decision. Preserve superseded accepted decisions with clear status. A never-accepted draft or erroneous proposal is not decision history: remove it without creating or amending an ADR merely to memorialize its rejection.

## Keep ADRs out of current instructions

An ADR explains a decision; it is not normally the operator's procedure or the user's product guide. Update the current owner document after a decision is accepted. Link to the ADR for rationale without copying its alternatives into the current explanation.

When a decision changes, follow repository policy to supersede or amend the record. Avoid rewriting history in a way that hides what was known or decided at the time.

## Write migration records for active transitions

Include old behavior only to help readers reach the supported state. Specify:

- Source and target versions or states.
- Preconditions, compatibility window, and affected users or systems.
- Ordered steps, validation, rollback, and failure recovery.
- Cutover or completion criteria.
- Removal date or follow-up cue when known.

Once the transition is complete, keep the durable record in the repository's historical location and remove obsolete instructions from current runbooks and READMEs.

## Use changelogs and release notes for events

Record externally meaningful changes with their release or date. State what changed, compatibility impact, and required action. Link to current instructions for how the system works now and to ADRs for deeper rationale.

Do not use a changelog as the only owner of a current requirement, architecture contract, or operational procedure.

## Review lifecycle language

For every reference to a rejected, replaced, deprecated, removed, or retired item, ask:

1. Was the item accepted, released, deployed, or deliberately evaluated in a decision process that the repository preserves?
2. Does the reader need this history to act now?
3. Is this document designed to preserve history?
4. Is the status and time scope explicit?
5. Is there a current owner document that must also change?

If the first answer is no, remove the item and any explanation whose only purpose is its rejection. Otherwise relocate or condense the statement when the remaining answers do not support its current placement.
