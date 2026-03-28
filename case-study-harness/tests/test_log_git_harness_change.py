"""Tests for log_git_harness_change.py."""

import json
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import log_git_harness_change
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_git_harness_change, "DATA_DIR", data_dir)


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_git_harness_change.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


def _mock_git_run(diff_tree_output: str, sha: str = "abc123def456", msg: str = "test commit") -> MagicMock:
    """Create a mock for subprocess.run that handles git commands."""

    def side_effect(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if "diff-tree" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=diff_tree_output, stderr="")
        if "rev-parse" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{sha}\n", stderr="")
        if "log" in cmd:
            return subprocess.CompletedProcess(cmd, 0, stdout=f"{msg}\n", stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    mock = MagicMock(side_effect=side_effect)
    return mock


class TestIsHarnessFile:
    def test_claude_rules(self) -> None:
        assert log_git_harness_change.is_harness_file(".claude/rules/foo.md") is True

    def test_claude_md(self) -> None:
        assert log_git_harness_change.is_harness_file("CLAUDE.md") is True

    def test_regular_file(self) -> None:
        assert log_git_harness_change.is_harness_file("src/main.py") is False


class TestGetChangedFiles:
    @patch("log_git_harness_change.subprocess.run")
    def test_parses_diff_tree_output(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, stdout="M\t.claude/rules/foo.md\nA\tCLAUDE.md\n", stderr=""
        )
        changes = log_git_harness_change.get_changed_files()
        assert changes == [("M", ".claude/rules/foo.md"), ("A", "CLAUDE.md")]

    @patch("log_git_harness_change.subprocess.run")
    def test_handles_rename_status(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess(
            [], 0, stdout="R100\t.claude/old.md\t.claude/new.md\n", stderr=""
        )
        changes = log_git_harness_change.get_changed_files()
        assert changes == [("R", ".claude/new.md")]

    @patch("log_git_harness_change.subprocess.run")
    def test_empty_output(self, mock_run: MagicMock) -> None:
        mock_run.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        changes = log_git_harness_change.get_changed_files()
        assert changes == []


class TestGitHarnessChangeEntry:
    @patch("log_git_harness_change.subprocess.run")
    def test_harness_commit_produces_entries(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("M\t.claude/rules/foo.md\n").side_effect
        log_git_harness_change.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    @patch("log_git_harness_change.subprocess.run")
    def test_non_harness_commit_produces_nothing(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("M\tsrc/app.py\nA\tREADME.md\n").side_effect
        log_git_harness_change.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0

    @patch("log_git_harness_change.subprocess.run")
    def test_multiple_harness_files(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("M\t.claude/rules/foo.md\nA\tCLAUDE.md\nM\tsrc/app.py\n").side_effect
        log_git_harness_change.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 2

    @patch("log_git_harness_change.subprocess.run")
    def test_status_mapping_created(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("A\t.claude/rules/new.md\n").side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert entry["action"] == "created"

    @patch("log_git_harness_change.subprocess.run")
    def test_status_mapping_modified(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("M\t.claude/rules/foo.md\n").side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert entry["action"] == "modified"

    @patch("log_git_harness_change.subprocess.run")
    def test_status_mapping_deleted(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("D\t.claude/rules/old.md\n").side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert entry["action"] == "deleted"

    @patch("log_git_harness_change.subprocess.run")
    def test_commit_sha_and_msg_populated(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run(
            "M\t.claude/rules/foo.md\n",
            sha="deadbeef12345678",
            msg="feat: update rule",
        ).side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert entry["commit_sha"] == "deadbeef12345678"
        assert entry["commit_msg"] == "feat: update rule"
        assert entry["source"] == "git_hook"

    @patch("log_git_harness_change.subprocess.run")
    def test_entry_has_all_required_fields(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run("A\tCLAUDE.md\n").side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert "timestamp" in entry
        assert entry["event_type"] == "harness_change"
        assert entry["source"] == "git_hook"
        assert "file_path" in entry
        assert "action" in entry
        assert "summary" in entry
        assert "commit_sha" in entry
        assert "commit_msg" in entry

    @patch("log_git_harness_change.subprocess.run")
    def test_git_failure_exits_cleanly(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")
        log_git_harness_change.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0

    @patch("log_git_harness_change.subprocess.run")
    def test_summary_includes_short_sha(self, mock_run: MagicMock, data_dir: Path) -> None:
        mock_run.side_effect = _mock_git_run(
            "A\tCLAUDE.md\n",
            sha="abcdef1234567890",
        ).side_effect
        log_git_harness_change.main()
        entry = _read_entries(data_dir)[0]
        assert "abcdef12" in entry["summary"]
