# Verification and Reporting

Treat evidence as a first-class state with provenance and limits. A plausible implementation or a test definition is not a passing result.

## Contents

- [Record evidence precisely](#record-evidence-precisely)
- [Decide gates conservatively](#decide-gates-conservatively)
- [Close post-deployment gaps](#close-post-deployment-gaps)
- [Use a structured reconciliation ledger](#use-a-structured-reconciliation-ledger)
- [Report the outcome](#report-the-outcome)

## Record evidence precisely

Use these statuses:

| Status | Meaning |
| --- | --- |
| `passed` | The named check ran for the relevant scope and produced trustworthy passing evidence. |
| `failed` | The named check ran and observed a material failure. |
| `blocked` | The check was attempted or required but could not run because a prerequisite or environment was unavailable. |
| `not-run` | The check was deliberately not attempted; state why. |
| `unverified` | No evidence establishes the claim, or existing evidence is stale, indirect, or insufficient. |

For every check, record its purpose, repository and revision, command or procedure, environment, observed result, and evidence location or concise output. Record time when freshness matters. Require non-empty observed evidence before using `passed`.

Discover commands and acceptance criteria from applicable repository guidance, automation, or owning artifacts. Do not invent a familiar test command when the repository does not declare one.

## Decide gates conservatively

Use the repository's own criteria and risk policy. In their absence, label the map provisional and do not claim a release-grade pass.

Return:

- `FAIL` when a required check fails or a known gate-blocking inconsistency remains open;
- `BLOCKED` when required authority, scope, environment, or evidence is unavailable;
- `PASS` only when all in-scope required checks have current passing evidence, all gate-blocking inconsistencies are resolved, and required post-deployment evidence is complete or explicitly deferred by repository policy;
- `NOT ASSESSED` when no gate was requested or defined.

A user request to “make the gate pass” does not authorize false evidence, relaxed criteria, or out-of-scope edits.

## Close post-deployment gaps

When local or isolated checks cannot prove real behavior, record:

- the local evidence already obtained and its limits;
- the exact deployment boundary still unverified;
- target environment, version, prerequisites, and authorization;
- steps, expected observations, failure signals, and evidence destination;
- containment or rollback guidance when users or data could be affected;
- status, owner, and follow-up cue when repository policy defines them.

Run the check only with required authorization. Never copy credentials, private endpoints, sensitive production data, or fabricated observations into a record. If deployed behavior conflicts with accepted intent or locally validated behavior, reopen reconciliation rather than editing the record to hide the difference.

## Use a structured reconciliation ledger

For complex or gated work, create a task-local JSON ledger and validate it with `scripts/validate_reconciliation.py`. Keep paths relative to one declared scope root.

```json
{
  "schema_version": 1,
  "mode": "gate",
  "scope": {
    "root": ".",
    "repositories": ["."],
    "write_authorized": false,
    "authorized_write_paths": []
  },
  "sources": [
    {
      "id": "requirement-account-view",
      "plane": "intended",
      "location": "docs/requirements.md",
      "authority": "declared",
      "status": "accepted"
    }
  ],
  "mismatches": [],
  "actions": [],
  "verifications": [
    {
      "id": "acceptance-account-view",
      "required": true,
      "status": "passed",
      "scope": "account-view behavior",
      "evidence": "Repository-declared acceptance command exited successfully for the recorded revision."
    }
  ],
  "gate": {
    "requested": true,
    "decision": "pass"
  }
}
```

Use these ledger rules:

- Set source `plane` to `intended`, `executable`, or `evidence`; mark authority `declared`, `provisional`, or `supporting`.
- Classify mismatches with the vocabulary in [state model and authority](state-model-and-authority.md). Set `status` to `open`, `resolved`, or `accepted-risk`, and set `gate_blocking` from repository policy and materiality. An open `source-conflict` always prevents `PASS`; open `ambiguous-authority` blocks a gate even when no source is safe to choose.
- Record applied, proposed, or skipped actions. An applied action must target an authorized relative path and must occur only in an explicitly writable `reconcile` or `post-deploy` task.
- Record every required verification even when it cannot run. Never omit a failed or blocked check to improve the gate result.
- Set the claimed gate decision to lowercase `pass`, `fail`, `blocked`, or `not-assessed`; the validator compares it with the evidence-derived result.

The ledger is an evidence index, not a replacement for repository-owned requirements, contracts, test output, or deployment records.

## Report the outcome

Use this compact order:

1. **Mode and scope:** repositories, change range, write boundary, and assumptions.
2. **Authority map:** intended, executable, and evidence owners by affected topic.
3. **Inconsistencies:** category, observation, affected consumers, materiality, and status.
4. **Corrections:** changed targets, authority for the change, and preserved out-of-scope work.
5. **Verification:** command or procedure, environment, result, and evidence.
6. **Open items:** unresolved conflicts, blocked checks, unverified behavior, post-deploy work, and owners when declared.
7. **Gate:** `PASS`, `FAIL`, `BLOCKED`, or `NOT ASSESSED`, with the decisive reasons.
