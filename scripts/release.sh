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
               [--remote <name>] [<release-tag>]

Validate and publish a repository-wide SemVer release.

Run without a release tag to enter the interactive release dialogue.

Arguments:
  <release-tag>       Optional SemVer tag with a leading "v" (for example,
                      v1.2.3). When omitted, the script prompts for it.

Options:
  --dry-run           Run preflight checks and print publishing commands without
                      creating a tag, pushing, or creating a GitHub Release.
  --publish           Select publishing mode without a mode prompt.
  --title <text>      Set the GitHub Release title (default: release tag).
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

suggest_next_release_tag() {
  local latest_tag="${1:-}"
  local version core major minor patch

  if ! validate_release_tag "$latest_tag"; then
    printf 'v0.1.0\n'
    return 0
  fi

  version="${latest_tag#v}"
  version="${version%%+*}"
  core="${version%%-*}"
  IFS='.' read -r major minor patch <<<"$core"

  if [[ "$version" == *-* ]]; then
    printf 'v%s.%s.%s\n' "$major" "$minor" "$patch"
    return 0
  fi

  printf 'v%s.%s.%s\n' "$major" "$minor" "$((patch + 1))"
}

prompt_release_tag() {
  local suggested_tag="$1"
  local input

  while true; do
    printf 'Release tag [%s]: ' "$suggested_tag" >&2
    IFS= read -r input || die "Release tag input ended unexpectedly"
    input="${input:-$suggested_tag}"
    if validate_release_tag "$input"; then
      printf '%s\n' "$input"
      return 0
    fi
    printf 'Enter valid SemVer with a leading v (for example, v1.2.3).\n' >&2
  done
}

prompt_release_title() {
  local release_tag="$1"
  local input

  printf 'Release title [%s]: ' "$release_tag" >&2
  IFS= read -r input || die "Release title input ended unexpectedly"
  printf '%s\n' "${input:-$release_tag}"
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
  local release_title=""
  local mode_option=""
  local selected_mode=""
  local interactive=0
  local repository_root remote_url repository_slug branch default_branch head tag_commit answer release_url
  local latest_release_tag suggested_tag commit_count npm_cache
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
      *)
        [[ -z "$release_tag" ]] || die "Only one release tag may be provided"
        release_tag="$1"
        ;;
    esac
    shift
  done

  if [[ -z "$release_tag" ]]; then
    interactive=1
  else
    validate_release_tag "$release_tag" || die "Release tag must be valid SemVer with a leading v: $release_tag"
  fi
  [[ -z "$release_title" || -n "${release_title//[[:space:]]/}" ]] || die "Release title must not be blank"
  [[ "$REMOTE" =~ ^[A-Za-z0-9._-]+$ ]] || die "Invalid remote name: $REMOTE"

  require_command git
  require_command gh
  require_command python3
  require_command npx
  require_command mktemp

  repository_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die "Run this script from a Git repository"
  cd "$repository_root"

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

  if ((interactive == 1)); then
    suggested_tag="$(suggest_next_release_tag "$latest_release_tag")"
    printf '\nInteractive release setup\n' >&2
    printf 'Latest release: %s\n' "${latest_release_tag:-none}" >&2
    release_tag="$(prompt_release_tag "$suggested_tag")"
    if [[ -z "$release_title" ]]; then
      release_title="$(prompt_release_title "$release_tag")"
    fi
    if [[ -z "$mode_option" ]]; then
      mode_option="$(prompt_release_mode)"
    fi
  fi

  validate_release_tag "$release_tag" || die "Release tag must be valid SemVer with a leading v: $release_tag"
  release_title="${release_title:-$release_tag}"
  [[ -n "${release_title//[[:space:]]/}" ]] || die "Release title must not be blank"
  selected_mode="${mode_option:-publish}"
  if [[ "$selected_mode" == "dry-run" ]]; then
    DRY_RUN=1
  else
    DRY_RUN=0
  fi

  if git show-ref --verify --quiet "refs/tags/$release_tag"; then
    tag_commit="$(git rev-list -n 1 "$release_tag")"
    [[ "$tag_commit" == "$head" ]] || die "Existing tag $release_tag does not point to HEAD"
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
  printf '  Commit:     %s\n' "$head"
  printf '  Tag:        %s\n' "$release_tag"
  printf '  Title:      %s\n' "$release_title"
  printf '  Mode:       %s\n' "$([[ "$DRY_RUN" -eq 1 ]] && printf 'dry run' || printf 'publish')"

  if ((DRY_RUN == 0 && ASSUME_YES == 0)); then
    [[ -t 0 ]] || die "Interactive confirmation unavailable; rerun with --yes"
    read -r -p "Publish $release_tag? [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]] || die "Release cancelled"
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
    printf '\nDry run complete; no tag, push, or GitHub Release was created.\n'
    return 0
  fi

  release_url="$(gh release view "$release_tag" --repo "$repository_slug" --json url --jq '.url')"
  printf '\nPublished %s\n' "$release_url"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
