---
name: evidence-driven-debugging
description: Diagnose software failures through scoped evidence, discriminating experiments, and complete-path regression checks. Use for ambiguous errors, repeated failed attempts, environment-dependent behavior, authentication or external-service failures, and disagreements between component success and final health or user outcomes. Scale down for simple reproducible defects; do not use as a general code review or project-state audit.
---

# Evidence-Driven Debugging

Reduce uncertainty before spending another user action or production change. Establish what failed, test an explanation, and verify the user's intended outcome within the evidence's actual limits.

## Scale to the failure

For a simple deterministic defect, use a short path: confirm the expected behavior, reproduce the failure with a test, make the smallest complete repair, and run the relevant regression checks. A separate ledger or experiment document is unnecessary.

Use the fuller workflow below when the failing boundary is unclear, attempts repeat, environments differ, or several components can overwrite the result. Keep notes in the task's existing evidence location or conversation; do not create a new reporting system by default.

## Establish the boundary and baseline

1. Read applicable repository instructions and the current change state. Identify the user's goal, accepted success criteria, authorized repositories and operations, and the first boundary where expected and observed behavior diverge. Separate an external source's response from transport, observation, parsing, persistence, aggregation, scheduling, and presentation failures.
2. Keep **facts**, **hypotheses**, and **unknowns** distinct. A UI message is an observation, not automatically a root cause. Distinguish an explicit business rejection from a source/access restriction and from an unreadable or absent response. Missing evidence remains unknown rather than success or a fabricated rejection.
3. Record the revision or artifact, relevant runtime and dependency versions, environment, configuration differences, session provenance when relevant, and observation time. Keep the baseline stable during each experiment; record unavoidable changes and their confounding effects. Use safe identifiers, not secret values.
4. Compare a known successful sample with a failing one before inventing fixes. Identify differences in input, environment, session lifecycle, timing, and code path. If no successful sample exists, say so and use the accepted contract plus the smallest available reproducer. Success on another host or with an older session does not establish success for a fresh session in the target environment.

## Choose the next informative experiment

Before each nontrivial attempt, state these items briefly:

| Item | Required decision |
| --- | --- |
| Hypothesis | One falsifiable explanation for the observed boundary failure |
| Main variable | What changes, what stays fixed, and any uncontrolled differences |
| Expected evidence | The observation that distinguishes this explanation from alternatives |
| Stop condition | A bounded time, event, attempt budget, or impact threshold appropriate to the task |
| Result branches | What to do if supported, contradicted, inconclusive, or unsafe |

Prefer the cheapest experiment that can separate plausible explanations. Complete relevant code review, offline reproduction, and diagnostic preparation before requesting another login, scan, restart, or deployment. Inspect available context yourself instead of asking the user to gather evidence you can obtain within authorization.

Capture the failing stage before repeating it: project only necessary metadata such as stage, safe correlation ID, status category, body availability, timing, navigation/frame context, and persistence outcome. Do not collect or retain raw cookies, tokens, browser profiles, response bodies, or private URLs as routine diagnostics. Use synthetic or redacted fixtures; where sensitive evidence is genuinely necessary, follow the task's access and retention rules without exposing it in reports.

A retry must have stated information value: changed instrumentation, a controlled variable, or a bounded sampling plan for an intermittent hypothesis. Do not treat repetition alone as progress. When the limit is reached or attempts stop distinguishing hypotheses, stop that experiment, summarize the evidence, and change the diagnostic approach. Inconclusive evidence calls for better observation, not a success label.

If human participation is indispensable, prepare the code, checks, evidence capture, and result branches first. Request the smallest concrete action, explain what it will distinguish, and say what ends the attempt. Reuse existing authorization; skill invocation grants no additional production, credential, deployment, or cross-repository access and imposes no redundant approval step. For an authorized disruptive experiment, identify containment or rollback before acting.

## Repair the complete result path

- Trace producers, callers, persistence, status reducers or aggregators, scheduling gates, and the final user-visible outcome. A successful leaf operation can still be overwritten downstream. Inspect those consumers before selecting the repair location.
- For each behavioral increment, add a regression test derived from the accepted contract or failure evidence, run it and confirm the relevant failure, then implement the smallest repair and rerun. Dependency or setup failures do not count as reproducing the defect. Use integration or end-to-end tests first when the behavior cannot be isolated meaningfully.
- Verify the connected path as well as the changed function. Cover allowed degraded or partial results, real failures, and unknown results according to the contract. A classification change must not invent a success timestamp, discard a real failure, or turn missing evidence into readiness.
- Keep fallback evidence narrowly correlated to the same operation, target, and lifecycle. For example, a response lost during navigation may justify inspecting a replacement only when the loss and relevant navigation are established and the replacement has the required frame, origin, and identity evidence. Nearby traffic alone proves nothing. A fallback must have a stop condition and preserve unknown outcomes.
- Fix what the evidence supports. A repair can be validated while the external service's internal reason remains unknown; describe that distinction instead of claiming an unobserved platform cause. Do not convert an environment-specific workaround into a universal runtime requirement.

## Verify and report within scope

Bind every conclusion to its revision, environment, evidence source, and observation window. Separate applicable acceptance boundaries: user confirmation, service-recognized identity, persisted session, reopen/restart behavior, target read, durable write, scheduler health, and final delivery. Mark each as passed, failed, blocked, or unverified with supporting evidence; omit boundaries irrelevant to the user's goal.

Use accepted criteria to decide which missing checks block the goal. No new event means delivery latency may remain unverified even if collection passed. A short successful observation window does not prove long-term stability; a memory snapshot does not prove peak capacity. Local tests do not establish deployed behavior.

Report the established failure and any remaining hypotheses, the repair and covered path, observed test failures and subsequent results, acceptance boundaries, remaining uncertainty, and the next informative action if needed. Distinguish fixture reasoning, executed tests, and real-environment checks. Do not report a planned check as executed.

## Compose without duplicating other skills

When available and applicable, use `reconcile-project-state` for alignment of accepted intent, implementation, and completion evidence; `documentation-governance` for document ownership and synchronization; and `ponytail` for the smallest complete implementation. This skill owns diagnostic hypotheses and experiment selection. If those skills are unavailable, follow repository rules and continue the scoped debugging workflow; no plugin or client-specific runtime is required.

## Invoke and integrate

Explicit invocation in compatible clients:

```text
Use $evidence-driven-debugging to investigate this failure within the authorized scope and verify the complete result path.
```

After installing the Skill, adapt this statement for a consumer's `AGENTS.md`:

```markdown
Use $evidence-driven-debugging for ambiguous failures, repeated unsuccessful
attempts, environment-dependent behavior, or component success that disagrees
with the final outcome. Establish facts and baseline, choose informative bounded
experiments, and prepare diagnostics before requesting user actions or deployment.
Reproduce behavioral defects before fixing them and verify the complete result
path. Keep conclusions scoped to observed evidence and existing authorization;
use the short workflow for simple reproducible defects.
```

Description-based discovery depends on the client; this statement is repository guidance, not an event listener or proof that the Skill is installed.
