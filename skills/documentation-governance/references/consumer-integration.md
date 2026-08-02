# Consumer Integration

Carry this guidance with the installed Skill so agents and people can invoke it without access to the publication repository's root README.

## Invoke explicitly

Use a named prompt when the client supports Skill invocation:

```text
Use $documentation-governance to audit the current documentation and report conflicts without editing.
```

```text
Use $documentation-governance to update the accepted design and synchronize its affected current-state guidance.
```

```text
Use $documentation-governance to record the post-deployment checks that local validation cannot establish.
```

Name the documents, task, read or write boundary, and expected outcome when they are known. An explicit invocation does not grant permission to edit unrelated artifacts or external systems.

## Configure consumer repository instructions

Frontmatter supports semantic activation, but a Skill cannot guarantee that every client will invoke it at a required lifecycle point. Put mandatory repository behavior in the applicable `AGENTS.md` or equivalent governance file.

Use this portable starting point:

```markdown
## Documentation governance

Use `$documentation-governance` whenever a task creates, modifies, reviews,
or synchronizes project documentation, including requirements, designs,
ADRs, runbooks, migrations, release guidance, and verification records.

Read every applicable `AGENTS.md` and repository-provided document or
ownership map before editing. Treat repository-declared document classes,
status vocabulary, owners, paths, and validation commands as authoritative.
Preserve unrelated changes and report unresolved authority conflicts.
```

Adapt the template to the repository's actual governance. Declare project-specific document locations, owners, status terms, validation commands, citations, and write restrictions in the consumer repository rather than in this global Skill.

## Keep activation layers distinct

- Use frontmatter description for semantic activation in compatible clients.
- Use consumer `AGENTS.md` rules for mandatory lifecycle behavior.
- Use repository-owned checks for deterministic validation.

Do not describe semantic activation as a Git, CI, or deployment event listener.
