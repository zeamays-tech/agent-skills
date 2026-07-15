# Agent Skills

Open, versioned, and portable Agent Skills for AI coding agents.

This repository publishes Skills in the lightweight [Agent Skills open format](https://agentskills.io/specification). The GitHub repository is the authoritative source for released Skill content.

## Available Skills

| Skill | Purpose |
| --- | --- |
| [`documentation-governance`](skills/documentation-governance/SKILL.md) | Create, modify, review, and synchronize software documentation while separating current guidance from decision and migration history. |

## Install

The current [`skills` CLI documentation](https://github.com/vercel-labs/skills#install-a-skill) supports GitHub repository shorthand and selecting a named Skill:

```bash
npx skills add zeamays-tech/agent-skills --skill documentation-governance
```

The CLI installs to project scope by default. Review the CLI's documented agent and global-scope options before choosing a different target. `npx` may download the CLI package on first use.

## Use

Invoke the Skill explicitly when the client supports named Skill prompts:

```text
Use $documentation-governance to review and synchronize the project documentation.
```

Compatible agents may also activate it automatically from the `name` and `description` fields. The optional `agents/openai.yaml` improves one client interface but is not required by the Skill.

## Versioning

Releases follow [Semantic Versioning](https://semver.org/) through Git tags and GitHub Releases:

- Patch: clarifications and compatible guidance fixes.
- Minor: compatible capabilities, references, or workflows.
- Major: breaking changes to Skill behavior, structure, or expected usage.

Skill frontmatter intentionally has no version field. Installers and consumers should use repository tags or release references when reproducibility requires a fixed version.

## License

This repository is licensed under the [Apache License, Version 2.0](LICENSE). See the accepted [licensing decision](docs/decisions/0002-license-repository-under-apache-2.0.md) for the repository-level rationale.

## Safety and portability

- Read the target repository's `AGENTS.md` and local governance before applying a Skill.
- Review Skill changes like code: inspect diffs, sources, scripts, and generated artifacts before adoption.
- Keep secrets, private URLs, personal paths, and organization-specific policy out of public Skill content.
- Treat repository-specific ownership, document paths, and decision processes as consumer configuration, not universal defaults.
- Treat guidance as assistance, not as a substitute for security, legal, compliance, or operational approval.

See the accepted [distribution decision](docs/decisions/0001-open-agent-skills-primary-distribution.md) for repository-level rationale.

## Validate

Run the dependency-free repository checks:

```bash
python3 -m unittest discover -s tests -v
```

Validate each Skill with a current Agent Skills-compatible validator before release.
