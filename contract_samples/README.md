# Contract Samples

Layout

- `emoji_runtime/`: golden emoji-runtime@1.0 payloads
- `factory_order_expected/`: matching factory-order@1.0 payloads

Filename pairs

- Each `emoji_runtime/<name>.json` must have a matching
  `factory_order_expected/<name>.json`.

Coverage

- Level-0 templates: `basic_ritual_forge`, `guarded_delivery`,
  `signal_loop`, `conditional_repeat`.
- Samples intentionally include actor/action/target/outcome vocabulary so
  drift checks can confirm the contract mapping.

Usage

- Run `python tools/contract_test_runner.py` from the repo root.
- Optional flags:
  - `--fail-fast` stops on the first failure.
  - `--junit reports/contract_tests.junit.xml` emits CI-friendly output.

