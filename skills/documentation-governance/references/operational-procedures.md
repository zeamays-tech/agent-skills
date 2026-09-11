# Operational Procedures

Apply this guidance to initialization, deployment, release, recovery, and acceptance procedures in runbooks and READMEs. Use repository-owned commands, locations, and success criteria; do not infer operational constraints from another project's examples.

## Show the execution order

Start a multi-stage deployment with an operation-order table. Use the same approach for other multi-stage procedures when readers need an overview to act in the correct order. Include:

| Order / stage | Prerequisite or entry condition | Execution location | Operation entry point | Completion signal | Next step |
| --- | --- | --- | --- | --- | --- |
| Stage identifier and purpose | Required prior state | Machine, environment, working directory, or UI as applicable | Exact section or automation link | Observable result that permits progress | Exact next stage, decision, or terminal state |

Treat the table as navigation into the owning procedure. Link to detailed steps or automation instead of repeating commands or maintaining an independent workflow. Keep stage identifiers, conditions, completion signals, and destinations consistent with the body when either changes.

Prefer Markdown tables for linear sequences and conditional decisions. Use a Mermaid flowchart when interdependent branches are clearer as a graph, and keep its destinations aligned with the owning steps. A simple single-step operation needs only short text; do not require a diagram for every explanation.

## Make each operation executable

- State prerequisites, execution location, operation or command, observable pass signal, and subsequent action for each step. A shared location or prerequisite may be declared once for a clearly bounded group; mark any change at the affected step.
- Label operations as required, conditional, or skippable. For conditional or skippable work, specify the triggering or skip condition and the destination when skipped. Put the condition immediately beside the command, outside the copyable command block, so copying a block does not silently include a conditional action.
- Split multiple actions into ordered steps. Split multiple conditions into a decision table or flowchart instead of embedding them in a long sentence.
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

Walk through the procedure from entry to completion and check:

- A multi-stage deployment starts with an order table containing location, entry point, completion signal, and next step; the table and body describe one consistent workflow.
- Each operation identifies prerequisites, location, pass signal, and continuation. Required, conditional, and skippable actions are distinguishable, with conditions adjacent to commands.
- Decisions cover normal, empty, unexpected, and failed results where applicable. Each branch reaches a named step, recovery action, or terminal state; no branch silently falls through to dependent work.
- Failures state whether to stop, repair and retry, or roll back, and identify the safe resume point. Disruptive recovery is separate from routine execution.
- Cross-document links resolve to the intended file and heading, with timing, completion signal, and return step specified.
- Steps and conditions are not hidden in long sentences. Tables or diagrams clarify multi-stage work without duplicating command ownership or burdening simple operations.

Check examples against their command contracts and inspect every branch on paper. Run repository-approved checks where authorized; a reader-flow review alone does not establish deployed behavior. Record remaining environment checks using [post-deployment verification](post-deployment-verification.md).
