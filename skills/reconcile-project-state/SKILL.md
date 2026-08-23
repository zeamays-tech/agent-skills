---
name: reconcile-project-state
description: Reconcile software project state across accepted requirements, design decisions, current documentation, implementation, schemas, configuration, migrations, tests, acceptance results, and deployment evidence. Use for impact, audit, authorized correction, completion gates, and post-deployment verification when accepted requirements or ADRs change; APIs, events, persistence schemas, configuration, migrations, or other executable contracts change; integrations cross repositories or components; a feature, milestone, merge, or release is about to be declared complete; intended, executable, and evidence state conflict; real deployed behavior must be verified; or a consumer repository needs lifecycle-trigger or explicit-invocation guidance for this Skill. Skip broad reconciliation for spelling or format-only edits, behavior-preserving internal refactors, and unaccepted drafts unless explicitly requested.
---

# Reconcile Project State

Close delivery gaps by tracing accepted intent to executable authority and trustworthy verification evidence without inventing project policy or widening the authorized scope.

## Load the operating guidance

- Always read [state model and authority](references/state-model-and-authority.md) and [modes, scope, and activation](references/modes-scope-and-activation.md).
- Read [discovery and reconciliation](references/discovery-and-reconciliation.md) for audit, reconcile, gate, cross-component, or cross-repository work.
- Read [verification and reporting](references/verification-and-reporting.md) for audit, reconcile, gate, post-deploy, or any completion claim.
- Read [consumer integration](references/consumer-integration.md) when invoking the Skill explicitly or configuring semantic and mandatory lifecycle triggers in a consumer repository.
- When creating, changing, reviewing, or synchronizing documentation, load and follow `documentation-governance` in addition to this Skill. Let that Skill govern document classification and synchronization; keep this Skill focused on closing the delivery-state loop. If it is unavailable, follow the target repository's documentation rules and report the missing dependency.

## Select a mode before acting

Use the user's explicit instruction first. Treat an explicit `$reconcile-project-state` invocation with no arguments as `audit` of the current change set.

Use a named mode when the desired outcome must be unambiguous:

```text
Use $reconcile-project-state in gate mode before declaring this release complete.
```

| Mode | Purpose | Mutation |
| --- | --- | --- |
| `impact` | Identify affected components, repositories, contracts, authorities, and checks. | Read-only |
| `audit` | Classify inconsistencies and missing evidence. | Read-only |
| `reconcile` | Correct confirmed inconsistencies, then revalidate. | Only inside explicitly authorized write scope |
| `gate` | Decide whether the declared feature, milestone, merge, or release satisfies repository-defined criteria. | Read-only unless separately authorized |
| `post-deploy` | Plan, perform when authorized, and record checks that require a real environment. | Read-only by default; never infer production authority |

Interpret explicit requests to fix, correct, reconcile, or globally reconcile as `reconcile`; “global” means all affected artifacts inside the declared project or workspace boundary, never every repository on the machine. Discover and state the exact boundary before editing. Without explicit write authorization, stay read-only even when activated automatically.

When activation is semantic rather than explicit, choose the smallest sufficient read-only mode: `impact` for a prospective change, `audit` for a current inconsistency, `gate` for a completion claim, or `post-deploy` when local evidence cannot prove deployed behavior.

## Run the workflow

1. **Establish scope.** Read every applicable `AGENTS.md` and repository-provided governance, ownership, workspace, or source map. Inspect every in-scope repository's branch, staged, unstaged, and untracked changes. Preserve existing work.
2. **Define the change set.** Prefer the user's stated scope and repository-declared comparison base. Otherwise audit staged, unstaged, and untracked files; include a branch comparison only when its base is defensible. State omissions and assumptions.
3. **Map authority.** For each affected topic, identify intended, executable, and evidence sources plus owners and synchronization targets. Prefer a declared workspace or repository manifest. If none exists, create a provisional map and label every inference.
4. **Trace directionally.** Follow `requirement -> design decision -> implementation or executable authority -> verification evidence`. Record identifiers or links and a short relationship; never copy a complete contract merely to create traceability.
5. **Classify gaps.** Separate source conflicts, missing links, stale intent, executable drift, incomplete implementation, insufficient or stale evidence, environment divergence, ambiguous authority, and out-of-scope repairs.
6. **Act according to mode.** Report only in read-only modes. In `reconcile`, change only confirmed targets inside the authorized write set. Do not silently choose between accepted intent and validated actual behavior; surface the conflict and obtain the missing decision.
7. **Validate proportionally.** Run repository-declared checks from the correct repository and environment. Record commands, scope, results, and evidence. Mark unavailable or insufficient checks `blocked` or `unverified`, never `passed`.
8. **Decide and report.** Apply repository-defined gate criteria. Report sources, gaps, corrections, validation, unresolved conflicts, unverified items, and the final gate result even when the result is blocked.

## Use deterministic helpers selectively

- Run `python3 scripts/collect_project_state.py --root <scope>` to collect read-only Git boundaries and change state. Add `--discover-nested` only when nested repository discovery is in scope; use `--base-ref` only when the comparison base is known.
- Build a reconciliation ledger following the loaded verification and reporting guidance, then run `python3 scripts/validate_reconciliation.py <ledger.json>` to detect invalid evidence claims, unauthorized applied actions, and unsatisfied gates.

Treat helper output as inventory, not semantic authority. Discover project facts from the target repository and never let a script's reach expand task scope.

## Preserve safety invariants

- Default to read-only and keep automatic activation read-only.
- Require explicit task scope before repairing another repository or component.
- Preserve all unrelated and pre-existing changes; never reset, overwrite, or reformat them for convenience.
- Distinguish accepted intent from drafts and actual behavior from validated behavior.
- Surface conflicting authorities and request a decision instead of silently normalizing one to another.
- Keep historical and decision records distinct from current-state guidance by composing with `documentation-governance`.
- Preserve accepted or repository-required history, but treat confirmed never-accepted work as repair material rather than history; in `reconcile`, remove its in-scope sole-purpose artifacts without tombstones or absence-only checks.
- Never fabricate evidence, production access, command results, owners, manifests, or gate criteria.
- Do not interact with a deployed environment without the required user and repository authorization.

## Complete the handoff

Always state:

- the mode, scope, repositories, and assumptions;
- the identified intended, executable, and evidence authorities;
- classified inconsistencies and directional trace gaps;
- corrections applied and their authorization boundary;
- validation commands and observed results;
- unresolved authority conflicts and unverified or post-deploy items;
- `PASS`, `FAIL`, `BLOCKED`, or `NOT ASSESSED` for the requested gate.
