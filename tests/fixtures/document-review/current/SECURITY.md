# Security Boundaries

Administrative endpoints must not accept unauthenticated requests. The service refuses to start when its signing key is missing, preventing it from issuing unverifiable tokens.
