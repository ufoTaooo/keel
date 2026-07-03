import subprocess
import sys
from pathlib import Path

import mini_keel


def test_mini_keel_module_and_public_exports():
    assert mini_keel.Keel is not None
    assert mini_keel.FakeModelClient is not None
    assert not hasattr(mini_keel, "MiniAgent")
    result = subprocess.run([sys.executable, "-m", "mini_keel", "--help"], capture_output=True, text=True, check=True)
    assert "Teaching-sized Keel agent harness" in result.stdout


def test_readme_main_mapping_points_to_existing_files():
    repo_root = Path(__file__).resolve().parents[3]
    main_files = [
        "keel/cli.py",
        "keel/runtime.py",
        "keel/agent_loop.py",
        "keel/context_manager.py",
        "keel/providers/clients.py",
        "keel/tool_executor.py",
        "keel/tools.py",
        "keel/task_state.py",
        "keel/run_store.py",
        "keel/workspace.py",
    ]
    for path in main_files:
        assert (repo_root / path).exists()
