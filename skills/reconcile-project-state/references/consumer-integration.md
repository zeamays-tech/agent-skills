# Consumer Integration

Carry this guidance with the installed Skill so agents and people can configure it without access to the publication repository's root README.

## Invoke explicitly

An invocation without a mode audits the current change set:

```text
Use $reconcile-project-state.
```

Select a mode or authorized scope when needed:

```text
Use $reconcile-project-state in impact mode for this proposed contract change.
```

```text
Use $reconcile-project-state to reconcile this contract. Write scope is limited to the explicitly named repositories and paths.
```

```text
Use $reconcile-project-state in gate mode before declaring this milestone complete.
```

```text
Use $reconcile-project-state in post-deploy mode to verify the repository-declared deployed behavior.
```

An explicit mode does not expand write, deployment, publication, or external-system authority.

## Configure consumer repository instructions

Use semantic activation for relevant tasks and consumer governance for mandatory lifecycle nodes. A Skill cannot listen to Git, CI, merge, or deployment events by itself.

Use this portable starting point:

```markdown
## Project-state reconciliation

Use `$reconcile-project-state` after accepted requirements or decisions
change, when executable contracts change, when project-state sources
conflict, for cross-component or cross-repository integrations, and before
declaring a feature, milestone, merge, or release complete.

An explicit invocation without arguments audits the current change set.
Automatic or semantic activation is read-only. Enter `reconcile` only when
the active task explicitly authorizes the affected repositories and paths.
Use `post-deploy` when local evidence cannot establish deployed behavior.
When reconciliation changes documentation, also use
`$documentation-governance`.
```

Ordinary spelling or formatting changes, behavior-preserving internal refactors, and unaccepted drafts should not trigger a broad scan unless the task explicitly requests one.

## Declare project-owned facts

Keep these facts in the consumer repository's applicable `AGENTS.md`, governance manifest, or owning artifacts:

- repository and workspace boundaries;
- intended, executable, and evidence authorities;
- document and decision status vocabulary;
- version and compatibility policy;
- validation, acceptance, and post-deployment commands;
- mandatory lifecycle nodes and gate criteria;
- authorized write paths and external environments.

Do not copy project-specific values into the global Skill. If the consumer repository declares no source map, allow the Skill to build a provisional map and require it to label assumptions.
