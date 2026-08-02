#!/usr/bin/env python3
"""Validate a reconciliation ledger and derive its gate result."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import PurePosixPath
from typing import Iterable


MODES = {"impact", "audit", "reconcile", "gate", "post-deploy"}
PLANES = {"intended", "executable", "evidence"}
AUTHORITIES = {"declared", "provisional", "supporting"}
MISMATCH_CLASSES = {
    "source-conflict",
    "missing-link",
    "stale-intent",
    "executable-drift",
    "incomplete-implementation",
    "insufficient-evidence",
    "environment-divergence",
    "ambiguous-authority",
    "out-of-scope",
}
MISMATCH_STATUSES = {"open", "resolved", "accepted-risk"}
ACTION_STATUSES = {"applied", "proposed", "skipped"}
VERIFICATION_STATUSES = {"passed", "failed", "blocked", "not-run", "unverified"}
GATE_DECISIONS = {"pass", "fail", "blocked", "not-assessed"}
CONFLICT_CLASSES = {"source-conflict", "ambiguous-authority"}
BLOCKED_MISMATCH_CLASSES = {"ambiguous-authority", "insufficient-evidence", "out-of-scope"}
DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")


def non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def relative_ledger_path(value: object) -> str | None:
    if not non_empty_string(value):
        return None
    normalized = str(value).replace("\\", "/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or DRIVE_PREFIX.match(normalized) or ".." in path.parts:
        return None
    return path.as_posix()


def target_is_authorized(target: str, allowed_values: list[str]) -> bool:
    for raw_allowed in allowed_values:
        subtree = raw_allowed.endswith("/")
        allowed = relative_ledger_path(raw_allowed.rstrip("/") or ".")
        if allowed is None:
            continue
        if allowed == ".":
            return True
        if subtree and (target == allowed or target.startswith(f"{allowed}/")):
            return True
        if not subtree and target == allowed:
            return True
    return False


def require_list(document: dict[str, object], key: str, errors: list[str]) -> list[object]:
    value = document.get(key)
    if not isinstance(value, list):
        errors.append(f"{key} must be a list")
        return []
    return value


def unique_id(item: object, collection: str, seen: set[str], errors: list[str]) -> str | None:
    if not isinstance(item, dict):
        errors.append(f"{collection} entries must be objects")
        return None
    identifier = item.get("id")
    if not non_empty_string(identifier):
        errors.append(f"{collection} entry is missing a non-empty id")
        return None
    identifier = str(identifier)
    if identifier in seen:
        errors.append(f"duplicate {collection} id: {identifier}")
        return None
    seen.add(identifier)
    return identifier


def validate_references(
    values: object, known: set[str], label: str, errors: list[str]
) -> None:
    if values is None:
        return
    if not isinstance(values, list) or not all(non_empty_string(value) for value in values):
        errors.append(f"{label} must be a list of non-empty ids")
        return
    for value in values:
        if value not in known:
            errors.append(f"{label} references unknown id: {value}")


def derive_gate(
    requested: bool,
    mismatch_items: list[dict[str, object]],
    verification_items: list[dict[str, object]],
) -> str:
    if not requested:
        return "not-assessed"

    open_failure = any(
        item.get("status") == "open"
        and (
            item.get("classification") == "source-conflict"
            or (
                item.get("gate_blocking") is True
                and item.get("classification") not in BLOCKED_MISMATCH_CLASSES
            )
        )
        for item in mismatch_items
    )
    open_blocker = any(
        item.get("status") == "open"
        and (
            item.get("classification") == "ambiguous-authority"
            or (
                item.get("gate_blocking") is True
                and item.get("classification") in BLOCKED_MISMATCH_CLASSES
            )
        )
        for item in mismatch_items
    )
    required = [item for item in verification_items if item.get("required") is True]
    failed = any(item.get("status") == "failed" for item in required)
    if open_failure or failed:
        return "fail"
    if open_blocker or not required or any(
        item.get("status") in {"blocked", "not-run", "unverified"} for item in required
    ):
        return "blocked"
    return "pass"


def validate(document: object) -> dict[str, object]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return {"valid": False, "errors": ["ledger root must be an object"]}

    if document.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    mode = document.get("mode")
    if mode not in MODES:
        errors.append(f"mode must be one of: {', '.join(sorted(MODES))}")

    scope = document.get("scope")
    authorized_write_paths: list[str] = []
    write_authorized = False
    if not isinstance(scope, dict):
        errors.append("scope must be an object")
    else:
        if relative_ledger_path(scope.get("root")) is None:
            errors.append("scope.root must be a relative path without parent traversal")
        repositories = scope.get("repositories")
        if not isinstance(repositories, list) or not repositories:
            errors.append("scope.repositories must be a non-empty list")
        elif any(relative_ledger_path(value) is None for value in repositories):
            errors.append("scope.repositories must contain only relative in-scope paths")
        write_authorized = scope.get("write_authorized") is True
        raw_write_paths = scope.get("authorized_write_paths")
        if not isinstance(raw_write_paths, list):
            errors.append("scope.authorized_write_paths must be a list")
        elif not all(non_empty_string(value) for value in raw_write_paths):
            errors.append("scope.authorized_write_paths must contain non-empty paths")
        else:
            authorized_write_paths = [str(value).replace("\\", "/") for value in raw_write_paths]
            if any(relative_ledger_path(value.rstrip("/") or ".") is None for value in authorized_write_paths):
                errors.append("authorized write paths must be relative and cannot traverse parents")

    source_values = require_list(document, "sources", errors)
    source_ids: set[str] = set()
    source_items: list[dict[str, object]] = []
    for item in source_values:
        identifier = unique_id(item, "source", source_ids, errors)
        if identifier is None or not isinstance(item, dict):
            continue
        source_items.append(item)
        if item.get("plane") not in PLANES:
            errors.append(f"source {identifier} has an invalid plane")
        if item.get("authority") not in AUTHORITIES:
            errors.append(f"source {identifier} has an invalid authority")
        for field in ("location", "status"):
            if not non_empty_string(item.get(field)):
                errors.append(f"source {identifier} requires {field}")

    mismatch_values = require_list(document, "mismatches", errors)
    mismatch_ids: set[str] = set()
    mismatch_items: list[dict[str, object]] = []
    for item in mismatch_values:
        identifier = unique_id(item, "mismatch", mismatch_ids, errors)
        if identifier is None or not isinstance(item, dict):
            continue
        mismatch_items.append(item)
        if item.get("classification") not in MISMATCH_CLASSES:
            errors.append(f"mismatch {identifier} has an invalid classification")
        if item.get("status") not in MISMATCH_STATUSES:
            errors.append(f"mismatch {identifier} has an invalid status")
        if not isinstance(item.get("gate_blocking"), bool):
            errors.append(f"mismatch {identifier} requires boolean gate_blocking")
        if not non_empty_string(item.get("summary")):
            errors.append(f"mismatch {identifier} requires summary")
        validate_references(item.get("source_ids"), source_ids, f"mismatch {identifier} source_ids", errors)

    action_values = require_list(document, "actions", errors)
    action_ids: set[str] = set()
    action_items: list[dict[str, object]] = []
    for item in action_values:
        identifier = unique_id(item, "action", action_ids, errors)
        if identifier is None or not isinstance(item, dict):
            continue
        action_items.append(item)
        status = item.get("status")
        if status not in ACTION_STATUSES:
            errors.append(f"action {identifier} has an invalid status")
        target = relative_ledger_path(item.get("target"))
        if target is None:
            errors.append(f"action {identifier} target must be a relative in-scope path")
        validate_references(
            item.get("mismatch_ids"), mismatch_ids, f"action {identifier} mismatch_ids", errors
        )
        if status == "applied" and target is not None:
            if mode not in {"reconcile", "post-deploy"}:
                errors.append(f"action {identifier} is applied in read-only mode {mode}")
            if not write_authorized:
                errors.append(f"action {identifier} is applied without explicit write authorization")
            if not target_is_authorized(target, authorized_write_paths):
                errors.append(f"action {identifier} target is outside authorized write paths: {target}")

    verification_values = require_list(document, "verifications", errors)
    verification_ids: set[str] = set()
    verification_items: list[dict[str, object]] = []
    for item in verification_values:
        identifier = unique_id(item, "verification", verification_ids, errors)
        if identifier is None or not isinstance(item, dict):
            continue
        verification_items.append(item)
        if not isinstance(item.get("required"), bool):
            errors.append(f"verification {identifier} requires boolean required")
        if item.get("status") not in VERIFICATION_STATUSES:
            errors.append(f"verification {identifier} has an invalid status")
        if not non_empty_string(item.get("scope")):
            errors.append(f"verification {identifier} requires scope")
        if not non_empty_string(item.get("evidence")):
            errors.append(f"verification {identifier} requires evidence or a blocking reason")
        validate_references(
            item.get("source_ids"), source_ids, f"verification {identifier} source_ids", errors
        )

    gate = document.get("gate")
    if gate is None:
        gate = {}
    if not isinstance(gate, dict):
        errors.append("gate must be an object when provided")
        gate = {}
    requested = mode == "gate" or gate.get("requested") is True
    if "requested" in gate and not isinstance(gate.get("requested"), bool):
        errors.append("gate.requested must be boolean")
    claimed = gate.get("decision", "not-assessed")
    if claimed not in GATE_DECISIONS:
        errors.append(f"gate.decision must be one of: {', '.join(sorted(GATE_DECISIONS))}")
    computed = derive_gate(requested, mismatch_items, verification_items)
    if claimed in GATE_DECISIONS and claimed != computed:
        errors.append(f"claimed gate decision {claimed} does not match evidence-derived {computed}")

    unresolved_conflicts = sorted(
        str(item["id"])
        for item in mismatch_items
        if item.get("status") == "open" and item.get("classification") in CONFLICT_CLASSES
    )
    unverified_items = sorted(
        str(item["id"])
        for item in verification_items
        if item.get("status") in {"blocked", "not-run", "unverified"}
    )

    return {
        "valid": not errors,
        "mode": mode,
        "counts": {
            "sources": len(source_items),
            "mismatches": len(mismatch_items),
            "actions": len(action_items),
            "applied_actions": sum(item.get("status") == "applied" for item in action_items),
            "verifications": len(verification_items),
        },
        "unresolved_conflicts": unresolved_conflicts,
        "unverified_items": unverified_items,
        "gate": {
            "requested": requested,
            "claimed": claimed,
            "computed": computed,
            "satisfied": (
                True
                if computed == "pass"
                else False if computed in {"fail", "blocked"} else None
            ),
        },
        "errors": errors,
    }


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a reconciliation JSON ledger and derive its gate result."
    )
    parser.add_argument("ledger", help="Path to the reconciliation ledger JSON file, or - for stdin.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON output.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.ledger == "-":
            document = json.load(sys.stdin)
        else:
            with open(args.ledger, encoding="utf-8") as handle:
                document = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        result = {"valid": False, "errors": [f"cannot read ledger: {error}"]}
        json.dump(result, sys.stdout, indent=None if args.compact else 2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 2

    result = validate(document)
    json.dump(result, sys.stdout, indent=None if args.compact else 2, ensure_ascii=False)
    sys.stdout.write("\n")
    if not result["valid"]:
        return 2
    if result["gate"]["computed"] in {"fail", "blocked"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
