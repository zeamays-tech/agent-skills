# Track the Shared Repository Version in a File

- Status: Accepted
- Date: 2026-09-11

## Context

Reading the repository version should not require querying Git tags. Skills already share a repository-wide release version under the [distribution decision](0001-open-agent-skills-primary-distribution.md).

## Decision

Keep a root `VERSION` file containing the shared SemVer value without a leading `v`. Retain the last release value during development, then let the release script update and commit it during a confirmed publishing run. Initialize it from the existing published release when adopting this convention.

The release script displays the current version and offers only major/minor/patch upgrades and prompts for a title. It calculates the next stable version, resetting lower components and removing prerelease/build suffixes; custom version input is not supported. A recovery-only `--retry` resumes the current version without incrementing it. It rejects SemVer downgrades against the file and fetched release tags. After validation and publishing confirmation, it updates and commits only the version file when the value changes, before tagging that commit. Dry runs leave the file and commit history unchanged. Tags and GitHub Releases remain the evidence of publication; a version file alone does not establish that a working tree or prepared release has been published.

## Consequences

- Readers can inspect one file for the shared version; Skills do not acquire independent version fields or runtime dependencies.
- Release preparation starts from a clean checkout. The publishing confirmation covers the version commit and remote publication; failed publication may leave a prepared version commit for retry.
- Tagged snapshots carry their own version file from adoption onward. Existing tags and separately installed copies are not rewritten.
- Current operating instructions live in the root [README](../../README.md#versioning).
