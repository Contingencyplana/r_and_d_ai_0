"""Run a minimal ORDER-042 demo dispatch and log telemetry.

This script dispatches a single curated Alfa Zero cell through the
emoji translator bridge and appends a minimal telemetry JSONL record
under `telemetry/emoji_runtime/demo_runs/`.

Usage:
  python golf_00/delta_00/alfa_00/run_order_042_demo.py \
      --cell 0,4 \
      --telemetry telemetry/emoji_runtime/demo_runs

If no arguments are provided, it defaults to cell 0,4 and writes to
`telemetry/emoji_runtime/demo_runs/ORDER-042-<timestamp>.jsonl`.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from overlay_bridge import CELL_MAPPINGS, build_bridge, cell_label

Cell = Tuple[int, int]


def parse_cell(token: str) -> Cell:
    cleaned = token.replace(",", " ").strip().upper()
    parts = [p for p in cleaned.split() if p]
    if len(parts) == 2:
        row_t, col_t = parts
    elif len(parts) == 1 and len(parts[0]) == 2:
        row_t, col_t = parts[0][0], parts[0][1]
    else:
        raise argparse.ArgumentTypeError("Cell must be ROW,COL or ROWCOL using hex 0-F")
    try:
        row = int(row_t, 16)
        col = int(col_t, 16)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Row and column must be hexadecimal digits (0-F)") from exc
    if not (0 <= row <= 15 and 0 <= col <= 15):
        raise argparse.ArgumentTypeError("Row and column must be within 0-F")
    return row, col


def main() -> None:
    parser = argparse.ArgumentParser(description="ORDER-042 demo runner (single dispatch + telemetry)")
    parser.add_argument("--cell", default="0,4", help="Cell to dispatch (e.g. 0,4 or 04)")
    parser.add_argument(
        "--telemetry",
        default="telemetry/emoji_runtime/demo_runs",
        help="Directory to write telemetry JSONL (file is auto-named)",
    )
    parser.add_argument(
        "--outbox",
        default=None,
        help="Optional override for emoji-runtime outbox location",
    )
    args = parser.parse_args()

    cell = parse_cell(args.cell)
    bridge = build_bridge(args.outbox)

    # Dispatch
    destination = bridge.dispatch_cell(cell)

    # Summarize payload for telemetry record
    try:
        payload = json.loads(destination.read_text(encoding="utf-8"))
    except Exception:
        payload = {}

    chain_name, _desc = CELL_MAPPINGS[cell]
    glyphs = payload.get("glyph_chain")
    if isinstance(glyphs, list) and glyphs:
        first_glyph = str(glyphs[0])
    else:
        first_glyph = None

    # Telemetry record (minimal schema for demo)
    session_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {
        "session_id": f"ORDER-042-{session_ts}",
        "chain_id": chain_name,
        "frame_ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "glyph": first_glyph,
        "narration_text": payload.get("summary"),
        "sync_state": "green",
        "notes": "demo_smoke_run",
        "payload_path": str(destination),
    }

    # Write JSONL
    telemetry_dir = Path(args.telemetry)
    telemetry_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = telemetry_dir / f"ORDER-042-{session_ts}.jsonl"
    with telemetry_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False))
        handle.write("\n")

    # Operator feedback
    try:
        rel_payload = destination.relative_to(bridge.repo_root)
    except ValueError:
        rel_payload = destination
    try:
        rel_telemetry = telemetry_path.relative_to(bridge.repo_root)
    except ValueError:
        rel_telemetry = telemetry_path

    print("? ORDER-042 demo dispatch complete")
    print(f"  - Cell: {cell_label(cell)} -> {chain_name}")
    print(f"  - Payload: {rel_payload}")
    print(f"  - Telemetry: {rel_telemetry}")


if __name__ == "__main__":
    main()

