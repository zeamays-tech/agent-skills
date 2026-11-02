# Publish Skills with Independent Versions

- Status: Accepted
- Date: 2026-11-02

## Context

Skills need independent publication and installation references. A shared repository version couples unrelated Skill changes and does not identify the version of an installed Skill directory. The maintainer approved independent `metadata.version` values, tags and release packages, with every current Skill starting at `1.0.0`.

## Decision

Use each `skills/<skill-name>/SKILL.md` as its version authority. Store a quoted SemVer string under a block-style `metadata` mapping, with a two-space-indented `version` key. This is a repository formatting convention within the [Agent Skills metadata format](https://agentskills.io/specification#metadata-field), which permits string-to-string custom metadata (accessed 2026-11-02). The format itself does not define an installation resolver.

Publish one Skill with a `<skill-name>-v<version>` Git tag and a corresponding GitHub Release asset containing that Skill's tagged directory. Installation pins the tag and Skill path. Each release increment changes only the selected Skill's version; the script retains its confirmation, clean-tree checks, scoped version commit, local tag and remote conflict checks.

Allow publishing the current version for the initial `1.0.0` releases and retrying a prepared release without another increment. Compare version precedence only within that Skill's tag namespace. Different Skills may publish from one commit, and no new release is designated repository-wide latest.

## Migration and consequences

- Remove the root `VERSION` file. All four current Skills use `metadata.version: "1.0.0"` as the start of their independent sequence; this is not a claim that these releases are already published.
- Preserve old `v*` tags, GitHub Releases and pinned installation URLs. Do not retag or rewrite their content.
- This decision supersedes the shared-version rule in [the distribution decision](0001-open-agent-skills-primary-distribution.md) and the [version-file decision](0003-track-repository-version-in-file.md). The open repository remains the primary publication source.
- Keep platform-required metadata transformations in derived packages. Such packages do not replace the portable source or define a separate Skill content version.
- A metadata value is prepared state. Publication is established by the matching tag, Release and asset. A failed upload may require inspecting and repairing an incomplete Release with explicit authorization.
- Repository validation and open-format discovery still run before publication. Current commands and recovery procedures live in the root [README](../../README.md#release).

## Alternatives considered

Retaining shared repository versions would keep the old release script but continue coupling independent Skills. Maintaining only Git commit references would support pinning, but would not meet the selected independent semantic-version publication workflow.
