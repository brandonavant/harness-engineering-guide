"""Tests for log_friction.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_friction
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_friction, "DATA_DIR", data_dir)


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_friction.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_friction.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestTruncate:
    def test_short_text_unchanged(self) -> None:
        assert log_friction.truncate("short") == "short"

    def test_long_text_truncated(self) -> None:
        long_text = "x" * 600
        result = log_friction.truncate(long_text)
        assert len(result) == 500
        assert result.endswith("...")

    def test_exact_limit_unchanged(self) -> None:
        exact = "x" * 500
        assert log_friction.truncate(exact) == exact


class TestExtractContext:
    def test_command_field(self) -> None:
        result = log_friction.extract_context({"command": "npm test"})
        assert result == "Running: npm test"

    def test_file_path_field(self) -> None:
        result = log_friction.extract_context({"file_path": "/tmp/foo.py"})
        assert result == "Operating on /tmp/foo.py"

    def test_fallback_to_json(self) -> None:
        result = log_friction.extract_context({"pattern": "*.md"})
        assert '"pattern"' in result


class TestFrictionEntry:
    def test_produces_friction_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["event_type"] == "friction"
        assert entry["source"] == "hook"
        assert "timestamp" in entry
        assert "tool_name" in entry
        assert "error_summary" in entry
        assert "context" in entry

    def test_tool_name_captured(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["tool_name"] == "Bash"

    def test_error_summary_captured(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["error_summary"] == "Command exited with non-zero status code 1"

    def test_context_from_command(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["context"] == "Running: npm test"

    def test_error_summary_truncated(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_failure_payload: dict[str, Any],
    ) -> None:
        post_tool_use_failure_payload["error"] = "E" * 600
        _run_with_payload(monkeypatch, post_tool_use_failure_payload)
        entry = _read_entries(data_dir)[0]
        assert len(entry["error_summary"]) == 500

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("bad json"))
        log_friction.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0
