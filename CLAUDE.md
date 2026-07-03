# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests -q

# Run a single test file
uv run pytest tests/test_agent_loop.py -q

# Run a single test by name
uv run pytest tests/test_agent_loop.py::test_name -q

# Lint
uv run ruff check keel tests scripts

# Start interactive REPL (default: deepseek provider)
uv run keel

# One-shot task
uv run keel "inspect the test failures and propose a fix"

# Resume latest session
uv run keel --resume latest
```

## Architecture

### Core data flow

`cli.py` → `build_agent()` assembles a `Keel` instance → `Keel.ask()` → `AgentLoop.run()` → perceive/decide/act loop → traces/reports written to `.keel/runs/<run_id>/`.

The main loop in `agent_loop.py` follows: build prompt → call model → parse response → if tool call: execute tool, checkpoint, continue; if final answer: return.

### Key modules

- **`keel/runtime.py`** — `Keel` class: the central facade. Owns session state, memory, tool registry, approval policy, and the prompt-building pipeline. All tool calls funnel through `run_tool()` → `execute_tool()` → `ToolExecutor`.
- **`keel/agent_loop.py`** — `AgentLoop.run()`: the perceive→decide→act loop, extracted from `Keel`. Manages `TaskState`, trace events, and checkpoint triggers.
- **`keel/tools.py`** — The tool whitelist: `list_files`, `read_file`, `search`, `run_shell`, `write_file`, `patch_file`, `delegate`. Risky tools (`run_shell`, `write_file`, `patch_file`) require approval based on `approval_policy`.
- **`keel/providers/clients.py`** — Model backend adapters (`OllamaModelClient`, `OpenAICompatibleModelClient`, `AnthropicCompatibleModelClient`, `FakeModelClient`). All expose a single `complete(prompt, max_new_tokens, **kwargs)` interface.
- **`keel/features/memory.py`** — `LayeredMemory`: working memory (task summary, recent files, file summaries, episodic notes) plus durable memory (project conventions, key decisions, dependency facts, user preferences). Kept small so it fits in each prompt without crowding history.
- **`keel/context_manager.py`** — Prompt assembly and budget control. Total budget: 12,000 chars split across prefix/memory/relevant_memory/history/current_request. Excess triggers section compression in order: relevant_memory → history → memory → prefix.
- **`keel/checkpoint.py`** — Checkpoint/resume logic. Checkpoints are written after every tool execution, context reduction, and run completion. Resume detects workspace or tool-signature mismatches vs. the saved runtime identity.
- **`keel/workspace.py`** — `WorkspaceContext`: snapshot of the repo root, git branch, recent commits, and project docs. Also supplies `IGNORED_PATH_NAMES` and `MAX_HISTORY`.
- **`keel/security.py`** — Secret redaction for trace/report output. API keys are stripped before anything is written to `.keel/runs/`.
- **`keel/session_store.py`** — Persists session JSON to `.keel/sessions/`.
- **`keel/run_store.py`** — Writes `task_state.json`, `trace.jsonl`, and `report.json` to `.keel/runs/<run_id>/`.
- **`keel/cli.py`** — CLI entry point (`main()`). Handles provider selection, secret name collection, one-shot vs. REPL mode, and the `/help /memory /session /reset /exit` REPL commands.

### Package layout

```
keel/
  providers/    # model backend clients
  features/     # optional runtime capabilities (memory)
  # root: runtime, agent_loop, tools, cli, context_manager, checkpoint, security, workspace, session_store, run_store
tests/          # pytest suite
scripts/        # benchmark/experiment runners
benchmarks/     # coding task definitions
```

### Subpackage boundaries

New code goes in the appropriate subpackage: `keel/providers/` for model clients, `keel/features/` for optional runtime capabilities. The legacy flat imports (`keel.evaluator`, `keel.metrics`, `keel.models`, `keel.memory`) are no longer public entry points.

### Model output parsing

`Keel.parse()` in `runtime.py` handles two tool call formats:
1. `<tool>{"name": "...", "args": {...}}</tool>` — JSON inside tag
2. `<tool name="write_file" path="file.py"><content>...</content></tool>` — XML attributes with child tags

Final answers use `<final>...</final>` or bare text. Malformed responses return `"retry"` kind, which re-prompts without incrementing `tool_steps`.

### Delegate (sub-agent)

`delegate` tool spawns a child `Keel` with `read_only=True`, `approval_policy="never"`, and `max_steps=3`. Used to investigate sub-tasks without granting write access. Sub-agents cannot further delegate (depth limit enforced in `build_tool_registry`).

### Provider configuration

Default provider is `deepseek`. Priority: `--provider` > `KEEL_PROVIDER` env var > code default. DeepSeek uses the Anthropic-compatible client pointed at `https://api.deepseek.com/anthropic`. The `.env` file is loaded by `load_project_env()` before the client is built.
