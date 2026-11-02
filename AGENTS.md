# Repository Guidance

## Scope

These instructions apply to the entire repository. Add narrower `AGENTS.md` files only when a subtree needs additional portable rules.

## Repository purpose

Maintain open, versioned, and portable Agent Skills for AI coding agents. Keep every Skill usable through the Agent Skills open format without requiring a product-specific plugin, marketplace, or runtime.

## Sources of truth

- Treat `skills/<skill-name>/` as the published source for that Skill.
- Keep repository-level installation, version selection, and catalog guidance in the root `README.md`.
- Keep installed-Skill invocation and consumer `AGENTS.md` integration guidance in `SKILL.md` or a directly linked file under `references/`.
- Keep durable repository decisions in `docs/decisions/`.
- Keep each Skill version in its `SKILL.md` under `metadata.version` as a quoted SemVer string. Use a block-style `metadata` mapping and two spaces before `version` so release tooling can replace only that value. Publish one Skill at a time with tag `<skill-name>-v<version>` and an archive from that tagged Skill directory. Update and commit only the selected `SKILL.md` during an authorized version increment. Preserve historical tags and releases; a metadata value alone is not proof of publication.
- Treat repository-local ownership or document maps as authoritative when they are added later.

## Skill changes

- Read the complete target `SKILL.md` and every reference needed for the change.
- Use standard frontmatter fields: `name`, `description`, and `metadata` with the required independent `version`. Additional metadata values must be strings and serve an actual consumer need. Keep platform-specific top-level extensions in generated distribution packages.
- Make the description explain both capability and triggering contexts.
- Keep `SKILL.md` concise and link directly to focused files under `references/`.
- Add `scripts/` only for deterministic, repeatable work with controllable error rates. Test every added script.
- Keep optional client metadata nonessential to execution.
- Do not create a README, changelog, or installation guide inside a Skill directory.

## Public-content boundaries

- Use generic examples and fixture names.
- Do not include private repository, organization, person, host, URL, role, or business-project details.
- Do not include developer-machine absolute paths, credentials, tokens, or environment-specific state.
- Do not hardcode a consumer repository's documentation paths, owners, or ADR numbering scheme.
- Preserve unrelated and untracked files. Do not overwrite user changes.

## Documentation layers

- Keep READMEs, active requirements, active designs, and runbooks focused on the current valid state.
- Keep rejected, superseded, retired, and migration history in ADRs, migration records, release notes, or changelogs.
- Allow prohibitive language for security, privacy, permissions, compliance, compatibility, and operational safety.
- Classify content by document purpose, path, status, and semantics; never reject text from a single keyword.

## Completion handoff

- After any AI-authored repository change, inspect the complete uncommitted state, including staged changes, unstaged changes, and untracked files, then recommend exactly one commit message in the completion response: a concise single line that follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) in the form `<type>[optional scope]: <description>` and summarizes all uncommitted repository changes.

## Validation

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Also validate each changed Skill with a current Agent Skills-compatible validator. Check all public text for private identifiers, absolute paths, private URLs, stale links, and accidental product-specific dependencies.

Do not commit, push, tag, or publish unless the user explicitly authorizes it.
