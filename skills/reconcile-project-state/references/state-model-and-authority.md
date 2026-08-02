# State Model and Authority

Model delivery state as three connected planes. Use the model to organize evidence, not to impose a repository layout.

## Classify the planes

### Intended state

Use accepted requirements, active designs, accepted decision records, current operating or governance guidance, and explicit acceptance criteria to establish what should be true. Record draft, proposed, rejected, superseded, and accepted status exactly as the repository defines it. An unaccepted draft may inform impact analysis but does not override accepted intent.

An ADR normally owns why a decision was accepted. It is not automatically the current user or operator guide. Apply the repository's document map and load `documentation-governance` before changing documentation.

### Executable state

Use the artifact that actually controls the topic: implementation, interface or data schema, configuration, migration, generated specification, policy-as-code, build definition, deployment definition, or another repository-declared executable source. Do not assume one artifact type is authoritative for every topic.

Executable artifacts show what may run; they do not prove that a path was built, deployed, or exercised successfully.

### Evidence state

Use test and build results, acceptance records, generated comparisons, runtime observations, deployment records, and post-deployment checks. Judge evidence by provenance, scope, environment, version or revision, time, and result. A test definition without an observed run is executable intent for verification, not passed evidence.

## Build a topic-specific authority map

Prefer a repository-declared workspace manifest, ownership map, document map, or governance file. Otherwise create a provisional map and mark it as inferred.

For each affected topic, record:

| Field | Meaning |
| --- | --- |
| Topic or contract | The behavior or boundary being reconciled |
| Intended owner | Accepted requirement, design, decision, or current guidance |
| Executable authority | Artifact that controls actual behavior for this topic |
| Evidence owner | Check or record capable of verifying the behavior |
| Human or team owner | Only when declared by the repository |
| Consumers | Components, repositories, docs, examples, or operators affected |
| Confidence | Declared or provisional, with the supporting evidence |

Do not copy this table's artifact examples into project policy. Populate it from the target project's own rules and content.

## Maintain directional traceability

Trace each material behavior in one direction:

`requirement -> design decision -> implementation or executable authority -> verification evidence`

Use stable repository identifiers or relative links when available. For each link, summarize only the relationship, covered behavior, and relevant version or scope. Link to complete schemas, option lists, defaults, and procedures at their owner rather than copying them.

A missing design record is not automatically a defect: repositories may deliberately connect a small requirement directly to executable authority. Report a missing link only when repository policy or the risk of the change requires it.

## Resolve authority without erasing disagreement

Apply this order:

1. Follow explicit repository governance, status, and ownership rules.
2. Confirm that each source is current and applies to the same topic, version, and environment.
3. Distinguish normative intent from observed actual behavior.
4. Use validated evidence to describe actual behavior, not to rewrite accepted intent silently.
5. Escalate same-topic authoritative conflicts or accepted-intent versus validated-actual conflicts for a decision.
6. Record the selected authority and rationale only after that decision is available.

Never infer that code wins because it runs, that a requirement wins because it is prose, or that a passing test proves behavior beyond the test's scope.

## Classify inconsistencies

Use the smallest accurate category:

- `source-conflict`: authoritative sources make incompatible claims about the same scope.
- `missing-link`: a required directional trace link is absent or cannot be defended.
- `stale-intent`: current-state intent still describes a retired or replaced behavior.
- `executable-drift`: executable authority differs from confirmed accepted intent.
- `incomplete-implementation`: only part of the intended behavior or consumer set is implemented.
- `insufficient-evidence`: required evidence is missing, stale, too narrow, or from the wrong environment.
- `environment-divergence`: deployed or integration behavior differs from locally validated behavior.
- `ambiguous-authority`: no defensible owner or status can be established.
- `out-of-scope`: a needed repair lies outside the authorized write or repository boundary.

Keep observed facts, interpretations, and assumptions separate in notes and reports.
