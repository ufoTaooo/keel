# Keel Benchmark Data Provenance

This directory records a reproducible snapshot of the local agent-harness metrics
for the `main` branch. These are not production or user-traffic statistics; they
are deterministic benchmark and ablation results produced by Keel's own
evaluation harness.

## Directory contents

| File | Purpose |
| --- | --- |
| `harness-regression-v2.json` | Fixed harness regression task results |
| `context-ablation-v2.json` | Long-context governance ablation experiment |
| `memory-ablation-v2.json` | Structured memory ablation experiment |
| `recovery-ablation-v2.json` | Checkpoint / resume recovery experiment |
| `keel-benchmark-core-report.md` | Auto-generated core benchmark summary |

Only reviewable JSON/Markdown results are committed here; temporary workspace
copies are not. Each task's summary, verifier, status, and run-artifact fields
are written into `harness-regression-v2.json`.

## How to reproduce

From the repository root:

```bash
python3 - <<'PY'
from pathlib import Path
from keel.evaluation.evaluator import run_harness_regression_v2
from keel.evaluation.metrics import (
    run_context_ablation_v2,
    run_memory_ablation_v2,
    run_recovery_ablation_v2,
    write_benchmark_core_report,
)

out = Path("benchmarks/results/main-benchmark-repro-2026-07-02")
run_harness_regression_v2(
    benchmark_path=Path("benchmarks/coding_tasks.json"),
    artifact_path=out / "harness-regression-v2.json",
    workspace_root=Path("/tmp/keel-main-benchmark-workspaces"),
)
run_context_ablation_v2(out / "context-ablation-v2.json", repetitions=5)
run_memory_ablation_v2(out / "memory-ablation-v2.json", repetitions=5)
run_recovery_ablation_v2(out / "recovery-ablation-v2.json", repetitions=3)
write_benchmark_core_report(
    report_path=out / "keel-benchmark-core-report.md",
    harness_artifact_path=out / "harness-regression-v2.json",
    context_artifact_path=out / "context-ablation-v2.json",
    memory_artifact_path=out / "memory-ablation-v2.json",
    recovery_artifact_path=out / "recovery-ablation-v2.json",
)
PY
```

## What each layer measures

- **Harness regression** (`harness-regression-v2.json`): reads the 12 fixed
  tasks in `benchmarks/coding_tasks.json`. Each task copies a fresh fixture
  workspace, runs the agent with deterministic scripted model output, and checks
  the final workspace and run artifacts with the task's own verifier command -
  not just the model's final answer. Coverage includes README patching,
  invalid-patch recovery, path-escape recovery, repeated-read recovery,
  context-reduction checkpoints, freshness reanchor resume, workspace-mismatch
  resume, and durable-memory promotion accept/reject.
- **Context ablation** (`context-ablation-v2.json`): builds a fixed
  12-configuration matrix (3 history levels x 2 note levels x 2 request levels)
  and compares prompt character counts with and without context governance,
  while checking that the current request is preserved.
- **Memory ablation** (`memory-ablation-v2.json`): builds 12 memory-dependency
  tasks across `fact_lookup`, `edit_dependency`, and `history_reference`
  categories, and compares `memory_off`, `memory_irrelevant`, and `memory_on`
  variants. It measures whether the follow-up phase still needs tool reads to
  re-confirm facts already held in memory.
- **Recovery ablation** (`recovery-ablation-v2.json`): builds 10 recovery tasks
  across checkpoint resume, partial stale, workspace mismatch, schema mismatch,
  and partial-success recovery categories, comparing `resume_enabled` and
  `resume_disabled` variants, and tracks drift detection and false-accept rates.

Every run persists `task_state.json`, `trace.jsonl`, and `report.json`, so the
evidence is not limited to the model's final message.
