# Discovery and Reconciliation

Discover project policy before comparing artifacts. Keep the investigation proportional to the mode and the materiality of the change.

## Discover boundaries and rules

1. Locate the workspace and every explicitly in-scope repository without assuming they share one Git root.
2. Read every applicable `AGENTS.md` from the workspace or repository root down to each affected artifact.
3. Look for repository-declared workspace manifests, ownership maps, source maps, status vocabularies, version policies, acceptance commands, deployment guidance, and generated-source notices.
4. Inspect Git status separately in every repository, including staged, unstaged, untracked, renamed, and deleted paths.
5. Identify pre-existing changes and keep them outside the repair set unless the user includes them.
6. If no manifest or source map exists, infer a provisional map from imports, build or deployment definitions, schema consumers, links, and repository layout. Label the evidence and uncertainty.

Use `scripts/collect_project_state.py` when deterministic Git inventory is useful. Its nested discovery is opt-in so a semantic trigger cannot silently widen scope.

## Build an impact ledger

For each changed or disputed topic, record:

- source artifact and owning plane;
- accepted or operational status;
- directly affected requirements, decisions, executable contracts, and checks;
- producers and consumers across component or repository boundaries;
- synchronization targets and generated artifacts;
- repository-declared validation commands and required environment;
- unresolved authority or scope assumptions.

Follow explicit identifiers and links first. Then use executable references, schema imports, configuration consumers, test coverage, and deployment wiring. Do not claim exhaustive impact from filenames or keyword matches alone.

## Audit by topic

For each trace chain:

1. Confirm that intended sources are accepted and current for the same scope.
2. Confirm that design decisions cover material boundaries and point to executable owners where repository policy requires it.
3. Compare executable producers and consumers rather than only adjacent prose.
4. Confirm migrations, compatibility behavior, configuration, and deployment definitions when the contract crosses versions or environments.
5. Match verification evidence to the exact requirement, revision, environment, and consumer set.
6. Classify each gap and state the observation that supports it.

Search outward only while the trace produces a material dependency. A small local change does not justify an unconditional repository-wide scan.

## Reconcile in authority order

Before editing, confirm explicit write authorization and re-read status to detect concurrent or pre-existing work.

Then:

1. Resolve authoritative conflicts through an existing user or repository decision. Stop on unresolved accepted-intent versus validated-actual disagreement.
2. Update the owning artifact rather than a downstream copy.
3. Update direct executable producers and consumers inside scope.
4. Add or update verification that demonstrates the accepted behavior at the affected boundaries.
5. Synchronize current guidance, generated references, examples, migrations, and acceptance records inside scope. Load `documentation-governance` for documentation changes.
6. Preserve accepted or repository-required decision history in the repository's historical layer instead of rewriting it as though it never happened.
7. Re-run affected validation from each owning repository and inspect the final diff for unrelated changes.

Do not create a cross-language auto-rewriter or mechanically normalize contracts based on one selected file. Semantic reconciliation requires confirmed authority and consumer-aware changes.

## Remove confirmed unaccepted work cleanly

Apply this boundary only in `reconcile` mode when the user or repository authority confirms that the work was never accepted, released, or deployed and explicitly requests its removal. Treat the work as an error in the current change set, not as decision history.

- Remove in-scope code, documentation, configuration, schemas, migrations, tests, fixtures, examples, comments, and other artifacts whose only authority or purpose came from that work.
- Do not replace them with a rejection explanation, tombstone, ADR, changelog entry, or test whose only assertion is that the work is absent. Keep such a test only when absence is itself an accepted security, compatibility, compliance, or operational contract.
- Retain artifacts that have an independent accepted purpose, rewriting them to remove the rejected assumption.
- Search for names, identifiers, synonyms, and derived concepts after removal; report any residual and its independent authority.

Do not rewrite Git history. If the work may have been accepted, released, deployed, persisted, exposed through an external contract, or relied on for compatibility or safety, stop clean removal and determine the required retirement or migration path.

## Coordinate multiple repositories

Maintain one row per repository containing its root, branch or revision, applicable rules, existing changes, authoritative artifacts, authorized writes, and validation commands.

Trace integration in dependency order:

1. identify the contract owner and its accepted version or compatibility window;
2. identify every in-scope producer and consumer;
3. distinguish coordinated source changes from published or deployed dependencies;
4. validate each repository locally with its own declared commands;
5. validate the integration boundary in the environment that can exercise it;
6. report repositories or environments that remain outside scope.

Do not treat a clean repository as proof that its installed dependency, deployed service, or generated contract matches another repository's working tree.

## Handle common stop conditions

Stop mutation and report when:

- authoritative sources conflict and no decision identifies the intended outcome;
- the required repository or artifact is outside the explicit write scope;
- a required generated file has an unknown or unavailable generator;
- validation would require undeclared credentials, production access, destructive data changes, or an unauthorized external side effect;
- current user changes overlap the proposed repair and cannot be preserved safely.

Continue read-only discovery where safe so the handoff names the exact decision, owner, scope, or environment needed.
