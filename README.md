# keel

`keel` is a lightweight local coding agent for code repositories. It runs directly in the terminal: it first looks at the current workspace, then uses a constrained set of tools to read files, edit files, and run commands, and it saves session state in a local `.keel/` directory.

It behaves more like a command-line assistant that keeps working inside a repository than a plain chat window. You can use it to investigate code, fix failing tests, analyze a repository, or run a one-off engineering task in the current project.

## What it is good for

- Investigating test failures in a local repository
- Reading the current code structure and proposing changes
- Iterating in small steps on existing files instead of guessing away from the repo
- Preserving context across a session so you can continue previous work

## Key features

- The package name is `keel`
- The CLI command is `keel`
- The module entry point is `python -m keel`
- Sessions are saved under `.keel/sessions/`
- Per-run artifacts are saved under `.keel/runs/<run_id>/`
- Four model backends are supported:
  - Ollama
  - OpenAI-compatible Responses API
  - Anthropic-compatible Messages API
  - DeepSeek Anthropic-compatible API

## Screenshots

Screenshots (CLI help, startup screen, and REPL commands) will be added once real `keel` captures are available.

## Installation

Requires Python 3.10+.

If you use `uv`, install the dependencies directly:

```bash
uv sync
```

If you already work inside your own Python environment, you can install it in editable mode instead:

```bash
pip install -e .
```

## Quick start

Start interactive mode in the current repository. The default provider is DeepSeek:

```bash
uv run keel
```

Point at a different working directory:

```bash
uv run keel --cwd /path/to/repo
```

Run a one-shot task directly:

```bash
uv run keel "inspect the test failures and propose a fix"
```

If the package is already installed in the current environment, you can also start it like this:

```bash
python -m keel
```

## Model backends

Keel reads the `.env` at the project root on startup. Keep your real keys in `.env`; the repository only ships `.env.example`. Configuration priority is:

```text
explicit CLI arguments > KEEL_* variables in .env > legacy environment variables > code defaults
```

The provider selection order specifically is:

```text
--provider > KEEL_PROVIDER > code default deepseek
```

Without `--provider` and without `KEEL_PROVIDER`, it defaults to `deepseek`. This is the recommended path: DeepSeek's Anthropic-compatible endpoint depends less on a local model environment than Ollama, and assumes one fewer default gateway layer than an OpenAI-compatible/Anthropic-compatible proxy. The other providers are still available: set `KEEL_PROVIDER=openai`, `KEEL_PROVIDER=anthropic`, or `KEEL_PROVIDER=ollama` in `.env`, or pass `--provider openai`, `--provider anthropic`, or `--provider ollama` explicitly.

The `.env` file is loaded before the provider client is built, and it overrides same-named environment variables in the current process. The model name and base URL can be temporarily overridden with `--model` and `--base-url`; the API key is only read from environment variables.

First-time local setup:

```bash
cp .env.example .env
```

Then fill in the key for the provider you want to use. `.env` is already ignored by `.gitignore`; do not commit real keys.

### Recommended: DeepSeek

The minimal configuration only needs a key:

```bash
KEEL_DEEPSEEK_API_KEY="your-api-key"
```

The default model and endpoint are:

```bash
KEEL_DEEPSEEK_API_BASE="https://api.deepseek.com/anthropic"
KEEL_DEEPSEEK_MODEL="deepseek-v4-pro"
```

So in the common case, filling in only `KEEL_DEEPSEEK_API_KEY` in `.env` is enough to start:

```bash
uv run keel
```

If you need to temporarily switch the model or proxy address, you do not have to edit `.env`; you can override directly:

```bash
uv run keel --model deepseek-v4-pro --base-url https://api.deepseek.com/anthropic
```

DeepSeek currently goes through the Anthropic-compatible Messages API, so the runtime reuses the Anthropic-compatible client; this only affects the HTTP protocol, not the CLI usage.

### Optional: right.codes

right.codes exposes two optional provider paths in Keel:

- `--provider openai`: uses the OpenAI-compatible `/responses`, with default base URL `https://www.right.codes/codex/v1` and default model `gpt-5.4`
- `--provider anthropic`: uses the Anthropic-compatible `/messages`, with default base URL `https://www.right.codes/claude/v1` and default model `claude-sonnet-4-6`

If right.codes gives you a single shared key, it is recommended to set just this one:

```bash
KEEL_RIGHT_CODES_API_KEY="your-right-codes-key"
```

Then pick the provider as needed:

```bash
uv run keel --provider openai
uv run keel --provider anthropic
```

If you want to distinguish the two provider keys explicitly, you can configure them separately:

```bash
KEEL_OPENAI_API_KEY="your-right-codes-key-for-codex"
KEEL_ANTHROPIC_API_KEY="your-right-codes-key-for-claude"
```

Do not write shell-expansion forms like `KEEL_OPENAI_API_KEY=$KEEL_RIGHT_CODES_API_KEY` in `.env`; Keel's `.env` parser only reads literals and does not expand variable references. Either set only `KEEL_RIGHT_CODES_API_KEY`, or fill the key string into the provider-specific variables separately.

If a request to right.codes returns an insufficient-quota error, it means the protocol and endpoint are already working but the current key has no available quota; switch to a key that has quota, or handle the quota in the right.codes console.

Current provider environment variables:

| provider | base URL | API key | model |
| --- | --- | --- | --- |
| `deepseek` | `KEEL_DEEPSEEK_API_BASE`, falls back to `DEEPSEEK_API_BASE`, default `https://api.deepseek.com/anthropic` | `KEEL_DEEPSEEK_API_KEY`, falls back to `DEEPSEEK_API_KEY` | `KEEL_DEEPSEEK_MODEL`, falls back to `DEEPSEEK_MODEL`, default `deepseek-v4-pro` |
| `openai` | `KEEL_OPENAI_API_BASE`, falls back to `OPENAI_API_BASE`, default `https://www.right.codes/codex/v1` | `KEEL_OPENAI_API_KEY`, falls back to `OPENAI_API_KEY`, `KEEL_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `KEEL_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` | `KEEL_OPENAI_MODEL`, falls back to `OPENAI_MODEL`, default `gpt-5.4` |
| `anthropic` | `KEEL_ANTHROPIC_API_BASE`, falls back to `ANTHROPIC_API_BASE`, default `https://www.right.codes/claude/v1` | `KEEL_ANTHROPIC_API_KEY`, falls back to `ANTHROPIC_API_KEY`, `KEEL_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `KEEL_OPENAI_API_KEY`, `OPENAI_API_KEY` | `KEEL_ANTHROPIC_MODEL`, falls back to `ANTHROPIC_MODEL`, default `claude-sonnet-4-6` |
| `ollama` | `--host`, default `http://127.0.0.1:11434` | not needed | `--model`, default `qwen3.5:4b` |

If there are extra sensitive environment variables that should be redacted from traces/reports, configure a comma-separated list of names with `KEEL_SECRET_ENV_NAMES`, or pass `--secret-env-name NAME` repeatedly at startup.

### OpenAI-compatible interface

To switch to an OpenAI-compatible `/responses` service, pass `--provider openai` explicitly:

```bash
uv run keel --provider openai
```

The default OpenAI-compatible interface uses right.codes' Codex endpoint:

```bash
KEEL_OPENAI_API_BASE="https://www.right.codes/codex/v1"
KEEL_RIGHT_CODES_API_KEY="your-right-codes-key"
KEEL_OPENAI_MODEL="gpt-5.4"
```

You can also switch to another OpenAI-compatible service:

```bash
KEEL_OPENAI_API_BASE="https://your-api.example/v1"
KEEL_OPENAI_API_KEY="your-api-key"
KEEL_OPENAI_MODEL="gpt-5.4"
```

### Anthropic-compatible interface

To switch to an Anthropic-compatible service, pass `--provider anthropic` explicitly:

```bash
uv run keel --provider anthropic
```

The default Anthropic-compatible interface uses right.codes' Claude endpoint:

```bash
KEEL_ANTHROPIC_API_BASE="https://www.right.codes/claude/v1"
KEEL_RIGHT_CODES_API_KEY="your-right-codes-key"
KEEL_ANTHROPIC_MODEL="claude-sonnet-4-6"
```

If your server reuses the same key across several compatible interfaces, `keel` also supports falling back from `KEEL_ANTHROPIC_API_KEY` to `ANTHROPIC_API_KEY`, `KEEL_RIGHT_CODES_API_KEY`, `RIGHT_CODES_API_KEY`, `KEEL_OPENAI_API_KEY`, or `OPENAI_API_KEY`.

### Ollama

To switch to a local Ollama, pass `--provider ollama` explicitly:

```bash
ollama serve
ollama pull qwen3.5:4b
uv run keel --provider ollama --model qwen3.5:4b
```

## Common interactive commands

- `/help`: show the built-in commands
- `/memory`: show the distilled working memory
- `/session`: show the current session file path
- `/reset`: clear the current session state
- `/exit` or `/quit`: exit the REPL

## Security and persistence

`keel` does not open up every action by default. High-risk operations such as shell execution and file writes are controlled by the approval mode:

- `--approval ask`
- `--approval auto`
- `--approval never`

After every run, these files are written under `.keel/runs/<run_id>/`:

- `task_state.json`
- `trace.jsonl`
- `report.json`

By default these are kept locally only and do not need to be committed with the repository.

## Development

Common local checks:

```bash
uv run pytest tests -q
uv run ruff check keel tests scripts
```

The internal code is split along lighter boundaries: `keel/evaluation/` holds the benchmark and metrics, `keel/providers/` holds the model provider clients, and `keel/features/` holds optional runtime capabilities. New code should use these package paths directly; the legacy `keel.evaluator`, `keel.metrics`, `keel.models`, and `keel.memory` imports are no longer kept as public entry points.
