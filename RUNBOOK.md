# r_and_d_ai_0 – Runbook (v1)

Purpose: run the Nightlands research backbone that prototypes the Five Major Pivots and supplies validated experiments to Toyfoundry, Toysoldiers, Valiant Citadel, and High Command.

Operating Principles
- Keep play (70%) and ops (30%) intertwined; every research sprint produces something testable plus the documentation to explain it.
- Treat each golf/delta theatre as a lab: new ideas incubate under `golf_##/delta_##/alfa_##/` with clear README + artifact log.
- Exchange artifacts only after pairing order → acknowledgement → report with evidence.

Research Loop (per session)
1. **Readiness Gate** – Run `python -m tools.ops_readiness`, confirm this RUNBOOK and charter docs exist, and repair staged metadata gaps immediately.
2. **Sync Orders** – Pull the latest directives from the exchange hub; mirror IDs into `planning/change_log.md` and `exchange/ledger/index.json`.
3. **Prototype** – Build/test inside the appropriate golf/delta/alfa folders; capture notes under `planning/` or `new_major_pivots/`.
4. **Document** – Update research READMEs plus any schema or emoji grammar drafts touched during the session.
5. **Report** – Stage acknowledgements/reports under `outbox/` referencing evidence paths; rerun readiness to confirm metadata completeness.
6. **Exchange** – Run `python tools/end_of_block.py` (heartbeat → offline sync → readiness → exchange) and verify `logs/exchange_all.json` updated.

Quality Gates
- All staged JSON files provide `created_at` (orders + reports) and `ack_timestamp` (acks).
- Emojiflow prototypes cite the glyph grammar version they implement.
- Nightlands safety alignment: major experiments mention how they respect Valiant Citadel kill-switch hooks.
- Ledger entries reference the golf/delta/alfa path plus supporting docs or attachments.

Evidence & Logging
- Readiness status: `logs/ops_readiness.json`
- Exchange pushes: `logs/exchange_all.json`
- Smoke check: `python tools/factory_order_emitter.py --help` (confirm CLI available; use as the default smoke)
- Research notes: `planning/`, `new_major_pivots/`
- Ledger + attachments: `exchange/ledger/`, `exchange/attachments/`

Escalation
- If readiness fails twice, pause prototyping; notify High Command and file a note in `planning/change_log.md`.
- For high-risk experiments (emoji compiler, Nightlands simulators), secure Valiant Citadel approval before running off-hours tests.

References
- `README.md`
- `new_major_pivots/`
- `planning/`
- `war_office.md`
- `exchange/README.md`
