"""Tests for log_user_prompt.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_user_prompt
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_user_prompt, "DATA_DIR", data_dir)


@pytest.fixture()
def user_prompt_submit_payload() -> dict[str, Any]:
    """Return a UserPromptSubmit hook payload."""
    return {
        "session_id": "test-session-001",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": "/home/user/my-project",
        "permission_mode": "default",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Fix the authentication bug in the login handler",
    }


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_user_prompt.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_user_prompt.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestUserPromptEntry:
    def test_produces_user_prompt_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        user_prompt_submit_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, user_prompt_submit_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        user_prompt_submit_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, user_prompt_submit_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["event_type"] == "user_prompt"
        assert entry["source"] == "hook"
        assert "timestamp" in entry
        assert "session_id" in entry
        assert "prompt" in entry

    def test_session_id_from_payload(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        user_prompt_submit_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, user_prompt_submit_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["session_id"] == "test-session-001"

    def test_prompt_from_payload(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        user_prompt_submit_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, user_prompt_submit_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["prompt"] == "Fix the authentication bug in the login handler"

    def test_prompt_truncated_at_2000(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        user_prompt_submit_payload: dict[str, Any],
    ) -> None:
        user_prompt_submit_payload["prompt"] = "x" * 2500
        _run_with_payload(monkeypatch, user_prompt_submit_payload)
        entry = _read_entries(data_dir)[0]
        assert len(entry["prompt"]) == 2000
        assert entry["prompt"].endswith("...")

    def test_missing_prompt_uses_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        payload: dict[str, Any] = {
            "session_id": "test",
            "hook_event_name": "UserPromptSubmit",
        }
        _run_with_payload(monkeypatch, payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1
        assert entries[0]["prompt"] == ""

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("invalid"))
        log_user_prompt.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0
