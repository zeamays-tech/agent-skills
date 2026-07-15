# Version 3 Configuration Migration

Version 2 accepted `timeout_seconds` as a quoted string. Version 3 requires an integer.

Before enabling version 3, convert the value to an integer, validate the configuration, and retain the previous file until rollback is no longer required.
