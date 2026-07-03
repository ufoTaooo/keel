from pathlib import Path

import keel
from keel import Keel, SessionStore, WorkspaceContext, build_agent, build_arg_parser, build_welcome, main


def test_public_api_exports_current_names_only():
    assert Keel is not None
    assert SessionStore is not None
    assert WorkspaceContext is not None
    assert callable(build_agent)
    assert callable(build_arg_parser)
    assert callable(build_welcome)
    assert callable(main)
    assert not hasattr(keel, "MiniAgent")
    assert "MiniAgent" not in keel.__all__


def test_build_agent_returns_keel(tmp_path):
    (tmp_path / "README.md").write_text("demo\n", encoding="utf-8")
    args = build_arg_parser().parse_args(["--cwd", str(tmp_path), "--approval", "auto"])

    agent = build_agent(args)

    assert isinstance(agent, Keel)


def test_lightweight_package_split_uses_package_paths_without_legacy_shims():
    from keel.evaluation.evaluator import BenchmarkEvaluator
    from keel.evaluation.metrics import run_context_ablation_v2
    from keel.features.memory import LayeredMemory
    from keel.providers.clients import FakeModelClient as ProviderFakeModelClient

    assert BenchmarkEvaluator is not None
    assert LayeredMemory is not None
    assert ProviderFakeModelClient is not None
    assert callable(run_context_ablation_v2)
    for legacy_module in ("evaluator.py", "metrics.py", "models.py", "memory.py"):
        assert not (Path("keel") / legacy_module).exists()


def test_packaging_discovers_keel_subpackages():
    pyproject_text = Path("pyproject.toml").read_text(encoding="utf-8")

    assert "[tool.setuptools.packages.find]" in pyproject_text
    assert 'include = ["keel*"]' in pyproject_text
