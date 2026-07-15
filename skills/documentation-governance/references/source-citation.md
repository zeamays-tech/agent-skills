# Source Citation

Preserve external evidence in the document whose claims depend on it.

## Apply the workflow

1. Identify claims, constraints, compatibility statements, data, or recommendations derived from external material.
2. Prefer the primary source: a standard, official documentation, release note, source repository, specification, or authoritative issue or change record.
3. Check the source's owner, version, publication date, and applicability to the project.
4. Cite the source next to the supported claim or in a compact references section in the same project document.
5. Include an access date or source date for information likely to change.
6. Distinguish normative authority from contextual evidence, examples, and secondary commentary.
7. Reopen each cited link and verify that it supports the final wording.

## Choose traceable citations

- Link to a canonical page or versioned specification, not a search result or generated summary.
- Prefer a stable section anchor, release, tag, or commit when the exact version matters.
- Cite sources that materially influenced feasibility, API usage, compatibility, security, performance, deployment, or business claims.
- Keep citations concise and close enough that readers know which claim they support.
- When primary sources disagree, describe the scope or version difference instead of hiding it.
- Label a source as context when it informed exploration but does not prove the final claim.

## Keep authority boundaries clear

An external source establishes facts about the system or policy it owns. It does not automatically establish this project's requirements. Record the project decision in the appropriate owner document and use the external citation as evidence or a constraint.

Do not leave a source only in an agent response when project documentation relies on it. Conversely, do not add citations that did not influence the final document merely to make it look researched.

## Suggested forms

Use an inline link for a local claim:

```markdown
The client follows the protocol's retry requirements ([Protocol specification](https://example.org/specification#retries)).
```

Use a references section when several claims share a source set:

```markdown
## References

- Protocol specification, version 2.1: https://example.org/specification
- Compatibility guide, accessed 2026-01-15: https://example.org/compatibility
```

Use illustrative domains only in examples. Replace them with the actual authoritative sources in project documentation.
