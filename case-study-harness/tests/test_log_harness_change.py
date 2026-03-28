"""Tests for log_harness_change.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_harness_change
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_harness_change, "DATA_DIR", data_dir)


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_harness_change.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_harness_change.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestIsHarnessFile:
    def test_claude_rules_file(self) -> None:
        assert log_harness_change.is_harness_file(".claude/rules/backend.md") is True

    def test_claude_settings(self) -> None:
        assert log_harness_change.is_harness_file(".claude/settings.json") is True

    def test_claude_md(self) -> None:
        assert log_harness_change.is_harness_file("CLAUDE.md") is True

    def test_regular_source_file(self) -> None:
        assert log_harness_change.is_harness_file("src/app.py") is False

    def test_nested_claude_md(self) -> None:
        assert log_harness_change.is_harness_file("docs/CLAUDE.md") is False


class TestNormalizePath:
    def test_absolute_to_relative(self) -> None:
        result = log_harness_change.normalize_path(
            "/home/user/project/.claude/rules/foo.md",
            "/home/user/project",
        )
        assert result == ".claude/rules/foo.md"

    def test_root_file(self) -> None:
        result = log_harness_change.normalize_path(
            "/home/user/project/CLAUDE.md",
            "/home/user/project",
        )
        assert result == "CLAUDE.md"


class TestHarnessChangeEntry:
    def test_harness_file_produces_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_non_harness_file_produces_no_output(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_non_harness_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_non_harness_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 0

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entry = _read_entries(data_dir)[0]
        assert "timestamp" in entry
        assert entry["event_type"] == "harness_change"
        assert entry["source"] == "hook"
        assert "file_path" in entry
        assert "action" in entry
        assert "summary" in entry
        assert "commit_sha" in entry
        assert "commit_msg" in entry

    def test_edit_maps_to_modified(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        post_tool_use_harness_payload["tool_name"] = "Edit"
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["action"] == "modified"

    def test_write_maps_to_created(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        post_tool_use_harness_payload["tool_name"] = "Write"
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["action"] == "created"

    def test_commit_sha_is_null(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["commit_sha"] is None
        assert entry["commit_msg"] is None

    def test_file_path_is_relative(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        entry = _read_entries(data_dir)[0]
        assert not entry["file_path"].startswith("/")
        assert entry["file_path"] == ".claude/rules/backend.md"

    def test_data_dir_created_if_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        post_tool_use_harness_payload: dict[str, Any],
    ) -> None:
        new_data_dir = tmp_path / "nonexistent" / "data"
        monkeypatch.setattr(log_harness_change, "DATA_DIR", new_data_dir)
        _run_with_payload(monkeypatch, post_tool_use_harness_payload)
        assert new_data_dir.exists()
        log_path = new_data_dir / log_harness_change.LOG_FILE
        entries = [json.loads(line) for line in log_path.read_text().strip().splitlines()]
        assert len(entries) == 1

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("not valid json"))
        log_harness_change.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0

    def test_claude_md_detected(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        payload: dict[str, Any] = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/home/user/project/CLAUDE.md"},
            "cwd": "/home/user/project",
        }
        _run_with_payload(monkeypatch, payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1
        assert entries[0]["file_path"] == "CLAUDE.md"
