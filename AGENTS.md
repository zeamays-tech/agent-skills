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
- Use Git tags and GitHub Releases for SemVer versions; do not add version fields to Skill frontmatter.
- Treat repository-local ownership or document maps as authoritative when they are added later.

## Skill changes

- Read the complete target `SKILL.md` and every reference needed for the change.
- Keep frontmatter limited to `name` and `description` unless the open specification and repository policy explicitly require otherwise.
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
