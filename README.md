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

Read the root [VERSION](VERSION) file to find the shared version for all Skills without querying Git tags. It contains one SemVer value without a leading `v`. Between releases it remains at the last release version until a confirmed publishing run updates it; local changes or a prepared version do not prove publication. Git tags and GitHub Releases identify published snapshots. See the [version-file decision](docs/decisions/0003-track-repository-version-in-file.md).

Choose release increments using [Semantic Versioning](https://semver.org/):

- Patch: clarifications and compatible guidance fixes.
- Minor: compatible capabilities, references, or workflows.
- Major: breaking changes to Skill behavior, structure, or expected usage.

Skill frontmatter intentionally has no version field. Installers and consumers should use repository tags or release references when reproducibility requires a fixed version.

## Release

Run the following sequence from the repository root:

| Step | Entry point | Completion signal | Next step |
| --- | --- | --- | --- |
| Prepare | Commit release-ready changes with authorization; leave version selection to the script | The working tree is clean on the GitHub default branch | Validate |
| Validate | Run the command below, choose major/minor/patch and enter a title, and select dry run | Validation succeeds and the displayed version/commit plan matches the intended release | Publish; on failure, stop, repair, commit any fixes, and retry Validate |
| Publish | Rerun with the same upgrade level and title, select publish, and confirm the version commit and publication with authorization | The script reports the published Release URL | Complete; on failure, use the [release recovery guidance](#release-recovery) |

The script displays the current [VERSION](VERSION) and previews the results of major, minor, and patch upgrades. Choose a level (default: patch), enter a nonblank Release title, then choose dry-run or publishing mode. Custom versions are not accepted; invalid choices and blank titles are prompted again:

```bash
./scripts/release.sh
```

Dry run is the default mode. It validates and displays the plan without changing `VERSION`, committing, tagging, pushing, or creating a Release. Select publish after a successful dry run. After confirmation, a changed version is written to `VERSION` and committed alone as `chore(release): v<version>`. The script then pushes the default branch, creates and pushes an annotated tag at the resulting `HEAD`, and creates the Release. An unchanged version creates no extra commit.

Major increments the major component and resets minor/patch; minor increments minor and resets patch; patch increments patch. Each choice produces a higher stable version, removing any previous prerelease/build suffix.

Version precedence follows [SemVer 2.0.0](https://semver.org/#spec-item-11) (accessed 2026-09-11), including prerelease identifiers and ignoring build metadata. A version must not be older than `VERSION` or any fetched SemVer tag. The recovery-only `--retry` option uses the current `VERSION` without an increment or custom input. An existing GitHub Release is never overwritten.

The script requires Bash, standard Unix utilities including `basename`, `mktemp`, and `rm`, plus `git`, an authenticated [GitHub CLI](https://cli.github.com/manual/gh_auth_status), `python3`, and `npx`. The open-format check uses `NPM_CONFIG_CACHE` or `npm_config_cache` when configured; otherwise, it creates an isolated temporary npm cache. It does not add a repository dependency. The script uses `--verify-tag` so GitHub will not silently create a tag at another commit; these options follow the current [`gh release create` manual](https://cli.github.com/manual/gh_release_create) (accessed 2026-08-02).

For automation, provide the upgrade level, title, and mode as arguments. Version numbers are not accepted as arguments:

```bash
./scripts/release.sh --dry-run --title "Release title" patch
./scripts/release.sh --publish --yes --title "Release title" patch
```

Use `--yes` only to authorize the displayed version update, version commit, and publication without a final interactive confirmation.

### Release recovery

Stop after any publishing failure; completed local or remote steps are not automatically undone.

| Failure point | Recovery from the repository root | Resume and completion |
| --- | --- | --- |
| Writing or committing `VERSION` | Repair the local error and inspect the diff; with authorization, finish the version commit and restore a clean working tree | Run `./scripts/release.sh --retry` and enter the same title after completing the version commit; complete when the Release URL is reported |
| Push, tag, or Release creation after the version commit | Resolve the external error without changing `HEAD` or `VERSION` | Run `./scripts/release.sh --retry` and enter the same title; an existing tag is accepted only at `HEAD`, and no extra version commit is created |
| Release already exists | Verify the existing Release; do not overwrite or move its tag | If publication succeeded, complete; otherwise decide whether a new version is required |

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
