# Requirements and Design

Keep product intent, technical design, and acceptance evidence connected without collapsing them into one document.

## Write positive requirements

Describe the observable desired state directly:

- State what the user can accomplish and what the system provides.
- State scope, preconditions, outcomes, and measurable acceptance behavior.
- Replace rejected alternatives with the selected outcome in current requirements.
- Put option history and tradeoff rationale in an ADR or design-review record.

Do not apply a blanket ban on negative wording. Retain prohibitions when they define a meaningful boundary, and name the protected property or risk when it is not obvious:

- Security and privacy: data must not cross a trust boundary.
- Authorization: a role cannot perform an operation.
- Compliance: records must not be deleted before a retention period ends.
- Compatibility: a client does not support a protocol version.
- Operational safety: a rollout must not proceed while a health gate fails.

Rewrite a negative product aspiration such as "do not make users repeat setup" as an observable outcome such as "preserve completed setup across sessions."

## Keep PRDs focused

Put the following in a product requirement document:

- Problem, audience, goals, and non-goals when they define current scope.
- User flows and user-visible behavior.
- Product data definitions and business rules.
- Acceptance criteria and success signals.
- Constraints that materially affect product behavior.

Keep component topology, storage selection, internal protocols, and low-level implementation details out unless they are fixed product constraints.

## Keep HLDs focused

Put the following in a high-level design:

- System boundaries and component responsibilities.
- Data flow, state ownership, and integration points.
- Interface contracts and failure handling.
- Security, reliability, scalability, and deployment implications.
- Traceability to the requirements the design satisfies.

Keep product prioritization and transient visual styling out unless they define a technical boundary. Put detailed interaction or visual specifications in the repository's designated design artifact.

## Maintain traceability

Connect requirements, design, implementation, and verification with stable identifiers or links when the repository supports them. Keep the relationship directional:

`requirement -> design decision -> implementation authority -> verification evidence`

Do not use traceability as a reason to repeat entire sections. Link and summarize the relationship instead.
