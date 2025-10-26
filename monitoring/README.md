# Monitoring Hooks

This directory houses R&D's monitoring utilities for High Command.

## Quint Alignment Monitor

`quint_alignment_monitor.py` scans `exchange/reports` payloads for
`factory-order@1.0` compliance and keeps a rolling log of narrator
alignment checks.

Run the hook in the repository root:

```pwsh
python monitoring/quint_alignment_monitor.py
```

Use `--dry-run` to inspect results without writing to the log:

```pwsh
python monitoring/quint_alignment_monitor.py --dry-run
```

Outputs are appended to `monitoring/logs/quint_alignment_report.jsonl`.  High
Command can tail this file to surface schema drift or narration issues.
