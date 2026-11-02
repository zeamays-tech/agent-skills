#!/usr/bin/env bash

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME=""
SKILL_FILE=""
TEMP_RELEASE_DIR=""
REMOTE="origin"
DRY_RUN=0
ASSUME_YES=0
TEMP_NPM_CACHE=""
LOCAL_RELEASE_TAG=""

usage() {
  cat <<EOF
Usage:
  $SCRIPT_NAME
  $SCRIPT_NAME [--dry-run | --publish] [--title <text>] [--yes]
               [--remote <name>] [--skill <name>] [major | minor | patch | --current | --retry]

Validate and publish a single Skill SemVer release.

Show the current version and prompt for an upgrade level, title, and mode.

Arguments:
  major|minor|patch  Optional upgrade level; otherwise prompt (default: patch).
                      The new version is calculated from metadata.version.

Options:
  --skill <name>      Select a Skill directory; otherwise prompt.
  --current           Publish the current metadata.version without incrementing.
  --retry             Resume an unfinished release using metadata.version without incrementing.
  --dry-run           Run preflight checks and print publishing commands without
                      changing SKILL.md, committing, tagging, pushing, or creating a Release.
  --publish           Select publishing mode without a mode prompt.
  --title <text>      Set a nonblank GitHub Release title; otherwise prompt.
  --yes               Skip the interactive publishing confirmation.
  --remote <name>     Git remote to publish through (default: origin).
  -h, --help          Show this help text.
EOF
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

cleanup() {
  local exit_code=$?
  if ((exit_code != 0)) && [[ -n "$LOCAL_RELEASE_TAG" ]]; then
    printf 'Local release %s (Skill version commit and tag) is retained. Resolve the error, then run %s --skill %s --retry with the same title.\n' "$LOCAL_RELEASE_TAG" "$SCRIPT_NAME" "$SKILL_NAME" >&2
  fi
  if [[ -n "$TEMP_RELEASE_DIR" ]]; then
    rm -rf -- "$TEMP_RELEASE_DIR"
  fi
  if [[ -n "$TEMP_NPM_CACHE" ]]; then
    rm -rf -- "$TEMP_NPM_CACHE"
  fi
}

validate_release_tag() {
  local tag="${1:-}"
  local without_build prerelease identifier
  local -a prerelease_identifiers=()

  [[ "$tag" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$ ]] || return 1

  without_build="${tag%%+*}"
  if [[ "$without_build" == *-* ]]; then
    prerelease="${without_build#*-}"
    IFS='.' read -r -a prerelease_identifiers <<<"$prerelease"
    for identifier in "${prerelease_identifiers[@]}"; do
      if [[ "$identifier" =~ ^[0-9]+$ && "$identifier" != "0" && "$identifier" == 0* ]]; then
        return 1
      fi
    done
  fi
}

read_release_tag() {
  local version

  version="$(python3 "$SCRIPT_DIR/skill_version.py" "$SKILL_FILE")" || return 1
  validate_release_tag "v$version" || die "metadata.version must contain SemVer without a leading v"
  printf 'v%s\n' "$version"
}

release_not_older() {
  validate_release_tag "$1" && validate_release_tag "$2" || return 1
  python3 - "$1" "$2" <<'PY'
import sys


def precedence(tag):
    version = tag[1:].split("+", 1)[0]
    core, separator, prerelease = version.partition("-")
    identifiers = tuple(
        (0, int(item)) if item.isdigit() else (1, item)
        for item in prerelease.split(".")
    ) if separator else ()
    return tuple(map(int, core.split("."))), not separator, identifiers


sys.exit(0 if precedence(sys.argv[1]) >= precedence(sys.argv[2]) else 1)
PY
}

check_release_tags() {
  local existing_tag
  while IFS= read -r existing_tag; do
    if validate_release_tag "${existing_tag#"$SKILL_NAME-"}"; then
      release_not_older "${1#"$SKILL_NAME-"}" "${existing_tag#"$SKILL_NAME-"}" || die "Release version must not be older than existing tag $existing_tag"
      git merge-base --is-ancestor "$existing_tag" HEAD || die "Skill release $existing_tag is not an ancestor of HEAD"
    fi
  done < <(git tag --list "$SKILL_NAME-v*")
}

next_release_tag() {
  validate_release_tag "$1" || return 1
  case "$2" in major | minor | patch) ;; *) return 1 ;; esac
  python3 - "$1" "$2" <<'PY'
import sys

core = sys.argv[1][1:].split("+", 1)[0].split("-", 1)[0]
parts = list(map(int, core.split(".")))
index = {"major": 0, "minor": 1, "patch": 2}[sys.argv[2]]
parts[index] += 1
parts[index + 1:] = [0] * (2 - index)
print("v" + ".".join(map(str, parts)))
PY
}

prompt_release_bump() {
  local current_tag="$1"
  local input

  printf 'Upgrade level:\n' >&2
  printf '  1) major -> %s\n' "$(next_release_tag "$current_tag" major)" >&2
  printf '  2) minor -> %s\n' "$(next_release_tag "$current_tag" minor)" >&2
  printf '  3) patch -> %s\n' "$(next_release_tag "$current_tag" patch)" >&2
  while true; do
    printf 'Select upgrade [3]: ' >&2
    IFS= read -r input || die "Upgrade input ended unexpectedly"
    case "${input:-3}" in
      1 | major) printf 'major\n'; return 0 ;;
      2 | minor) printf 'minor\n'; return 0 ;;
      3 | patch) printf 'patch\n'; return 0 ;;
      *) printf 'Choose major, minor, or patch; custom versions are not accepted.\n' >&2 ;;
    esac
  done
}

prompt_release_title() {
  local input

  while true; do
    printf 'Release title: ' >&2
    IFS= read -r input || die "Release title input ended unexpectedly"
    if [[ -n "${input//[[:space:]]/}" ]]; then
      printf '%s\n' "$input"
      return 0
    fi
    printf 'Release title must not be blank.\n' >&2
  done
}

write_release_version() {
  validate_release_tag "$1" || die "Invalid version: $1"
  python3 "$SCRIPT_DIR/skill_version.py" "$SKILL_FILE" "${1#v}"
}

prompt_release_mode() {
  local input

  while true; do
    printf 'Release mode:\n' >&2
    printf '  1) Dry run (recommended first)\n' >&2
    printf '  2) Publish\n' >&2
    printf 'Select mode [1]: ' >&2
    IFS= read -r input || die "Release mode input ended unexpectedly"
    case "${input:-1}" in
      1 | dry-run)
        printf 'dry-run\n'
        return 0
        ;;
      2 | publish)
        printf 'publish\n'
        return 0
        ;;
      *)
        printf 'Choose 1 (dry run) or 2 (publish).\n' >&2
        ;;
    esac
  done
}

print_command() {
  printf '+'
  printf ' %q' "$@"
  printf '\n'
}

run_mutation() {
  print_command "$@"
  if ((DRY_RUN == 0)); then
    "$@"
  fi
}

main() {
  local release_tag=""
  local bump=""
  local retry=0
  local release_title=""
  local mode_option=""
  local selected_mode=""
  local repository_root remote_url repository_slug branch default_branch head tag_commit answer release_url
  local version_tag next_version_tag npm_cache archive_path
  local tag_exists=0
  local -a release_command

  while (($# > 0)); do
    case "$1" in
      --dry-run)
        [[ -z "$mode_option" || "$mode_option" == "dry-run" ]] || die "--dry-run and --publish cannot be combined"
        mode_option="dry-run"
        ;;
      --publish)
        [[ -z "$mode_option" || "$mode_option" == "publish" ]] || die "--dry-run and --publish cannot be combined"
        mode_option="publish"
        ;;
      --title)
        (($# >= 2)) || die "--title requires a value"
        release_title="$2"
        shift
        ;;
      --skill)
        (($# >= 2)) || die "--skill requires a value"
        SKILL_NAME="$2"
        shift
        ;;
      --retry | --current)
        retry=1
        ;;
      --yes)
        ASSUME_YES=1
        ;;
      --remote)
        (($# >= 2)) || die "--remote requires a value"
        REMOTE="$2"
        shift
        ;;
      -h | --help)
        usage
        return 0
        ;;
      -*)
        die "Unknown option: $1"
        ;;
      major | minor | patch)
        [[ -z "$bump" ]] || die "Only one upgrade level may be provided"
        bump="$1"
        ;;
      *)
        die "Choose major, minor, or patch; custom versions are not accepted"
        ;;
    esac
    shift
  done

  [[ "$retry" == 0 || -z "$bump" ]] || die "--retry/--current cannot be combined with an upgrade level"
  [[ -z "$release_title" || -n "${release_title//[[:space:]]/}" ]] || die "Release title must not be blank"
  [[ "$REMOTE" =~ ^[A-Za-z0-9._-]+$ ]] || die "Invalid remote name: $REMOTE"

  require_command git
  repository_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this script from a Git repository"
  cd "$repository_root"

  require_command python3
  if [[ -z "$SKILL_NAME" ]]; then
    printf 'Available Skills:\n' >&2
    for skill_path in skills/*/SKILL.md; do
      [[ -f "$skill_path" ]] && printf '  %s\n' "${skill_path%/SKILL.md}" >&2
    done
    printf 'Skill name: ' >&2
    IFS= read -r SKILL_NAME || die "Skill input ended unexpectedly"
  fi
  [[ "$SKILL_NAME" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || die "Invalid Skill name"
  SKILL_FILE="skills/$SKILL_NAME/SKILL.md"
  [[ -f "$SKILL_FILE" && ! -L "$SKILL_FILE" && ! -L "skills/$SKILL_NAME" ]] || die "Skill not found or is a symlink: $SKILL_NAME"
  version_tag="$(read_release_tag)" || exit 1
  printf '\nInteractive release setup\n' >&2
  printf 'Current version (%s): %s\n' "$SKILL_NAME" "${version_tag#v}" >&2
  if ((retry == 1)); then
    next_version_tag="$version_tag"
    printf 'Using current Skill version: %s\n' "$SKILL_NAME-$next_version_tag" >&2
  else
    if [[ -z "$bump" ]]; then
      bump="$(prompt_release_bump "$version_tag")"
    fi
    next_version_tag="$(next_release_tag "$version_tag" "$bump")"
    printf 'New version (%s): %s\n' "$bump" "${next_version_tag#v}" >&2
  fi
  release_not_older "$next_version_tag" "$version_tag" || die "Release version must not be older than metadata.version ($version_tag)"
  release_tag="$SKILL_NAME-$next_version_tag"
  if [[ -z "$release_title" ]]; then
    release_title="$(prompt_release_title)"
  fi
  if [[ -z "$mode_option" ]]; then
    mode_option="$(prompt_release_mode)"
  fi
  selected_mode="$mode_option"
  if [[ "$selected_mode" == "dry-run" ]]; then
    DRY_RUN=1
  else
    DRY_RUN=0
  fi

  require_command gh
  require_command npx
  require_command mktemp

  trap cleanup EXIT
  printf 'Checking working tree...\n' >&2
  [[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "Working tree must be clean before release"

  remote_url="$(git remote get-url "$REMOTE" 2>/dev/null)" || die "Git remote not found: $REMOTE"
  case "$remote_url" in
    git@github.com:*)
      repository_slug="${remote_url#git@github.com:}"
      ;;
    https://github.com/*)
      repository_slug="${remote_url#https://github.com/}"
      ;;
    ssh://git@github.com/*)
      repository_slug="${remote_url#ssh://git@github.com/}"
      ;;
    *)
      die "Remote $REMOTE must point to GitHub: $remote_url"
      ;;
  esac
  repository_slug="${repository_slug%.git}"
  repository_slug="${repository_slug%/}"
  [[ "$repository_slug" =~ ^[^/]+/[^/]+$ ]] || die "Could not derive owner/repository from $remote_url"

  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)" || die "Releases must be created from a branch, not detached HEAD"
  default_branch="$(git symbolic-ref --quiet "refs/remotes/$REMOTE/HEAD")" || die "Remote default branch is not cached; run git remote set-head $REMOTE -a while connected, then retry"
  default_branch="${default_branch#refs/remotes/$REMOTE/}"
  [[ "$branch" == "$default_branch" ]] || die "Release from the cached default branch ($default_branch), not $branch"
  git merge-base --is-ancestor "$REMOTE/$default_branch" HEAD || die "Local $branch is behind or diverged from cached $REMOTE/$default_branch"
  head="$(git rev-parse HEAD)"
  check_release_tags "$release_tag"

  if git show-ref --verify --quiet "refs/tags/$release_tag"; then
    tag_commit="$(git rev-list -n 1 "$release_tag")"
    [[ "$tag_commit" == "$head" ]] || die "Existing tag $release_tag does not point to HEAD"
    [[ "$next_version_tag" == "$version_tag" ]] || die "Existing tag does not match metadata.version; cannot change a tagged release"
    tag_exists=1
  fi

  printf 'Running repository validation...\n'
  python3 -m unittest discover -s tests -v
  npm_cache="${NPM_CONFIG_CACHE:-${npm_config_cache:-}}"
  if [[ -z "$npm_cache" ]]; then
    TEMP_NPM_CACHE="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-release-npm.XXXXXX")"
    npm_cache="$TEMP_NPM_CACHE"
  fi
  printf 'Validating Skill discovery (npx may download the CLI)...\n' >&2
  npm_config_cache="$npm_cache" npx --yes skills@latest add "./skills/$SKILL_NAME" --list
  [[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "Validation changed the working tree; review it before release"

  printf '\nRelease plan\n'
  printf '  Repository: %s\n' "$repository_slug"
  printf '  Branch:     %s\n' "$branch"
  printf '  Base commit: %s\n' "$head"
  printf '  Skill:      %s\n' "$SKILL_NAME"
  printf '  Version:    %s -> %s\n' "${version_tag#v}" "${next_version_tag#v}"
  if [[ "$next_version_tag" != "$version_tag" ]]; then
    printf '  Version update: update selected SKILL.md and commit chore(release): %s\n' "$release_tag"
  fi
  printf '  Tag:        %s\n' "$release_tag"
  printf '  Asset:      %s.zip\n' "$release_tag"
  printf '  Title:      %s\n' "$release_title"
  printf '  Mode:       %s\n' "$([[ "$DRY_RUN" -eq 1 ]] && printf 'dry run' || printf 'publish')"

  if ((DRY_RUN == 0 && ASSUME_YES == 0)); then
    [[ -t 0 ]] || die "Interactive confirmation unavailable; rerun with --yes"
    read -r -p "Apply this version/commit plan and publish $release_tag? [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]] || die "Release cancelled"
  fi

  if [[ "$next_version_tag" != "$version_tag" ]]; then
    run_mutation write_release_version "$next_version_tag"
    run_mutation git add -- "$SKILL_FILE"
    run_mutation git commit -m "chore(release): $release_tag" -- "$SKILL_FILE"
    if ((DRY_RUN == 0)); then
      [[ "$(read_release_tag)" == "$next_version_tag" ]] || die "metadata.version changed during commit; review before retrying"
      [[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "Commit left local changes; review before retrying"
    fi
  fi

  if ((tag_exists == 0)); then
    run_mutation git tag -a "$release_tag" -m "$release_title"
  fi

  if ((DRY_RUN == 1)); then
    printf '\nDry run complete; local validation passed. SKILL.md, commits, and tags are unchanged. Remote checks and publication were not run.\n'
    return 0
  fi

  LOCAL_RELEASE_TAG="$release_tag"
  head="$(git rev-parse HEAD)"
  printf '\nLocal release ready: %s at %s (Skill version commit and tag).\n' "$release_tag" "$head"
  printf 'Checking GitHub authentication...\n' >&2
  gh auth status --hostname github.com >/dev/null
  printf 'Reading GitHub default branch...\n' >&2
  default_branch="$(gh repo view "$repository_slug" --json defaultBranchRef --jq '.defaultBranchRef.name')"
  [[ -n "$default_branch" ]] || die "Could not determine the GitHub default branch"
  [[ "$branch" == "$default_branch" ]] || die "Release from the GitHub default branch ($default_branch), not $branch"

  printf 'Fetching branches and tags from %s...\n' "$REMOTE" >&2
  git fetch --progress "$REMOTE" --tags
  git merge-base --is-ancestor "$REMOTE/$default_branch" HEAD || die "Local $branch is behind or diverged from $REMOTE/$default_branch"
  check_release_tags "$release_tag"
  printf 'Checking whether GitHub Release %s already exists...\n' "$release_tag" >&2
  if gh release view "$release_tag" --repo "$repository_slug" >/dev/null 2>&1; then
    die "GitHub Release $release_tag already exists; choose a new version"
  fi

  TEMP_RELEASE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agent-skill-release.XXXXXX")"
  archive_path="$TEMP_RELEASE_DIR/$release_tag.zip"
  git archive --format=zip --prefix="$SKILL_NAME/" --output="$archive_path" "$release_tag:skills/$SKILL_NAME"

  run_mutation git push "$REMOTE" "HEAD:refs/heads/$default_branch"
  run_mutation git push "$REMOTE" "refs/tags/$release_tag"

  release_command=(
    gh release create "$release_tag" "$archive_path"
    --title "$release_title"
    --notes "Release $SKILL_NAME ${next_version_tag#v}. Source: https://github.com/$repository_slug/tree/$release_tag/skills/$SKILL_NAME . The attached ZIP contains this Skill only."
    --verify-tag
    --latest=false
    --repo "$repository_slug"
  )
  if [[ "${next_version_tag%%+*}" == *-* ]]; then
    release_command+=(--prerelease)
  fi
  run_mutation "${release_command[@]}"

  release_url="$(gh release view "$release_tag" --repo "$repository_slug" --json url --jq '.url')"
  LOCAL_RELEASE_TAG=""
  printf '\nPublished %s\n' "$release_url"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
