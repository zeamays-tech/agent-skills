---
name: documentation-governance
description: Govern creation, modification, review, and synchronization of software project documentation. Use when working on READMEs, requirements or PRDs, architecture or HLDs, design documents, runbooks, ADRs, migration guides, changelogs, repository instructions, external-source citations, or post-deployment verification; especially when separating current state from decision history, resolving authority or ownership, or keeping related documents aligned.
---

# Documentation Governance

Keep operational guidance trustworthy while preserving useful decision history in the documents designed to hold it.

## Load the relevant guidance

- Always read [document layers](references/document-layers.md) and [authority and synchronization](references/authority-and-sync.md).
- Read [requirements and design](references/requirements-and-design.md) for PRDs, requirements, HLDs, design documents, acceptance criteria, or repository guidance.
- Read [decisions and migrations](references/decisions-and-migrations.md) for ADRs, changelogs, deprecations, replacements, migrations, or retired behavior.
- Read [source citation](references/source-citation.md) when external material informs a claim, constraint, recommendation, or compatibility statement.
- Read [post-deployment verification](references/post-deployment-verification.md) when local, mocked, sandboxed, or offline checks cannot establish deployed behavior.

## Follow the workflow

1. Discover repository rules before editing. Read every applicable `AGENTS.md` and any repository-provided ownership, document map, or governance configuration. Inspect related code, tests, schemas, configuration, and current changes without overwriting unrelated work.
2. Classify each affected document and, when necessary, each section as current-state, historical/decision, or transitional/verification. Use declared repository policy first, then document purpose and semantics, with the path as supporting evidence. Never classify from one keyword alone.
3. Identify the authoritative source and owner for every material claim. Surface conflicts instead of silently choosing whichever source is easiest to edit.
4. Edit current-state documents to describe only the currently valid product, architecture, contract, and operating procedure. Keep rejected, replaced, and retired approaches in ADRs, migration records, release notes, or changelogs. Leave a concise link from current guidance only when readers need the history to act safely.
5. Express requirements as observable desired outcomes. Preserve prohibitions when they define security, privacy, permission, compliance, compatibility, or operational risk boundaries. Judge wording by purpose, not grammatical polarity.
6. Synchronize all affected owner documents, links, examples, tests, generated references, and verification records. Summarize executable contracts instead of copying values that will drift from code, schemas, configuration, or generated API specifications.
7. Validate the result. Re-read the edited documents in their intended reader flow, inspect the diff, verify links and citations, run relevant repository checks, and record any deployed-environment checks that remain.

## Enforce these invariants

- Treat current guidance as a view of the valid state, not as a narrative of how the project arrived there.
- Preserve decision rationale and superseded alternatives in historical records where future readers can interpret their status.
- Allow necessary old-version details in migration material and necessary prohibitions in boundary constraints.
- Keep PRD intent separate from HLD implementation boundaries while maintaining traceability between them.
- Cite external authority in the project document that relies on it, not only in the agent response.
- Do not invent project paths, owners, ADR numbering, or source-of-truth mappings. Use repository instructions or report the ambiguity.

## Report completion

State which documents were classified and changed, which source was treated as authoritative, which related documents were synchronized, and which conflicts or post-deployment checks remain. Explain retained negative or historical language when its placement could otherwise look accidental.
