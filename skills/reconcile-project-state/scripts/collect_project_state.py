#!/usr/bin/env python3
"""Collect a read-only, structured inventory of in-scope Git repositories."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def run_git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *arguments],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def decode(value: bytes) -> str:
    return value.decode("utf-8", errors="surrogateescape")


def relative_path(path: Path, root: Path) -> str:
    return Path(os.path.relpath(path, root)).as_posix()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def containing_repository(path: Path) -> Path | None:
    result = run_git(path, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    return Path(decode(result.stdout).strip()).resolve()


def discover_nested_repositories(root: Path, max_depth: int) -> set[Path]:
    repositories: set[Path] = set()
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        if depth > max_depth:
            directory_names[:] = []
            continue

        has_git_marker = ".git" in directory_names or ".git" in file_names
        if ".git" in directory_names:
            directory_names.remove(".git")
        if has_git_marker:
            repository = containing_repository(current_path)
            if repository is not None and is_within(repository, root):
                repositories.add(repository)

        if depth == max_depth:
            directory_names[:] = []
    return repositories


def parse_porcelain_status(raw: bytes) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    records = raw.split(b"\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        text = decode(record)
        if len(text) < 4 or text[2] != " ":
            entries.append({"index": "?", "worktree": "?", "path": text})
            continue

        status = text[:2]
        entry = {
            "index": status[0],
            "worktree": status[1],
            "path": text[3:],
        }
        if (status[0] in "RC" or status[1] in "RC") and index < len(records):
            original = records[index]
            index += 1
            if original:
                entry["original_path"] = decode(original)
        entries.append(entry)
    return entries


def governance_files(repo: Path, scope_root: Path) -> list[str]:
    result = run_git(
        repo,
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "-z",
        "--",
        "AGENTS.md",
        ":(glob)**/AGENTS.md",
    )
    if result.returncode == 0:
        return sorted(
            relative_path(repo / decode(item), scope_root)
            for item in result.stdout.split(b"\0")
            if item
        )

    files: list[str] = []
    for current, directory_names, file_names in os.walk(repo, followlinks=False):
        current_path = Path(current)
        if current_path != repo and (".git" in directory_names or ".git" in file_names):
            directory_names[:] = []
            continue
        if ".git" in directory_names:
            directory_names.remove(".git")
        if "AGENTS.md" in file_names:
            files.append(relative_path(current_path / "AGENTS.md", scope_root))
    return sorted(files)


def optional_git_text(repo: Path, *arguments: str) -> str | None:
    result = run_git(repo, *arguments)
    if result.returncode != 0:
        return None
    value = decode(result.stdout).strip()
    return value or None


def collect_repository(repo: Path, scope_root: Path, base_ref: str | None) -> dict[str, object]:
    errors: list[str] = []
    status_result = run_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if status_result.returncode == 0:
        working_tree = parse_porcelain_status(status_result.stdout)
    else:
        working_tree = []
        errors.append(f"git status failed: {decode(status_result.stderr).strip()}")

    base_changed_paths: list[str] | None = None
    if base_ref is not None:
        verified = run_git(repo, "rev-parse", "--verify", f"{base_ref}^{{commit}}")
        if verified.returncode != 0:
            errors.append(f"base ref is unavailable: {base_ref}")
        else:
            diff = run_git(repo, "diff", "--name-only", "-z", f"{base_ref}...HEAD")
            if diff.returncode != 0:
                errors.append(f"base comparison failed: {decode(diff.stderr).strip()}")
            else:
                base_changed_paths = sorted(
                    decode(item) for item in diff.stdout.split(b"\0") if item
                )

    branch = optional_git_text(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    head = optional_git_text(repo, "rev-parse", "--verify", "HEAD")
    upstream = optional_git_text(
        repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
    )

    return {
        "path": relative_path(repo, scope_root),
        "branch": branch,
        "detached": head is not None and branch is None,
        "head": head,
        "upstream": upstream,
        "governance_files": governance_files(repo, scope_root),
        "working_tree_clean": not working_tree,
        "working_tree": working_tree,
        "base_ref": base_ref,
        "base_changed_paths": base_changed_paths,
        "errors": errors,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Git repository boundaries and change state without writing files."
    )
    parser.add_argument("--root", default=".", help="Scope root; defaults to the current directory.")
    parser.add_argument(
        "--repository",
        action="append",
        default=[],
        help="Explicit repository path relative to the scope root; repeat as needed.",
    )
    parser.add_argument(
        "--discover-nested",
        action="store_true",
        help="Opt in to discovering nested Git repositories under the scope root.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=6,
        help="Maximum nested discovery depth; defaults to 6.",
    )
    parser.add_argument(
        "--base-ref",
        help="Optional, known Git base ref to compare with HEAD in each repository.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    if args.max_depth < 0:
        raise SystemExit("--max-depth must be zero or greater")

    scope_root = Path(args.root).expanduser().resolve()
    if not scope_root.is_dir():
        raise SystemExit(f"scope root is not a directory: {args.root}")

    repositories: set[Path] = set()
    if args.repository:
        for value in args.repository:
            candidate = (scope_root / value).resolve()
            if not is_within(candidate, scope_root):
                raise SystemExit(f"repository path escapes the scope root: {value}")
            repository = containing_repository(candidate)
            if repository is None or not is_within(repository, scope_root):
                raise SystemExit(f"not an in-scope Git repository: {value}")
            repositories.add(repository)
    else:
        repository = containing_repository(scope_root)
        if repository is not None:
            repositories.add(repository)

    if args.discover_nested:
        repositories.update(discover_nested_repositories(scope_root, args.max_depth))

    records = [
        collect_repository(repo, scope_root, args.base_ref)
        for repo in sorted(repositories, key=lambda path: relative_path(path, scope_root))
    ]
    result = {
        "schema_version": 1,
        "scope_root": ".",
        "read_only": True,
        "nested_discovery": bool(args.discover_nested),
        "repositories": records,
        "warnings": [] if records else ["No Git repository was discovered in the selected scope."],
    }
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
