"""Contract Test Runner (skeleton) for ORDER-043.

Discovers golden emoji-runtime inputs and expected factory-order outputs,
validates schemas, and writes a JSON report. Exits non-zero on failures.

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
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def validate_with_schema_validator(paths: List[Path]) -> List[Tuple[str, str, Optional[str]]]:
    """Run tools/schema_validator.py over provided paths.

    Returns a list of tuples: (path_str, result, error)
    where result in {"ok", "skip", "error"}
    """
    results: List[Tuple[str, str, Optional[str]]] = []
    # Lazy import via module path
    from importlib.util import spec_from_file_location, module_from_spec

    root = Path(__file__).resolve().parents[1]
    validator_path = root / "tools" / "schema_validator.py"
    spec = spec_from_file_location("schema_validator", validator_path)
    if spec is None or spec.loader is None:
        for p in paths:
            results.append((str(p), "error", "schema_validator_import_failed"))
        return results
    module = module_from_spec(spec)
    sys.modules["schema_validator"] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]

    for p in paths:
        try:
            outcome = module.validate_file(p)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            results.append((str(p), "error", str(exc)))
        else:
            results.append((str(p), outcome, None))
    return results


def run_cases(cases: List[Case], fail_fast: bool) -> Dict[str, object]:
    report: Dict[str, object] = {
        "total": len(cases),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "schema_results": [],
        "cases": [],
    }

    # Schema validation pass for inputs and expected outputs
    schema_checks = []
    paths: List[Path] = []
    for case in cases:
        paths.append(case.input_path)
        paths.append(case.expected_path)
    schema_checks = validate_with_schema_validator(paths)
    report["schema_results"] = schema_checks

    # Basic structural comparison placeholder (to be extended by implementers)
    for case in cases:
        entry: Dict[str, object] = {"name": case.name, "status": "pending", "diff": None}
        try:
            input_payload = json.loads(case.input_path.read_text(encoding="utf-8"))
            expected_payload = json.loads(case.expected_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            entry["status"] = "error"
            entry["diff"] = f"load_error: {exc}"
            report["failed"] = int(report["failed"]) + 1
            report.setdefault("errors", []).append(entry)
            if fail_fast:
                break
            continue

        # Placeholder rule: ensure schemas exist and are the expected kinds
        in_schema = str(input_payload.get("schema", ""))
        ex_schema = str(expected_payload.get("schema", ""))
        if not in_schema.startswith("emoji-runtime") or not ex_schema.startswith("factory-order"):
            entry["status"] = "failed"
            entry["diff"] = {
                "reason": "schema_mismatch",
                "input_schema": in_schema,
                "expected_schema": ex_schema,
            }
            report["failed"] = int(report["failed"]) + 1
            report.setdefault("failures", []).append(entry)
            if fail_fast:
                break
            continue

        # Mark as passed for skeleton purposes; implementers will add real adapter comparisons
        entry["status"] = "passed"
        report["passed"] = int(report["passed"]) + 1
        report.setdefault("successes", []).append(entry)

    return report


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Contract Test Runner (ORDER-043)")
    parser.add_argument("--samples", default="contract_samples", help="Samples root directory")
    parser.add_argument("--report", default="reports/contract_test_report.json", help="Output report path")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    args = parser.parse_args(argv)

    samples_root = Path(args.samples).resolve()
    cases = discover_cases(samples_root)
    report = run_cases(cases, fail_fast=args.fail_fast)

    out_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[contract] cases={report['total']} passed={report['passed']} failed={report['failed']}")
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))

