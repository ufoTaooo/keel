from keel.prompt_prefix import tool_signature


def test_tool_signature_is_stable_across_registry_insertion_order(tmp_path):
    tools = {
        "b": {"schema": {"path": "str"}, "risky": False, "description": "B", "run": object()},
        "a": {"schema": {"command": "str"}, "risky": True, "description": "A", "run": object()},
    }
    reordered = {"a": tools["a"], "b": tools["b"]}

    assert tool_signature(tools) == tool_signature(reordered)
