"""Tests for log_session_end.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_session_end
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_session_end, "DATA_DIR", data_dir)


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_session_end.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_session_end.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestSessionEndEntry:
    def test_produces_session_end_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        session_end_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, session_end_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        session_end_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, session_end_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["event_type"] == "session_end"
        assert entry["source"] == "hook"
        assert "timestamp" in entry
        assert entry["session_id"] == "test-session-123"
        assert entry["reason"] == "prompt_input_exit"
        assert entry["token_usage"] is None

    def test_missing_session_id_uses_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        payload: dict[str, Any] = {
            "hook_event_name": "SessionEnd",
            "reason": "clear",
        }
        _run_with_payload(monkeypatch, payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1
        assert entries[0]["session_id"] == ""

    def test_missing_reason_uses_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        payload: dict[str, Any] = {
            "hook_event_name": "SessionEnd",
            "session_id": "test",
        }
        _run_with_payload(monkeypatch, payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1
        assert entries[0]["reason"] == ""

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("invalid"))
        log_session_end.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0
