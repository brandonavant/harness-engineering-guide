"""Tests for log_tool_use.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_tool_use
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_tool_use, "DATA_DIR", data_dir)


@pytest.fixture()
def post_tool_use_payload() -> dict[str, Any]:
    """Return a generic PostToolUse hook payload."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "PostToolUse",
        "tool_name": "Read",
        "tool_input": {
            "file_path": "/home/user/my-project/src/app.py",
        },
        "tool_response": {"content": "file contents here"},
        "tool_use_id": "toolu_test001",
    }


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_tool_use.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_tool_use.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestExtractSummary:
    def test_bash_extracts_command(self) -> None:
        result = log_tool_use.extract_summary("Bash", {"command": "npm test"})
        assert result == "Running: npm test"

    def test_read_extracts_file_path(self) -> None:
        result = log_tool_use.extract_summary("Read", {"file_path": "/tmp/foo.py"})
        assert result == "Reading /tmp/foo.py"

    def test_edit_extracts_file_path(self) -> None:
        result = log_tool_use.extract_summary("Edit", {"file_path": "/tmp/bar.py"})
        assert result == "Editing /tmp/bar.py"

    def test_write_extracts_file_path(self) -> None:
        result = log_tool_use.extract_summary("Write", {"file_path": "/tmp/baz.py"})
        assert result == "Writing /tmp/baz.py"

    def test_glob_extracts_pattern(self) -> None:
        result = log_tool_use.extract_summary("Glob", {"pattern": "**/*.py"})
        assert result == "Glob: **/*.py"

    def test_grep_extracts_pattern(self) -> None:
        result = log_tool_use.extract_summary("Grep", {"pattern": "def main"})
        assert result == "Grep: def main"

    def test_webfetch_extracts_url(self) -> None:
        result = log_tool_use.extract_summary(
            "WebFetch", {"url": "https://example.com"}
        )
        assert result == "Fetching https://example.com"

    def test_agent_extracts_description(self) -> None:
        result = log_tool_use.extract_summary(
            "Agent", {"description": "Explore codebase"}
        )
        assert result == "Subagent: Explore codebase"

    def test_unknown_tool_returns_name(self) -> None:
        result = log_tool_use.extract_summary("CustomTool", {"foo": "bar"})
        assert result == "CustomTool"

    def test_long_summary_truncated(self) -> None:
        long_cmd = "x" * 300
        result = log_tool_use.extract_summary("Bash", {"command": long_cmd})
        assert len(result) == 200
        assert result.endswith("...")


class TestToolUseEntry:
    def test_produces_tool_use_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["event_type"] == "tool_use"
        assert entry["source"] == "hook"
        assert "timestamp" in entry
        assert "session_id" in entry
        assert "tool_name" in entry
        assert "tool_summary" in entry

    def test_session_id_from_payload(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["session_id"] == "test-session-001"

    def test_tool_name_captured(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["tool_name"] == "Read"

    def test_tool_summary_for_read(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["tool_summary"] == "Reading /home/user/my-project/src/app.py"

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("bad json"))
        log_tool_use.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0
