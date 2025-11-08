"""Contract Test Runner for ORDER-043.

Discovers golden emoji-runtime inputs and expected factory-order outputs,
validates schemas, performs drift checks, and writes a JSON report. Exits
non-zero on failures. Optionally produces JUnit XML for CI pipelines.

Conventions:
- Samples directory defaults to `contract_samples/`
- Inputs:     `contract_samples/emoji_runtime/<name>.json`
- Expected:   `contract_samples/factory_order_expected/<name>.json`
- Report:     `reports/contract_test_report.json`
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

try:
    from tools.schema_validator import SchemaValidationError, validate_file
except ModuleNotFoundError:  # pragma: no cover - fallback for direct execution
    REPO_ROOT = Path(__file__).resolve().parents[1]
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from tools.schema_validator import SchemaValidationError, validate_file


@dataclass
class Case:
    name: str
    input_path: Path
    expected_path: Path


def discover_cases(samples_dir: Path) -> List[Case]:
    inputs = (samples_dir / "emoji_runtime").glob("*.json")
    cases: List[Case] = []
    for input_file in inputs:
        name = input_file.stem
        expected = samples_dir / "factory_order_expected" / f"{name}.json"
        if expected.exists():
            cases.append(Case(name=name, input_path=input_file, expected_path=expected))
    return sorted(cases, key=lambda c: c.name)


def validate_with_schema_validator(paths: Iterable[Path]) -> List[Dict[str, Optional[str]]]:
    """Validate the provided payloads with the shared schema validator."""

    results: List[Dict[str, Optional[str]]] = []
    for payload_path in paths:
        try:
            outcome = validate_file(payload_path)
        except SchemaValidationError as exc:
            results.append({"path": str(payload_path), "status": "error", "message": str(exc)})
        except Exception as exc:  # noqa: BLE001 - defensive guard
            results.append({"path": str(payload_path), "status": "error", "message": f"unexpected_error: {exc}"})
        else:
            results.append({"path": str(payload_path), "status": outcome, "message": None})
    return results


EMOJI_ALLOWED_FIELDS = {
    "schema",
    "glyph_chain",
    "spoken",
    "raw",
    "actor",
    "verb",
    "target",
    "qualifiers",
    "outcomes",
    "summary",
    "intent",
    "telemetry_stub",
    "created_at",
}

FACTORY_ALLOWED_FIELDS = {
    "schema",
    "order_id",
    "issued_by",
    "target",
    "priority",
    "timestamp_issued",
    "summary",
    "context",
    "directives",
    "requires_ack",
    "dependencies",
    "attachments",
    "success_criteria",
    "safety_notes",
    "metadata",
}

_OUTCOME_SYNONYMS = {
    "success": {"success", "victory", "triumph"},
    "victory": {"victory", "success", "triumph"},
    "ready": {"ready", "prepared"},
    "steadfast": {"steadfast", "secure", "guarded"},
}


def _word_variants(token: str) -> List[str]:
    base = token.lower()
    variants = {base}
    if not base:
        return list(variants)
    if base.endswith("e"):
        variants.add(base[:-1] + "ing")
    variants.add(base + "s")
    variants.add(base + "ed")
    return list(variants)


def _summary_contains(summary: str, token: str) -> bool:
    summary_lc = summary.lower()
    for variant in _word_variants(token):
        if variant and variant in summary_lc:
            return True
    return False


def _target_tokens(target: str) -> List[str]:
    return [piece for piece in target.replace("-", " ").split() if piece]


def check_drift(case: Case, input_payload: Dict[str, Any], expected_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    input_keys = set(input_payload.keys())
    unexpected_input = sorted(input_keys - EMOJI_ALLOWED_FIELDS)
    if unexpected_input:
        issues.append({"type": "unexpected_input_fields", "fields": unexpected_input})

    missing_input = sorted(EMOJI_ALLOWED_FIELDS - input_keys)
    if missing_input:
        issues.append({"type": "missing_input_fields", "fields": missing_input})

    expected_keys = set(expected_payload.keys())
    unexpected_expected = sorted(expected_keys - FACTORY_ALLOWED_FIELDS)
    if unexpected_expected:
        issues.append({"type": "unexpected_expected_fields", "fields": unexpected_expected})

    missing_expected = sorted({"schema", "order_id", "issued_by", "target", "priority", "timestamp_issued", "summary", "directives"} - expected_keys)
    if missing_expected:
        issues.append({"type": "missing_expected_fields", "fields": missing_expected})

    # Glyph/spoken alignment check
    if len(input_payload.get("glyph_chain", [])) != len(input_payload.get("spoken", [])):
        issues.append({"type": "glyph_spoken_mismatch", "expected_len": len(input_payload.get("glyph_chain", [])), "spoken_len": len(input_payload.get("spoken", []))})

    # Summary tokens must include actor/action/target/outcome hints
    summary = expected_payload.get("summary", "")
    intent = input_payload.get("intent", {})
    actor = intent.get("actor", "")
    action = intent.get("action", "")
    target = intent.get("target", "")
    outcome = intent.get("outcome", "")

    if actor and not _summary_contains(summary, actor):
        issues.append({"type": "summary_missing_actor", "actor": actor})
    if action and not _summary_contains(summary, action):
        issues.append({"type": "summary_missing_action", "action": action})
    if target and not all(_summary_contains(summary, token) for token in _target_tokens(target)):
        issues.append({"type": "summary_missing_target", "target": target})
    if outcome:
        allowed = _OUTCOME_SYNONYMS.get(outcome.lower(), {outcome.lower()})
        if not any(token in summary.lower() for token in allowed):
            issues.append({"type": "summary_missing_outcome", "outcome": outcome})

    # Directive alignment: first directive action should reflect intent action
    directives = expected_payload.get("directives", []) or []
    if directives:
        first_action = directives[0].get("action", "") if isinstance(directives[0], dict) else ""
        if action and action.lower() not in _word_variants(first_action):
            issues.append({"type": "directive_mismatch", "expected_action": action, "found": first_action})
    else:
        issues.append({"type": "missing_directives"})

    return issues


def run_cases(cases: List[Case], fail_fast: bool) -> Dict[str, object]:
    start = datetime.now(UTC)
    report: Dict[str, object] = {
    "generated_at": start.isoformat().replace("+00:00", "Z"),
        "total": len(cases),
        "passed": 0,
        "failed": 0,
        "schema_results": [],
        "cases": [],
        "drift_summary": defaultdict(int),
    }

    paths: List[Path] = []
    for case in cases:
        paths.extend([case.input_path, case.expected_path])
    schema_checks = validate_with_schema_validator(paths)
    report["schema_results"] = schema_checks
    schema_lookup = {item["path"]: item for item in schema_checks}

    for case in cases:
        entry: Dict[str, Any] = {"name": case.name, "status": "pending", "issues": []}
        related_checks = [
            schema_lookup.get(str(case.input_path)),
            schema_lookup.get(str(case.expected_path)),
        ]
        schema_errors = [chk for chk in related_checks if chk and chk["status"] != "ok"]
        if schema_errors:
            entry["status"] = "failed"
            entry["issues"] = [{"type": "schema_validation", "details": schema_errors}]
            report["failed"] += 1
            report.setdefault("failures", []).append(entry)
            if fail_fast:
                report["duration_seconds"] = (datetime.now(UTC) - start).total_seconds()
                return report
            report["cases"].append(entry)
            continue

        try:
            input_payload = json.loads(case.input_path.read_text(encoding="utf-8"))
            expected_payload = json.loads(case.expected_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "failed"
            entry["issues"] = [{"type": "load_error", "message": str(exc)}]
            report["failed"] += 1
            report.setdefault("errors", []).append(entry)
            if fail_fast:
                report["duration_seconds"] = (datetime.now(UTC) - start).total_seconds()
                return report
            report["cases"].append(entry)
            continue

        drift_issues = check_drift(case, input_payload, expected_payload)
        if drift_issues:
            entry["status"] = "failed"
            entry["issues"] = drift_issues
            for issue in drift_issues:
                key = issue.get("type", "unknown")
                report["drift_summary"][key] += 1
            report["failed"] += 1
            report.setdefault("failures", []).append(entry)
            report["cases"].append(entry)
            if fail_fast:
                report["duration_seconds"] = (datetime.now(UTC) - start).total_seconds()
                return report
            continue

        entry["status"] = "passed"
        report["passed"] += 1
        report.setdefault("successes", []).append(entry)
        report["cases"].append(entry)

    report["drift_summary"] = dict(report["drift_summary"])
    report["duration_seconds"] = (datetime.now(UTC) - start).total_seconds()
    return report


def _write_junit(report: Dict[str, object], junit_path: Path) -> None:
    testsuite = Element(
        "testsuite",
        name="contract_tests",
        tests=str(report["total"]),
        failures=str(report["failed"]),
        time=f"{report.get('duration_seconds', 0):.3f}",
    )
    for case in report["cases"]:
        testcase = SubElement(testsuite, "testcase", name=case["name"], time="0.000")
        if case["status"] != "passed":
            failure = SubElement(testcase, "failure", message=case["status"])
            failure.text = json.dumps(case.get("issues", []), ensure_ascii=False, indent=2)
    junit_path.parent.mkdir(parents=True, exist_ok=True)
    junit_path.write_bytes(tostring(testsuite, encoding="utf-8"))


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Contract Test Runner (ORDER-043)")
    parser.add_argument("--samples", default="contract_samples", help="Samples root directory")
    parser.add_argument("--report", default="reports/contract_test_report.json", help="Output report path")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--junit", help="Optional JUnit XML output path")
    args = parser.parse_args(argv)

    samples_root = Path(args.samples).resolve()
    cases = discover_cases(samples_root)
    report = run_cases(cases, fail_fast=args.fail_fast)

    out_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.junit:
        _write_junit(report, Path(args.junit))

    print(f"[contract] cases={report['total']} passed={report['passed']} failed={report['failed']}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))

