# Document Layers

Classify before editing so readers can tell what is valid now and what explains the past.

## Classification order

1. Apply an explicit repository document map or local instruction when one exists.
2. Read the document's stated purpose, audience, status, headings, and surrounding content.
3. Classify the claim by semantics: current instruction, durable rationale, completed event, or active transition.
4. Use the filename and path as corroborating evidence, never as the only evidence.
5. Classify individual sections separately when a document legitimately serves more than one purpose.
6. Report ambiguity instead of moving or deleting material when the repository gives no defensible answer.

## Current-state documents

Typical examples include a root README, active requirement or design documents, API guidance, operations manuals, security policies, and runbooks.

Keep these documents focused on:

- The supported product behavior and user-visible contract.
- The active architecture, responsibilities, interfaces, and data flow.
- The procedure an operator or contributor should follow now.
- Present compatibility, security, permission, and availability boundaries.

Remove narrative such as abandoned proposals, rejected designs, obsolete implementation details, and the chronology of replacements. If history affects a current action, state the active constraint briefly and link to the appropriate historical record.

## Historical and decision documents

Typical examples include ADRs, changelogs, release notes, migration records, incident reviews, and design-review records.

Allow these documents to preserve:

- The context available when a decision was made.
- Options considered, including rejected or superseded approaches.
- The decision, status, tradeoffs, and consequences.
- A migration sequence or compatibility window.
- What changed in a release or operational event.

Always make status and time scope clear. Do not rewrite an old decision record to pretend it described the current state; supersede it or add a later record according to repository policy.

## Transitional and mixed material

A migration guide may need to describe both an old contract and the target contract. A current runbook may need a short rollback note. A deprecation notice may remain current while a compatibility window is open.

Keep such material only when it helps a reader complete an active transition or handle a current risk. Label the versions, dates, entry conditions, exit conditions, and destination state. Move the completed narrative to history when the transition ends.

## Semantic checks

Evaluate the whole statement and its job in the document:

- "Unauthenticated callers must not access administrative endpoints" is a valid current security boundary.
- "The system used a polling relay before it moved to a stream" is historical narrative and normally does not belong in a current README.
- "Version 2 accepted a string; convert it to an integer before enabling version 3" is necessary migration context.
- "Requests enter the gateway and accepted jobs are routed to workers" is a current architecture description.

Words such as *old*, *deprecated*, *must not*, or *removed* are review signals, not automatic failures. Require evidence from purpose, status, and semantics before recommending relocation.
