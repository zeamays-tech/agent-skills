# Messaging Architecture

The service publishes accepted orders to the Stream Bus. Workers consume each order and persist the processing result.

The service previously used the Polling Relay. That design was retired after the team compared both approaches, and the earlier prototype was removed during the 2025 migration.
