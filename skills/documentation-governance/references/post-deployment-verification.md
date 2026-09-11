# Post-Deployment Verification

Record the checks that cannot be completed faithfully in the local or isolated environment.

## Trigger the workflow

Use a repository-designated verification record when confidence depends on:

- A trusted certificate, public domain, CDN, edge, firewall, or production gateway.
- Third-party callbacks, webhooks, identity providers, platform signatures, or vendor permissions.
- Device, operating-system, browser, native application, or hardware capabilities.
- Deployed credentials, quotas, network policy, production data shape, or managed-service behavior.
- Load, failover, observability, or rollout controls unavailable in the test environment.

Do not claim full verification from a mock or local substitute when the untested boundary is material.

## Record an actionable check

Use [operational procedures](operational-procedures.md) to structure the check's sequence, branches, recovery, and handoffs.

State:

- What was verified locally and the evidence produced.
- Which boundary remains unverified and why the local result is insufficient.
- The target environment and prerequisites.
- Exact steps, expected observations, and failure signals.
- Rollback or containment action when the check can affect users or data.
- Owner, status, and follow-up cue when repository policy provides them.

Keep active checks in the current verification or runbook document. Move completed rollout narrative and obsolete environment detail to a release, migration, or incident record according to repository policy.

## Close the loop

After deployment:

1. Run the documented checks in the authorized environment.
2. Attach durable evidence or link to the owning system when permitted.
3. Record the result, environment, version, and time.
4. Update current guidance if deployed behavior differs from the documented state.
5. Escalate conflicts among deployment state, implementation, tests, and documentation.

Never copy secrets, access tokens, private endpoints, or sensitive production data into a verification record.
