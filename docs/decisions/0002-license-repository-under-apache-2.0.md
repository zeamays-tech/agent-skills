# License the Repository Under Apache-2.0

- Status: Accepted
- Date: 2026-07-15

## Context

The repository publishes reusable instructions, documentation, configuration, and potentially executable scripts. Consumers need permission to use, modify, redistribute, and incorporate this material across commercial and non-commercial agent environments under one predictable license.

The license also needs to support outside contributions and provide clear patent, attribution, trademark, warranty, and liability terms without splitting code and documentation into separate licensing regimes.

## Decision

License the repository under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Keep the complete canonical text in the root `LICENSE` file.

Apply Apache-2.0 to original repository content unless a file or third-party component explicitly states different terms. Do not add a `NOTICE` file unless attribution material requires one. Treat intentionally submitted contributions according to section 5 of Apache-2.0 unless a separate agreement or explicit contribution notice applies.

## Consequences

- Consumers may use, modify, and redistribute the repository under Apache-2.0's conditions.
- Contributors provide the license grants described by Apache-2.0, including its explicit patent grant and patent-litigation termination provision.
- Distributors must include the license, preserve applicable notices, and mark modified files as required by section 4.
- The license does not grant rights to project or contributor trademarks.
- Third-party material remains governed by its own license and attribution requirements.

## Alternatives considered

### MIT License

MIT is shorter and imposes fewer redistribution formalities, but its text does not provide the explicit patent-license terms included in Apache-2.0.

### Separate software and documentation licenses

Using a software license for scripts and a Creative Commons license for documentation could express content-specific terms, but it would make mixed Skill directories and downstream redistribution harder to interpret. A single Apache-2.0 license provides a clearer repository-wide default.
