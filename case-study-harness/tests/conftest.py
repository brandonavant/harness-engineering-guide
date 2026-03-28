"""Shared fixtures for case study harness tests."""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Provide a temporary data directory for test isolation."""
    d = tmp_path / "data"
    d.mkdir()
    return d


@pytest.fixture()
def post_tool_use_harness_payload() -> dict[str, Any]:
    """Return a PostToolUse payload targeting a harness file."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/home/user/my-project/.claude/rules/backend.md",
            "old_string": "old content",
            "new_string": "new content",
        },
        "tool_response": {
            "filePath": "/home/user/my-project/.claude/rules/backend.md",
            "success": True,
        },
        "tool_use_id": "toolu_test123",
    }


@pytest.fixture()
def post_tool_use_non_harness_payload() -> dict[str, Any]:
    """Return a PostToolUse payload targeting a non-harness file."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": "/home/user/my-project/src/app.py",
            "old_string": "old",
            "new_string": "new",
        },
        "tool_response": {"filePath": "/home/user/my-project/src/app.py", "success": True},
        "tool_use_id": "toolu_test456",
    }


@pytest.fixture()
def post_tool_use_failure_payload() -> dict[str, Any]:
    """Return a PostToolUseFailure payload."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "PostToolUseFailure",
        "tool_name": "Bash",
        "tool_input": {
            "command": "npm test",
            "description": "Run test suite",
        },
        "tool_use_id": "toolu_test789",
        "error": "Command exited with non-zero status code 1",
        "is_interrupt": False,
    }


@pytest.fixture()
def stop_payload() -> dict[str, Any]:
    """Return a Stop hook payload."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "Stop",
        "stop_hook_active": True,
        "last_assistant_message": "I've completed the refactoring of the authentication module.",
    }


@pytest.fixture()
def session_end_payload() -> dict[str, Any]:
    """Return a SessionEnd hook payload."""
    return {
        "session_id": "test-session-123",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "hook_event_name": "SessionEnd",
        "reason": "prompt_input_exit",
    }
