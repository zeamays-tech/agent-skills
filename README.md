# Agent Skills

Open, versioned, and portable Agent Skills for AI coding agents.

This repository publishes Skills in the lightweight [Agent Skills open format](https://agentskills.io/specification). The GitHub repository is the authoritative source for released Skill content.

## Available Skills

| Skill | Purpose |
| --- | --- |
| [`documentation-governance`](skills/documentation-governance/SKILL.md) | Create, modify, review, and synchronize software documentation while separating current guidance from decision and migration history. |
| [`chinese-technical-writing`](skills/chinese-technical-writing/SKILL.md) | Write, update, translate, and review Chinese technical documentation with clear, natural expression from the first draft, grounded in project facts and reader needs. |
| [`reconcile-project-state`](skills/reconcile-project-state/SKILL.md) | Discover, audit, correct within authorization, and gate inconsistencies across intended, executable, and evidence state. |
| [`evidence-driven-debugging`](skills/evidence-driven-debugging/SKILL.md) | Diagnose ambiguous failures with informative experiments, fewer manual retries, and regression checks across the complete result path. |

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

Use the direct GitHub tree source documented by the [`skills` CLI source formats](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#source-formats), replacing the tag and Skill name. This pins installation to the repository content published by that tag:

```bash
skill_name="replace-with-skill-name"
skill_version="replace-with-published-version"
release_tag="${skill_name}-v${skill_version}"
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
- [`chinese-technical-writing` invocation and consumer integration](skills/chinese-technical-writing/SKILL.md#调用与接入)
- [`reconcile-project-state` consumer integration](skills/reconcile-project-state/references/consumer-integration.md)
- [`evidence-driven-debugging` invocation and consumer integration](skills/evidence-driven-debugging/SKILL.md#invoke-and-integrate)

Treat the installed Skill's `SKILL.md` and directly linked references as the usage authority available to both agents and people after installation.

Compatible agents may also activate it automatically from the `name` and `description` fields. The optional `agents/openai.yaml` improves one client interface but is not required by the Skill.

## Versioning

Each Skill has an independent SemVer string in its `SKILL.md` under `metadata.version`. The [Agent Skills metadata specification](https://agentskills.io/specification#metadata-field) permits custom string values; version selection and publication are repository conventions, not automatic installer behavior (accessed 2026-11-02).

Use this canonical YAML layout so the release script can change only the version value without rewriting descriptions or instructions:

```yaml
metadata:
  version: "1.0.0"
```

Version increments affect only the selected Skill. Read its metadata for the prepared version; a tag and GitHub Release establish publication. Each release tag is `<skill-name>-v<version>`, and its asset is `<skill-name>-v<version>.zip`, containing only that Skill directory. See the [independent-version decision](docs/decisions/0004-independent-skill-releases.md).

Choose increments using [Semantic Versioning](https://semver.org/): patch for compatible fixes, minor for compatible capabilities, and major for breaking behavior or usage changes. The release script offers major/minor/patch, calculates the result, and removes any prerelease/build suffix when incrementing. It compares versions only against tags for the selected Skill. Existing tags and published assets remain immutable.

Install a specific version using the [tagged installation command](#install-a-specific-release). Writing a version in metadata does not create a downloadable release. Choose an available Skill-specific tag from the [Releases page](https://github.com/zeamays-tech/agent-skills/releases). For an installation pinned to an unavailable tag, select a published Skill version and rerun the tagged installation command.

## Release

Run from the repository root. The script requires Bash, standard Unix utilities including `basename`, `mktemp`, and `rm`, plus `git`, an authenticated [GitHub CLI](https://cli.github.com/manual/gh_auth_status), `python3`, and `npx`. Version editing uses Python's standard library and the canonical metadata layout above; it does not need a YAML dependency.

| Step | Entry point | Completion signal | Next step |
| --- | --- | --- | --- |
| Prepare | With authorization, commit release-ready changes on the cached remote default branch | Working tree is clean and the selected Skill has valid metadata | Validate |
| Validate | Run the script, select a Skill, upgrade level and title, then choose dry run | Local tests and Skill discovery pass; the displayed Skill, version and tag match the intended release | Publish; on failure, repair, commit with authorization, and retry Validate |
| Publish | Repeat the same selection in publish mode and confirm | The script reports the Release URL after uploading the selected Skill ZIP | Complete; on failure, follow [release recovery](#release-recovery) |

```bash
./scripts/release.sh
```

Dry run is the default mode. It leaves Skill files, commits and tags unchanged and does not contact Git/GitHub remotes. Skill discovery may download its CLI package. The discovery command uses `NPM_CONFIG_CACHE` or `npm_config_cache` when configured; otherwise, it creates an isolated temporary npm cache. Temporary archives and caches are cleaned on exit. Local checks do not establish remote readiness.

For a first publication at the metadata version, use `--current` to avoid incrementing `1.0.0`. For later releases, use major/minor/patch. For example:

```bash
skill_name="replace-with-skill-name"
./scripts/release.sh --skill "$skill_name" --current --dry-run --title "Initial release"
./scripts/release.sh --skill "$skill_name" --current --publish --title "Initial release"
```

For a subsequent patch release:

```bash
./scripts/release.sh --skill "$skill_name" --dry-run --title "Release title" patch
./scripts/release.sh --skill "$skill_name" --publish --title "Release title" patch
```

After publishing confirmation, the script updates only the selected Skill's version when an increment is requested, commits that `SKILL.md`, and creates its local annotated tag. `--current` and `--retry` use the metadata version without an extra version commit. Existing tags are accepted only when they point to `HEAD` and match the selected metadata version.

It then checks authentication and the remote default branch, fetches tags, and rejects a newer version of the same Skill or a branch/tag conflict. It creates the ZIP from the [tagged Git subtree](https://git-scm.com/docs/git-archive), pushes the branch and selected tag, and creates a GitHub Release with the ZIP asset. Different Skills may release from the same commit. Releases are not marked as the repository-wide latest release. Tag verification and latest-selection flags follow the [GitHub CLI manual](https://cli.github.com/manual/gh_release_create) (accessed 2026-11-02).

Local preparation uses the cached remote HEAD/default branch and cached tags. If that reference is missing, run `git remote set-head origin -a` while connected (substitute the configured remote when needed), then return to Validate. Fresh remote checks may still reveal conflicts after local preparation; the script stops without overwriting them.

Use `--yes` only when the caller has authorized the displayed version commit and publication. Neither dry run nor this documentation authorizes publishing.

### Release recovery

Stop after a publishing failure; completed local or remote steps are retained. Use the same `--skill` and title when retrying:

```bash
./scripts/release.sh --skill "$skill_name" --retry --publish --title "Release title"
```

| Failure point | Repair and safe resumption |
| --- | --- |
| Version write or commit | Inspect the selected `SKILL.md` diff. Repair the error and, with authorization, finish its version commit and restore a clean tree; then retry without incrementing |
| Local tag creation | Preserve the version commit, resolve the tag error without moving an existing tag, then retry |
| Authentication, fetch, ZIP creation or push | Preserve the version commit/tag, resolve access or remote conflicts, then retry; the ZIP is regenerated from the same tag |
| Release creation or upload | Inspect the Release for the exact Skill tag. If absent, retry. If present, verify its asset against the tagged Skill; an incomplete asset requires an explicitly authorized repair before completion |
| Release already exists | Verify the existing release and asset. The script stops rather than overwriting it; a different content version needs a new release |

Complete only when the reported Release contains the expected Skill archive. Never infer completion solely from a local version field or tag.

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
