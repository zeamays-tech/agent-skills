# Modes, Scope, and Activation

Select the least expensive mode that can answer the request, then hold its read and write boundaries constant unless the user explicitly changes them.

## Apply invocation precedence

1. Follow an explicit user-selected mode.
2. Treat an explicit invocation with no mode or arguments as `audit` of the current change set.
3. Treat explicit fix, correction, or reconciliation language as `reconcile` only for the named task and artifacts.
4. Treat an explicit completion, merge, milestone, or release check as `gate`.
5. Treat a request to verify real deployed behavior as `post-deploy`.
6. For semantic activation without a mode, select the smallest sufficient read-only mode.

Do not let mode selection itself grant permission to edit files, invoke external systems, deploy, merge, publish, or alter production.

## Define the current change set

Use this priority:

1. User-named files, behavior, repositories, commits, or comparison range.
2. A comparison range or lifecycle boundary declared by applicable repository guidance.
3. Staged, unstaged, and untracked work in every explicitly in-scope repository.
4. A branch-to-base comparison only when the base can be established from repository policy, an upstream relationship, or the user.

If a base is ambiguous, audit the working tree and state that committed branch-only changes were not assessed. Never guess a base that could distort the result.

## Keep five modes distinct

### Impact

Perform lightweight, read-only discovery. Identify likely planes, authorities, consumers, repositories, validation owners, and post-deployment boundaries. Stop before a comprehensive scan when the question is only prospective.

### Audit

Inspect the current change set and directly connected authorities. Classify contradictions, missing links, incomplete consumers, and evidence gaps. Report repairs without applying them.

### Reconcile

Require explicit authorization to correct files. Record the authorized repositories, path set, and requested behavior before editing. Apply only decisions supported by a confirmed authority. Re-run affected checks and report needed out-of-scope repairs.

Treat “global reconciliation” as all affected artifacts inside an explicit project or workspace boundary. If the boundary is not defensible, remain read-only, present the discovered repositories, and request the missing scope decision.

### Gate

Evaluate repository-defined criteria for the named feature, milestone, merge, or release. A gate does not authorize fixes. Return `FAIL` for known violations, `BLOCKED` for missing authority or required evidence, and `PASS` only for a fully evidenced in-scope decision.

### Post-deploy

Identify what local evidence cannot prove. Document or run repository-approved checks only in an authorized target environment. Record environment, version, time, expected and observed results, failure signals, and containment or rollback guidance when applicable.

## Separate activation mechanisms

A Skill cannot listen to Git, CI, deployment, or document events by itself. Use three explicit layers:

- **Semantic activation:** Put broad but selective triggers in Skill frontmatter so a compatible agent can activate the workflow during a relevant task.
- **Lifecycle activation:** Let each consumer repository declare mandatory nodes in its applicable `AGENTS.md` or governance manifest, such as after an accepted contract change or before a release claim.
- **Deterministic enforcement:** Optionally let the consumer repository call a stable script or CI gate with project-declared inputs and validation commands.

Do not describe semantic activation as an event listener or guarantee that a client will invoke it.

## Trigger selectively

Use reconciliation when:

- an accepted requirement, active design, or accepted decision changes;
- an API, event, persistence schema, configuration contract, migration, or deployment definition changes;
- integration crosses components or repository boundaries;
- a feature, milestone, merge, or release is about to be declared complete;
- documentation, executable behavior, tests, acceptance results, or deployment evidence directly disagree;
- a material boundary can be verified only after deployment.

Avoid a broad scan for spelling or formatting changes, behavior-preserving internal refactors, generated churn already covered by a deterministic check, or unaccepted drafts. Escalate from lightweight impact analysis only when evidence shows a wider material effect.

## Enforce authorization boundaries

Record read scope separately from write scope. A useful task-local scope note contains:

- workspace boundary and in-scope repository roots;
- requested topics or change range;
- authorized write repositories and paths;
- permitted external environments and operations, if any;
- exclusions, pre-existing changes, and stop conditions.

Automatic activation never expands any of these fields. Cross-repository reading may be necessary for impact analysis, but cross-repository repair requires explicit task scope. If a required edit or check falls outside authorization, classify it `out-of-scope` and hand it off.
