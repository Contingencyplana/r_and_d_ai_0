# Contributing to High Command Exchange

The exchange repository acts as the shared message bus between High Command and field workspaces. To preserve auditability:

1. **Sync Often** — Always pull before pushing to avoid rewrites of orders, acknowledgements, or reports.
2. **One Order per Commit** — Introduce orders, acknowledgements, and reports with focused commits (reference order IDs).
3. **Validate Payloads** — Run `python tools/schema_validator.py <payload>` from the main workspace before committing.
4. **No Force Pushes** — The ledger is authoritative; never rewrite history.
5. **Keep the Inbox Clean** — After reviewing reports/acks, move them to the archived/logged directories and update the ledger indices.

This repository inherits the MIT License from the main workspace.
