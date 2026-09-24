# Operational Procedures

Apply this guidance to initialization, deployment, release, recovery, and acceptance procedures in runbooks and READMEs. Use repository-owned commands, locations, and success criteria; do not infer operational constraints from another project's examples.

## Separate purpose, actions, and rationale

When a purpose statement helps orient the reader, put it at the beginning of the section and limit it to one sentence describing the result after completion. Do not add a purpose paragraph to every simple operation.

Keep the operational body focused on prerequisites, execution location, concrete actions, expected results, and next steps. Explain technical rationale briefly beside an action only when it affects the operator's decision. Move other necessary implementation explanations to the corresponding design document or technical reference and link to the owning section, following [authority and synchronization](authority-and-sync.md). Reuse existing owners; do not create a document solely to relocate an unnecessary explanation or duplicate executable facts.

Keep risks, permissions, and limitations beside the affected action, with the triggering condition and required response. Preserve necessary safety boundaries when shortening or relocating explanations.

## Use short, repository-owned entry points

Keep only information needed to perform the operation: prerequisites, location and identity, required inputs, a short command, completion signal, and failure or recovery action. Remove agent-session narration, implementation progress, repeated boundaries, and explanations that do not change the operator's next action. Move necessary architecture or capability limits to their existing owner; retain actionable safety conditions beside the affected command.

Prefer an existing script or native command. Encapsulate repeated or multi-command automated work in a repository-owned script; expose one short invocation with its required arguments. The operator must not reconstruct internal commands, compare machine-readable values by eye, or search intermediate logs for an outcome. Validate paths, target identity, revisions, digests, configuration and other machine-checkable prerequisites before mutation. Keep secrets out of arguments and summaries when they could be exposed.

Make copyable command blocks self-contained: establish and validate the working directory or use a script entry point that resolves its own repository. Do not depend on a previous block changing directories. Multi-command or state-changing shell blocks must stop on failure, using a subshell where appropriate. A runbook may establish non-secret inputs once; each consuming script must validate them and reject placeholders or ambiguous targets before mutation.

Keep genuinely manual work explicit: entering console settings, authenticating, approving destructive actions, or confirming a real-world result. Do not automate a human decision or claim it passed because its preceding script succeeded. A simple native command or a test runner with an adequate final summary needs no wrapper solely for formatting. Long-running services and interactive sessions need readiness and exit instructions, not a premature completion marker.

## End automated operations with one scoped result

Every operator-facing automated operation or check must end with a compact result after all required work, assertions, and cleanup. Use this convention for repository-owned entry points unless an existing native tool already provides an equally unambiguous terminal summary:

```text
RESULT: PASS | checked scope
RESULT: FAIL | checked scope | safe failure summary; recovery entry
```

Print only the applicable final line. Put essential outputs (artifact paths, verified digests, counts, or next entry) together immediately before it. Emit PASS only after all required assertions and cleanup succeed, with exit status zero. Missing evidence, parse errors, command failure, or cleanup failure must produce a nonzero exit status and a best-effort FAIL summary; handle interruption where possible. Absence of a final result is never acceptance. An outer workflow owns its final result; successful substeps do not establish overall success.

Report the scope actually checked: a configuration check does not establish deployment health, and file delivery does not establish authentication. Label status, logs, and lists as information queries rather than acceptance. Preserve upstream errors through pipes and composite commands; never append an unconditional success marker. Keep diagnostics bounded and relevant, and do not require readers to find the important result earlier in the output.

When changing executable behavior, use the repository's testing rules and test observable success, failure, and cleanup outcomes. Verify output order and exit status with isolated inputs; never run a production operation merely to review its manual.

## Show the execution order

Start a multi-stage deployment with an operation-order table. Use the same approach for other multi-stage procedures when readers need an overview to act in the correct order. Include:

| Order / stage | Prerequisite or entry condition | Execution location | Operation entry point | Completion signal | Next step |
| --- | --- | --- | --- | --- | --- |
| Stage identifier and purpose | Required prior state | Machine, environment, working directory, or UI as applicable | Exact section or automation link | Observable result that permits progress | Exact next stage, decision, or terminal state |

Treat the table as navigation into the owning procedure. Link to detailed steps or automation instead of repeating commands or maintaining an independent workflow. Keep stage identifiers, conditions, completion signals, and destinations consistent with the body when either changes.

Prefer Markdown tables for linear sequences and conditional decisions. Use a Mermaid flowchart when interdependent branches are clearer as a graph, and keep its destinations aligned with the owning steps. A simple single-step operation needs only short text; do not require a diagram for every explanation.

## Make each operation executable

- State prerequisites, execution location, operation or command, observable pass signal, and subsequent action for each step. A shared location or prerequisite may be declared once for a clearly bounded group; mark any change at the affected step.
- Distinguish required actions, conditional or skippable actions, settings that need no modification, and verification. For unchanged settings, say what to retain and where to continue; retaining a setting does not waive a required check. For conditional or skippable work, specify the triggering or skip condition and the destination when skipped. Put the condition immediately beside the command, outside the copyable command block, so copying a block does not silently include a conditional action.
- Split multiple actions into ordered steps and multiple conditions into a decision table or flowchart. When a paragraph mixes implementation rationale, multiple actions, and conditional branches, separate the rationale and expose the actions and decisions in that structure. Definitions of technical terms do not substitute for instructions to act, retain, skip, or verify.
- Give setup and configuration steps a validation signal and an explicit continuation. State the terminal outcome when no further action is required.

## Cover outcomes and recovery

For a command or check with conditional outcomes, use a decision table or flowchart. Cover normal output, no matches or empty output, unexpected output, and command failure. If an outcome cannot occur for that operation, establish this from its contract rather than inventing a branch. Do not assume empty output means success or that an exit code alone distinguishes every outcome.

Use this decision-table shape, replacing the descriptions with the actual command's signals and destinations:

| Observed result | Interpretation | Required action | Resume or next step |
| --- | --- | --- | --- |
| Expected output and successful status | Step passed | Continue | Exact next step or completion state |
| No matches or empty output | Expected absence or missing prerequisite, according to the command contract | Skip only if absence satisfies the prerequisite; otherwise stop and repair | Exact skip destination or step to recheck after repair |
| Unexpected output | State is not established | Stop and diagnose before making dependent changes | Exact check to rerun once the state is understood and repaired |
| Failed command or failed acceptance signal | Step failed; partial changes may remain | Stop; follow the applicable repair-and-retry or rollback procedure | Exact recovery entry and safe resume checkpoint |

For each actual failure branch, name the applicable response: stop, repair then retry, or roll back. Identify the repair or rollback entry, its completion signal, and the step from which execution resumes. State when partial changes make a direct retry unsafe; do not direct readers to rerun the whole procedure without establishing that it is safe.

Separate routine operations from recovery actions such as a rebuild that interrupts service. Label the impact and entry conditions at the recovery command, include any required operational prerequisites, and link back to a verified resume point. Do not place disruptive recovery commands in an unconditional normal-path command block.

## Make document handoffs explicit

Link to the exact file and section heading for every cross-document operation. State when to leave the current procedure, what completion signal to obtain there, and the exact step to return to afterward. If the destination completes the workflow, say so instead of implying a return.

Use descriptive links containing the destination document and section names. Replace bare references such as "the same section," "follow the above," or "see the deployment guide" when they require the reader to infer a destination or operation. Verify relative paths and heading anchors from the document containing the link. Keep commands in their owning document, following [authority and synchronization](authority-and-sync.md#avoid-duplicated-executable-contracts).

## Validate the reader flow

Before delivery, walk through the procedure step by step as its intended operator, from entry to completion. Without needing to understand internal implementation, the reader must be able to determine what to do now, when to skip, where to go after success, and how to respond to failure. Check:

- Automated workflows use short repository-owned entry points and end in a scoped result after cleanup. Essential outputs are grouped at the end; no step requires searching intermediate logs or manually comparing machine-readable evidence. Information queries, long-running sessions, and human decisions are identified accurately.
- Any purpose statement opens its section, describes the completed result in at most one sentence, and does not burden simple operations. Rationale retained beside actions affects a decision; other necessary technical explanations link to their design or reference owner.
- A multi-stage deployment starts with an order table containing location, entry point, completion signal, and next step; the table and body describe one consistent workflow.
- Each operation identifies prerequisites, location, concrete action, pass signal, and continuation. Required actions, conditional or skippable actions, unchanged settings, and verification are distinguishable, with conditions adjacent to commands.
- Risks, permissions, and limitations remain beside affected actions, with trigger conditions and handling instructions; moving rationale has not removed necessary safety boundaries.
- Decisions cover normal, empty, unexpected, and failed results where applicable. Each branch reaches a named step, recovery action, or terminal state; no branch silently falls through to dependent work.
- Failures state whether to stop, repair and retry, or roll back, and identify the safe resume point. Disruptive recovery is separate from routine execution.
- Cross-document links resolve to the intended file and heading, with timing, completion signal, and return step specified.
- Steps and conditions are not hidden among implementation explanations or replaced by terminology. Tables or diagrams clarify multi-stage work without duplicating command ownership or burdening simple operations.

Repair missing actions, ambiguous destinations, unstated prerequisites, and verification results without a next step before delivery. Check examples against their command contracts and inspect every branch on paper. Run repository-approved checks where authorized; a reader-flow review alone does not establish deployed behavior. Record remaining environment checks using [post-deployment verification](post-deployment-verification.md).
