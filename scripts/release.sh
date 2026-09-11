#!/usr/bin/env bash

set -euo pipefail

SCRIPT_NAME="$(basename "$0")"
REMOTE="origin"
DRY_RUN=0
ASSUME_YES=0
TEMP_NPM_CACHE=""

usage() {
  cat <<EOF
Usage:
  $SCRIPT_NAME
  $SCRIPT_NAME [--dry-run | --publish] [--title <text>] [--yes]
               [--remote <name>] [major | minor | patch | --retry]

Validate and publish a repository-wide SemVer release.

Show the current version and prompt for an upgrade level, title, and mode.

Arguments:
  major|minor|patch  Optional upgrade level; otherwise prompt (default: patch).
                      The new version is calculated from VERSION.

Options:
  --retry             Resume an unfinished release using VERSION without incrementing.
  --dry-run           Run preflight checks and print publishing commands without
                      changing VERSION, committing, tagging, pushing, or creating a Release.
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

  [[ -f VERSION ]] || die "Missing VERSION file at repository root"
  version="$(<VERSION)"
  validate_release_tag "v$version" || die "VERSION must contain SemVer without a leading v"
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
  printf '%s\n' "${1#v}" > VERSION
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
  local latest_release_tag version_tag existing_tag commit_count npm_cache
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
      --retry)
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

  [[ "$retry" == 0 || -z "$bump" ]] || die "--retry cannot be combined with an upgrade level"
  [[ -z "$release_title" || -n "${release_title//[[:space:]]/}" ]] || die "Release title must not be blank"
  [[ "$REMOTE" =~ ^[A-Za-z0-9._-]+$ ]] || die "Invalid remote name: $REMOTE"

  require_command git
  repository_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this script from a Git repository"
  cd "$repository_root"

  require_command python3
  version_tag="$(read_release_tag)" || exit 1
  printf '\nInteractive release setup\n' >&2
  printf 'Current version (VERSION): %s\n' "${version_tag#v}" >&2
  if ((retry == 1)); then
    release_tag="$version_tag"
    printf 'Retrying unfinished release: %s\n' "$release_tag" >&2
  else
    if [[ -z "$bump" ]]; then
      bump="$(prompt_release_bump "$version_tag")"
    fi
    release_tag="$(next_release_tag "$version_tag" "$bump")"
    printf 'New version (%s): %s\n' "$bump" "${release_tag#v}" >&2
  fi
  release_not_older "$release_tag" "$version_tag" || die "Release version must not be older than VERSION ($version_tag)"
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

  gh auth status --hostname github.com >/dev/null
  default_branch="$(gh repo view "$repository_slug" --json defaultBranchRef --jq '.defaultBranchRef.name')"
  [[ -n "$default_branch" ]] || die "Could not determine the GitHub default branch"

  branch="$(git symbolic-ref --quiet --short HEAD 2>/dev/null)" || die "Releases must be created from a branch, not detached HEAD"
  [[ "$branch" == "$default_branch" ]] || die "Release from the GitHub default branch ($default_branch), not $branch"

  git fetch "$REMOTE" --tags
  git merge-base --is-ancestor "$REMOTE/$default_branch" HEAD || die "Local $branch is behind or diverged from $REMOTE/$default_branch"

  head="$(git rev-parse HEAD)"
  latest_release_tag="$(gh release view --repo "$repository_slug" --json tagName --jq '.tagName' 2>/dev/null || true)"

  printf 'Latest GitHub release: %s\n' "${latest_release_tag:-none}" >&2
  while IFS= read -r existing_tag; do
    if validate_release_tag "$existing_tag"; then
      release_not_older "$release_tag" "$existing_tag" || die "Release version must not be older than existing tag $existing_tag"
    fi
  done < <(git tag --list)

  if git show-ref --verify --quiet "refs/tags/$release_tag"; then
    tag_commit="$(git rev-list -n 1 "$release_tag")"
    [[ "$tag_commit" == "$head" ]] || die "Existing tag $release_tag does not point to HEAD"
    [[ "$release_tag" == "$version_tag" ]] || die "Existing tag does not match VERSION; cannot change a tagged release"
    tag_exists=1
  fi

  if gh release view "$release_tag" --repo "$repository_slug" >/dev/null 2>&1; then
    die "GitHub Release $release_tag already exists; choose a new version"
  fi

  if [[ -n "$latest_release_tag" ]]; then
    git show-ref --verify --quiet "refs/tags/$latest_release_tag" || die "Latest release tag is missing locally after fetch: $latest_release_tag"
    git merge-base --is-ancestor "$latest_release_tag" HEAD || die "Latest release $latest_release_tag is not an ancestor of HEAD"
    commit_count="$(git rev-list --count "$latest_release_tag..HEAD")"
    ((commit_count > 0)) || die "No commits exist after the latest release ($latest_release_tag)"
  fi

  printf 'Running repository validation...\n'
  python3 -m unittest discover -s tests -v
  npm_cache="${NPM_CONFIG_CACHE:-${npm_config_cache:-}}"
  if [[ -z "$npm_cache" ]]; then
    TEMP_NPM_CACHE="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-release-npm.XXXXXX")"
    trap cleanup EXIT
    npm_cache="$TEMP_NPM_CACHE"
  fi
  npm_config_cache="$npm_cache" npx --yes skills@latest add . --list
  [[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "Validation changed the working tree; review it before release"

  printf '\nRelease plan\n'
  printf '  Repository: %s\n' "$repository_slug"
  printf '  Branch:     %s\n' "$branch"
  printf '  Base commit: %s\n' "$head"
  printf '  VERSION:    %s -> %s\n' "${version_tag#v}" "${release_tag#v}"
  if [[ "$release_tag" != "$version_tag" ]]; then
    printf '  Version update: write VERSION and commit chore(release): %s\n' "$release_tag"
  fi
  printf '  Tag:        %s\n' "$release_tag"
  printf '  Title:      %s\n' "$release_title"
  printf '  Mode:       %s\n' "$([[ "$DRY_RUN" -eq 1 ]] && printf 'dry run' || printf 'publish')"

  if ((DRY_RUN == 0 && ASSUME_YES == 0)); then
    [[ -t 0 ]] || die "Interactive confirmation unavailable; rerun with --yes"
    read -r -p "Apply this version/commit plan and publish $release_tag? [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]] || die "Release cancelled"
  fi

  if [[ "$release_tag" != "$version_tag" ]]; then
    run_mutation write_release_version "$release_tag"
    run_mutation git add -- VERSION
    run_mutation git commit -m "chore(release): $release_tag" -- VERSION
    if ((DRY_RUN == 0)); then
      [[ "$(read_release_tag)" == "$release_tag" ]] || die "VERSION changed during commit; review before retrying"
      [[ -z "$(git status --porcelain=v1 --untracked-files=all)" ]] || die "Commit left local changes; review before retrying"
    fi
  fi

  run_mutation git push "$REMOTE" "HEAD:refs/heads/$default_branch"
  if ((tag_exists == 0)); then
    run_mutation git tag -a "$release_tag" -m "$release_title"
  fi
  run_mutation git push "$REMOTE" "refs/tags/$release_tag"

  release_command=(
    gh release create "$release_tag"
    --title "$release_title"
    --generate-notes
    --verify-tag
    --fail-on-no-commits
    --repo "$repository_slug"
  )
  if [[ "${release_tag%%+*}" == *-* ]]; then
    release_command+=(--prerelease)
  fi
  run_mutation "${release_command[@]}"

  if ((DRY_RUN == 1)); then
    printf '\nDry run complete; VERSION, commits, tags, and GitHub Releases are unchanged; nothing was pushed.\n'
    return 0
  fi

  release_url="$(gh release view "$release_tag" --repo "$repository_slug" --json url --jq '.url')"
  printf '\nPublished %s\n' "$release_url"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
