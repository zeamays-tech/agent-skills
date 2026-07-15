# Authority and Synchronization

Make each claim traceable to an owner and keep downstream documents aligned.

## Build a document map

Use a repository-provided map when available. Otherwise infer a provisional map from repository instructions and artifacts, then report assumptions. A useful map records:

| Topic | Current-state owner | Executable authority | Historical record | Human owner | Sync targets |
| --- | --- | --- | --- | --- | --- |
| Product behavior | Active requirements | Acceptance tests where applicable | Release notes | Repository-defined | README, user guide |
| Architecture | Active design document | Code and interface schemas | ADRs | Repository-defined | Runbooks, diagrams |
| Operations | Runbook | Deployment configuration and automation | Incident or migration records | Repository-defined | Alerts, verification checklists |

Do not copy this example as project policy. Adapt it to the repository's actual sources and ownership model.

## Resolve authority

- Follow explicit repository governance and ownership rules.
- Treat accepted requirements as authority for intended behavior and validated implementation as evidence of actual behavior.
- Treat schemas, configuration, tests, and generated specifications as executable authority for the contracts they define.
- Treat ADRs as authority for why a decision was accepted, not automatically as the latest operating guide.
- Treat external documentation as authority only within its owner, version, and time scope.
- Escalate conflicts among authoritative sources. Do not silently edit one source to match another without confirming which one should change.

## Avoid duplicated executable contracts

Prefer a durable summary plus a link to the executable source. Avoid manually copying:

- Complete option lists or enum members.
- Defaults, limits, ports, flags, environment variables, or version matrices.
- API request and response schemas already generated from source.
- Test commands or deployment steps owned by automation that changes independently.

Duplicate a contract only when the repository deliberately generates or verifies the copy, or when readers cannot safely use the authoritative source directly. Identify the synchronization mechanism and owner in that case.

## Synchronize by impact

Trace the change outward from its owner:

1. Update the authoritative product, architecture, or operational document.
2. Update direct consumer guidance such as READMEs, tutorials, runbooks, and examples.
3. Update or regenerate contract references, diagrams, and API material.
4. Align tests, acceptance criteria, and verification records when they are in scope.
5. Add or update an ADR, migration record, release note, or changelog when rationale or transition history matters.
6. Check incoming and outgoing links, terminology, versions, and status labels.

Do not widen an editing task into unrelated implementation without authorization. When an out-of-scope artifact must change, identify it, its owner, and the mismatch in the handoff.

## Review completion

Confirm that:

- Every material claim has a defensible authority.
- Every edited document has an identifiable audience and owner, even if ownership is recorded only in repository policy.
- Current-state documents agree on the current behavior.
- Historical records retain their original time scope and status.
- No manual copy can drift without an explicit synchronization mechanism.
