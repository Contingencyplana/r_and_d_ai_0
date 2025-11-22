# Change Log

All notable updates to the High Command AI workspace are documented here. Entries reference corresponding orders and ledger notes.

## 2025-11-22

- Hybrid comms restore: refreshed exchange tooling under `tools/` (end_of_block, watcher/validator, emitter), removed redundant copies, retired the `exchange_all` smoke caveat in favor of `python tools/factory_order_emitter.py --help`, and reran the cadence/validator to keep Batch 1 readiness evidence aligned.

## 2025-10-12

- **Order 2025-10-12-001** - Issued first exchange directive; toysoldiers_ai_0 stood up receiver, produced ack/report, and order closed in ledger.
- **Order 2025-10-12-002** — Directed toysoldiers_ai_0 to align acknowledgement/report payloads with official schemas and implement expiry warnings.
- **Order 2025-10-12-003** — Mandated governance collateral (MIT license, Code of Conduct, Contributing guide) across toysoldiers_ai_0; exchange ledger updated after acknowledgement/report cycle.
- **Exchange Watcher v1** — Introduced `tools/exchange_watcher.py` with tests to surface new orders/acks/reports automatically; recommended for deployment in all field theatres.
- **Doctrine Glossary** — Added `planning/glossary.md` capturing shared acronyms, terminology, and tooling references for High Command and field theatres.
- **Toyfoundry Charter Q4 2025** — Expanded `planning/toyfoundry/toyfoundry.md` with mission scope, interfaces, guardrails, and upcoming orders to prepare manufacturing rollout.
