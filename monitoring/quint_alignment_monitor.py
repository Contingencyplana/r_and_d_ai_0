#!/usr/bin/env python3
"""Quint alignment monitor for schema drift and narration parity.

This hook scans exchange report payloads for the factory-order@1.0 contract,
verifies required fields, and compares the narrated summary against the
shared narration brief.  Results are appended to
monitoring/logs/quint_alignment_report.jsonl so High Command can spot
schema drift or VO discrepancies quickly.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIRECTORIES = [
    BASE_DIR / "exchange" / "reports" / "archived",
    BASE_DIR / "exchange" / "reports" / "inbox",
]
LOG_PATH = BASE_DIR / "monitoring" / "logs" / "quint_alignment_report.jsonl"
EXPECTED_SCHEMA = "factory-order@1.0"
LEVEL0_GLYPH_CAP = 7
RE_REQUIRED_INTENT_KEYS: Tuple[str, ...] = (
    "actor",
    "action",
    "target",
    "outcome",
)
REQUIRED_TELEMETRY_KEYS: Tuple[str, ...] = (
    "batch_id",
    "ritual",
    "units_processed",
    "status",
    "duration_ms",
)


def _load_reference_stub() -> str:
    stub_file = BASE_DIR / "quint_synced" / "narration_alignment.md"
    pattern = re.compile(r'^-\s*Stub captured.*?"(.+?)"', re.MULTILINE)
    text = stub_file.read_text(encoding="utf-8")
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _iter_report_files() -> Iterable[Path]:
    for directory in REPORT_DIRECTORIES:
        if not directory.exists():
            continue
        for candidate in sorted(directory.glob("*.json")):
            yield candidate


def _validate_payload(payload: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Return schema status and list of notes."""
    notes: List[str] = []
    schema = payload.get("schema")
    if schema is None:
        return "missing", notes
    if schema != EXPECTED_SCHEMA:
        notes.append(f"unexpected schema: {schema}")
        return "drift", notes

    intent = payload.get("intent", {})
    telemetry = payload.get("telemetry_stub", {})
    missing_intent = [key for key in RE_REQUIRED_INTENT_KEYS if key not in intent]
    missing_telemetry = [key for key in REQUIRED_TELEMETRY_KEYS if key not in telemetry]
    if missing_intent:
        notes.append(f"intent missing {missing_intent}")
    if missing_telemetry:
        notes.append(f"telemetry_stub missing {missing_telemetry}")

    glyph_chain = payload.get("glyph_chain")
    if isinstance(glyph_chain, list):
        if len(glyph_chain) > LEVEL0_GLYPH_CAP:
            notes.append(
                f"glyph_chain length {len(glyph_chain)} exceeds level-0 cap {LEVEL0_GLYPH_CAP}"
            )
    else:
        notes.append("glyph_chain missing or not a list")

    return ("ok" if not notes else "issues"), notes


def _evaluate_narration(payload: Dict[str, Any], stub: str) -> Tuple[str, List[str]]:
    notes: List[str] = []
    summary = payload.get("summary")
    if not summary:
        notes.append("summary missing")
        return "missing", notes

    normalized_summary = summary.strip()
    if stub:
        if stub not in normalized_summary:
            notes.append("summary does not contain reference stub")
        narration_key = payload.get("narrator", "")
        if narration_key:
            notes.append(f"narrator={narration_key}")
    return ("ok" if not notes or notes == [notes[-1]] else "issues"), notes


def _append_log(entry: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_monitor(dry_run: bool = False) -> List[Dict[str, Any]]:
    stub = _load_reference_stub()
    results: List[Dict[str, Any]] = []
    timestamp = _dt.datetime.utcnow().isoformat() + "Z"

    for report_path in _iter_report_files():
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
            entry = {
                "timestamp": timestamp,
                "file": str(report_path.relative_to(BASE_DIR)),
                "schema_status": "invalid_json",
                "narration_status": "unknown",
                "notes": [f"json error: {exc.msg}"],
            }
            results.append(entry)
            if not dry_run:
                _append_log(entry)
            continue

        schema_status, schema_notes = _validate_payload(payload)
        narration_status, narration_notes = _evaluate_narration(payload, stub)

        entry = {
            "timestamp": timestamp,
            "file": str(report_path.relative_to(BASE_DIR)),
            "schema_status": schema_status,
            "narration_status": narration_status,
            "notes": schema_notes + narration_notes,
        }
        results.append(entry)
        if not dry_run:
            _append_log(entry)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan exchange payloads for factory-order@1.0 compliance and narration alignment."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform checks without writing to the monitoring log",
    )
    args = parser.parse_args()

    results = run_monitor(dry_run=args.dry_run)
    ok = sum(1 for r in results if r["schema_status"] == "ok" and r["narration_status"] == "ok")
    drift = sum(1 for r in results if r["schema_status"] in {"drift", "issues"})
    narr_issues = sum(1 for r in results if r["narration_status"] in {"missing", "issues"})

    print(f"Scanned {len(results)} report(s).")
    print(f"  ✓ schema ok   : {ok}")
    print(f"  ⚠ schema warn : {drift}")
    print(f"  ⚠ narration   : {narr_issues}")

    if results:
        print("\nLatest entries:")
        for entry in results[-5:]:
            print(
                f"- {entry['file']}: schema={entry['schema_status']} narration={entry['narration_status']}"
            )


if __name__ == "__main__":
    main()
