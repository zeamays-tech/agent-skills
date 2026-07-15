# Service Architecture

The API gateway authenticates requests and sends accepted jobs to the worker queue. Workers process jobs idempotently and store results in object storage. The status API reads the stored result for authorized callers.
