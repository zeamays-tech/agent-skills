# Use an Open Agent Skills Repository as the Primary Distribution Source

- Status: Accepted
- Date: 2026-07-15

## Context

The repository needs a public distribution model that keeps Skills versioned, reviewable, and usable across AI coding agents. The chosen model must preserve a single authoritative publication source while allowing compatible clients to consume the same core instructions and references.

The [Agent Skills specification](https://agentskills.io/specification) defines a portable directory built around `SKILL.md`, with optional scripts, references, and assets. The [`skills` CLI](https://github.com/vercel-labs/skills) can install named Skills from a GitHub repository.

## Decision

Use this GitHub repository as the authoritative publication source. Publish each Skill under `skills/<skill-name>/` using the Agent Skills open format.

Manage repository releases with Semantic Versioning expressed through Git tags and GitHub Releases. Keep Skill frontmatter focused on discovery metadata rather than release metadata.

Allow optional client-specific metadata only when the Skill remains fully usable without it. Keep installation and usage guidance centered on open-format consumers.

## Consequences

- One reviewed source defines released Skill content.
- Consumers can install the same Skill into multiple compatible agents.
- Version selection and rollback operate at repository release boundaries.
- Client-specific presentation can coexist with the portable Skill without becoming a runtime dependency.
- Maintainers must test portability and prevent private or environment-specific content from entering releases.

## Alternatives considered

### Use a client-specific plugin or marketplace as the primary source

This could provide richer integration for one client, but it would make the primary publication path less portable and could create a second authority for the same Skill. Client-specific packaging may be reconsidered as a secondary channel if it can be generated from, and remain subordinate to, this repository.

### Publish unversioned copies in consuming repositories

This would reduce initial distribution work but make provenance, updates, and rollback difficult. Consumer repositories may pin or vendor releases, but those copies are not the publication authority.
