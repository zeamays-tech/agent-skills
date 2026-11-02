# Debugging behavior scenarios

These synthetic inputs support qualitative forward evaluation of the Skill. They are not production observations or executable regression tests. Give an evaluator the Skill and these inputs without an answer key. Ask for the next action, experiment branches, test order, and claims justified by the supplied evidence. Do not access external services or change repositories while evaluating.

## A. Repeated confirmation, different observations

The user wants a fresh session to read a target record. They have confirmed sign-in repeatedly and ask whether another attempt would help. Revision R1 and the target runtime are unchanged. Attempt A returned a readable `reauth_required` result. Attempt B showed an access-restriction page. Attempt C recorded an unavailable response body after a top-level navigation; a later child-frame event says `signed_in`. An older local session reads successfully. No target identity probe or reopen check exists. The agent can inspect code and synthetic traces offline. There is no authorization for deployment or access to secret values.

## B. Writes succeed, final health fails

Accepted behavior permits a first-page `partial_list` result to count as healthy collection when a durable write is confirmed. The worker calls `collect -> classify -> aggregate -> publish_health`. A trace shows a write succeeded for two synthetic targets, followed by unhealthy status. `classify` currently accepts only `complete`; `aggregate` converts every non-`complete` result into failure. Existing tests exercise only `classify(complete)`. A mixed result may contain a real failure; some partial results lack write evidence or a timestamp. The user authorizes a local fix and tests, but no deployment.

## C. Bounded observation

Revision R2 ran in a named target environment with a fresh session. Service identity and persistence after reopen were observed. Target reads and durable writes passed on initial and later scheduled runs. No new eligible record appeared during the short observation window. No restart was observed, and one memory sample was low. The user asks whether collection, delivery latency, and long-term stability are all proven, and whether a visible browser must now be mandatory on every host. An older session on a different host also works; no controlled comparison of browser modes exists.

## D. Small local defect

A local formatter must display zero as `0`; it currently displays an empty string because it tests value truthiness. A pure unit-test harness exists, the caller passes numeric values, and the user authorizes the fix. There are no external services or environment differences. Explain the smallest complete workflow without making file changes.
