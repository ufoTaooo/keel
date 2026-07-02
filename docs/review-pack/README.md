# Keel Review Pack

## Project pitch

Keel is a lightweight local coding agent harness for repository-grounded engineering tasks. It wraps a model with workspace context, explicit tools, state tracking, memory, run artifacts, and benchmark evidence.

## Architecture map

- `keel.cli` wires configuration, provider clients, workspace context, and the runtime.
- `keel.runtime.Keel` coordinates the agent control surface.
- `keel.context_manager` builds bounded model context from prefix, memory, history, and the current request.
- `keel.tools` defines the explicit tool allowlist used by the runtime.
- `keel.run_store` writes per-run artifacts for review and replay.

## Benchmark evidence

Benchmark runs should preserve reproducibility metadata, task rows, summary counts, and failure categories so reviewers can distinguish runtime regressions from task or provider failures.

## Sample run artifact list

- `.keel/runs/<run_id>/task_state.json`
- `.keel/runs/<run_id>/trace.jsonl`
- `.keel/runs/<run_id>/report.json`
