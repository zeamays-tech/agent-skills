# Agent Skills

Open, versioned, and portable Agent Skills for AI coding agents.

This repository publishes Skills in the lightweight [Agent Skills open format](https://agentskills.io/specification). The GitHub repository is the authoritative source for released Skill content.

## Available Skills

| Skill | Purpose |
| --- | --- |
| [`documentation-governance`](skills/documentation-governance/SKILL.md) | Create, modify, review, and synchronize software documentation while separating current guidance from decision and migration history. |
| [`reconcile-project-state`](skills/reconcile-project-state/SKILL.md) | Discover, audit, correct within authorization, and gate inconsistencies across intended, executable, and evidence state. |

## Install

The current [`skills` CLI documentation](https://github.com/vercel-labs/skills#install-a-skill) (accessed 2026-08-02) supports GitHub repository shorthand, named Skill selection, project or global scope, and agent targeting. In the examples below, replace variable values with a Skill name, release tag, or supported agent identifier.

List the Skills available from this repository without installing them:

```bash
npx skills add zeamays-tech/agent-skills --list
```

Install a selected Skill to the current project:

```bash
skill_name="replace-with-skill-name"
npx skills add zeamays-tech/agent-skills --skill "$skill_name"
```

Install it globally for a selected agent:

```bash
skill_name="replace-with-skill-name"
agent_name="replace-with-agent-id"
npx skills add zeamays-tech/agent-skills --skill "$skill_name" --global --agent "$agent_name"
```

The CLI installs to project scope by default. `--global` makes the Skill available across projects for the selected agent; repeat `--agent` to target additional agents. `npx` may download the CLI package on first use.

### Install a specific release

Use the direct GitHub tree source documented by the [`skills` CLI source formats](https://github.com/vercel-labs/skills#source-formats), replacing the tag and Skill name. This pins installation to the repository content published by that tag:

```bash
release_tag="replace-with-release-tag"
skill_name="replace-with-skill-name"
npx skills add "https://github.com/zeamays-tech/agent-skills/tree/${release_tag}/skills/${skill_name}"
```

Add `--global --agent <agent-id>` when a pinned installation should apply globally to a particular agent. Published tags are listed on the repository's [Releases page](https://github.com/zeamays-tech/agent-skills/releases).

### Update an installed Skill

For an unpinned installation, update one tracked Skill to the latest content from its recorded source:

```bash
skill_name="replace-with-skill-name"
npx skills update "$skill_name" --global
```

Use `--project` instead of `--global` for a project-scoped installation. The [`skills update` documentation](https://github.com/vercel-labs/skills#skills-update) also covers updating multiple Skills or selecting the scope interactively.

Treat a release-tag installation as intentionally pinned. To upgrade it, select a newer published tag and rerun the specific-release installation command; do not silently turn a reproducible installation into an unpinned one.

## Use

Invoke the Skill explicitly when the client supports named Skill prompts:

```text
Use $<skill-name> for this task.
```

A selected Skill may be installed without this repository README. Each Skill therefore carries its own explicit-invocation and consumer-`AGENTS.md` guidance:

- [`documentation-governance` consumer integration](skills/documentation-governance/references/consumer-integration.md)
- [`reconcile-project-state` consumer integration](skills/reconcile-project-state/references/consumer-integration.md)

Treat the installed Skill's `SKILL.md` and directly linked references as the usage authority available to both agents and people after installation.

Compatible agents may also activate it automatically from the `name` and `description` fields. The optional `agents/openai.yaml` improves one client interface but is not required by the Skill.

## Versioning

Releases follow [Semantic Versioning](https://semver.org/) through Git tags and GitHub Releases:

- Patch: clarifications and compatible guidance fixes.
- Minor: compatible capabilities, references, or workflows.
- Major: breaking changes to Skill behavior, structure, or expected usage.

Skill frontmatter intentionally has no version field. Installers and consumers should use repository tags or release references when reproducibility requires a fixed version.

## Release

After committing release-ready changes, start the interactive release dialogue. When the latest GitHub Release has a valid SemVer tag, the script suggests the next patch for a stable version or the corresponding stable version for a prerelease; otherwise, it suggests `v0.1.0`. It then asks for the release tag, Release title, and dry-run or publishing mode:

```bash
./scripts/release.sh
```

Dry run is the default interactive mode. It performs preflight checks and validation but does not create a tag, push, or create a GitHub Release. Select publish only after reviewing a successful dry run. The publishing run requires a clean checkout on the GitHub default branch, pushes that branch, creates and pushes an annotated tag at `HEAD`, and creates a Release with generated notes.

The script requires Bash, standard Unix utilities including `basename`, `mktemp`, and `rm`, plus `git`, an authenticated [GitHub CLI](https://cli.github.com/manual/gh_auth_status), `python3`, and `npx`. The open-format check uses `NPM_CONFIG_CACHE` or `npm_config_cache` when configured; otherwise, it creates an isolated temporary npm cache. It does not add a repository dependency. The script uses `--verify-tag` so GitHub will not silently create a tag at another commit; these options follow the current [`gh release create` manual](https://cli.github.com/manual/gh_release_create) (accessed 2026-08-02).

For automation, provide the same information as arguments:

```bash
./scripts/release.sh --dry-run --title "Release title" v1.2.3
./scripts/release.sh --publish --yes --title "Release title" v1.2.3
```

Use `--yes` only for an intentional non-interactive release. If tag publication succeeds but Release creation fails, resolve the external error and rerun the same command; the script accepts an existing tag only when it still points to `HEAD`.

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
