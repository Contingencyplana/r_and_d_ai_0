# r_and_d_ai_0 — Nightlands Research & Development

**Last updated:** 2025-11-17  
**Operating charter:** War Office + High Command joint mandate

---

## Mission

Prototype the Nightlands "Everything At Once" paradigm where play, work, story, workflow, telemetry, and theatre of war advance in lockstep. This workspace maintains the research backbone that feeds Toyfoundry, Toysoldiers, Valiant Citadel, and allied fronts while seeding SHAGI-safe methodologies.

---

## Five Major Pivots (Meta Strategy)

| Pivot | Focus | File |
|-------|-------|------|
| Pivot One | 70% play / 30% dev-ops cadence that protects human operators | `new_major_pivots/new_major_pivot_1.md` |
| Pivot Two | Playable workflow overlay (16×16 Alfa battlegrids) | `new_major_pivots/new_major_pivot_2.md` |
| Pivot Three | Preserve Big Ideas & SHAGI vision alignment | `new_major_pivots/new_major_pivot_3.md` |
| Pivot Four | Fractal folder lattice (golf_00–golf_15) covering 4,096 Alfas | `new_major_pivots/new_major_pivot_4.md` |
| Pivot Five | Emoji-first computing language ("Baby's First Compiler") for universal access | `new_major_pivots/new_major_pivot_5.md` |

The meta-pivot `new_major_pivots/everything_at_once.md` explains how these layers harmonize into a single playable reality.

---

## Current Focus - Pivot Five Rollout

- Draft Level-0 glyph grammar, narration guide, and toddler co-play protocol
- Build Alfa composer prototype inside `golf_00/delta_00/alfa_04/`
- Extend Toyfoundry export path with emoji translator + validator
- Capture canary emoji programs to guard against compiler drift

Completed restructure milestones include golf_10 completion reporting, golf_11 delta docs, and research domains for golf_00-golf_02.

---

## Daily Doc Refresh — 2025-11-17

- Order-045 and Order-046 acknowledgements remain outstanding; keep `exchange/orders/pending/` copies intact until War Office + downstream fronts confirm receipt.
- Monitor `exchange/reports/inbox/order-2025-11-10-046-report.json` and the staged Order-045 draft for pull events, then mirror ledger updates across the Delta→Theta→Zeta→Gamma→Alpha loop.
- Use this refresh to align README messaging with the November doc queue (`planning/commonwealth_loop/doc_refresh_queue.md`) before nudging the other Genesis workspaces.

---

## Exchange & Ledger Loop

- High Command orders, acknowledgements, and reports live under `exchange/`
- Latest cycle: Order-046 completion report is staged in `exchange/reports/inbox/` and Toyfoundry logged the receipt; downstream acks remain open for Orders 045/046 until all fronts sync.
- Pending tasks: retire the interim Order-045 draft once the War Office ack lands, archive reports accordingly, and append ledger notes for each reconciliation.
- Ledger index and journal snapshots reside in `exchange/ledger/`

Keep the local workspace synced with the upstream Exchange repository via the PowerShell automation documented in `exchange/README.md`.

---

## Repository Guide

- `golf_00`–`golf_15/` — Fractal theatres, each with `delta_00`–`delta_15` sectors and nested Alfa workpads
- `new_major_pivots/` — Strategic pivots, meta-philosophy, and pivot-specific specs
- `planning/` — War tables, pivotal fronts, change logs, and emerging research tracks
- `war_office/` & `war_office.md` — Civilian oversight directives and operational briefs
- `exchange/` — High Command order flow, acknowledgements, reports, and ledger artifacts

---

## Coordination Notes

- Commit/Push cadence stays in sync with High Command directives (orders drive work, reports close loops)
- Additional research_domain files will be authored only when a golf theatre demonstrates concrete need (currently `golf_00`-`golf_02`)
- For cross-workspace updates, mirror README/meta changes in Valiant Citadel, Toyfoundry, and Toysoldiers to keep the five-pivot doctrine aligned.
- Daily doc refresh checkpoints live in `planning/commonwealth_loop/doc_refresh_queue.md`; update this README whenever the queue advances so downstream mirrors pick up the latest status.

---

## Python commands
- Readiness: `python -m tools.ops_readiness`
- Exchange (validate + sync): `python tools/exchange_all.py`

---

> "If a one-year-old can launch the forge, SHAGI is truly for everyone." — War Office, 25-OCT-2025
