"""Tests for log_session_summary.py."""

import io
import json
import sys
from pathlib import Path
from typing import Any

import log_session_summary
import pytest


@pytest.fixture(autouse=True)
def _patch_data_dir(monkeypatch: pytest.MonkeyPatch, data_dir: Path) -> None:
    monkeypatch.setattr(log_session_summary, "DATA_DIR", data_dir)


def _run_with_payload(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    log_session_summary.main()


def _read_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_file = data_dir / log_session_summary.LOG_FILE
    if not log_file.exists():
        return []
    return [json.loads(line) for line in log_file.read_text().strip().splitlines()]


class TestSessionSummaryEntry:
    def test_produces_session_summary_entry(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, stop_payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1

    def test_entry_has_all_required_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, stop_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["event_type"] == "session_summary"
        assert entry["source"] == "hook"
        assert "timestamp" in entry
        assert "description" in entry
        assert "observations" in entry
        assert "token_usage" in entry

    def test_description_from_last_message(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, stop_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["description"] == "I've completed the refactoring of the authentication module."

    def test_description_truncated(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        stop_payload["last_assistant_message"] = "x" * 600
        _run_with_payload(monkeypatch, stop_payload)
        entry = _read_entries(data_dir)[0]
        assert len(entry["description"]) == 500
        assert entry["description"].endswith("...")

    def test_token_usage_is_null(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, stop_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["token_usage"] is None

    def test_observations_is_empty_string(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
        stop_payload: dict[str, Any],
    ) -> None:
        _run_with_payload(monkeypatch, stop_payload)
        entry = _read_entries(data_dir)[0]
        assert entry["observations"] == ""

    def test_missing_last_message_uses_empty(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        payload: dict[str, Any] = {
            "session_id": "test",
            "hook_event_name": "Stop",
        }
        _run_with_payload(monkeypatch, payload)
        entries = _read_entries(data_dir)
        assert len(entries) == 1
        assert entries[0]["description"] == ""

    def test_malformed_json_exits_silently(
        self,
        monkeypatch: pytest.MonkeyPatch,
        data_dir: Path,
    ) -> None:
        monkeypatch.setattr(sys, "stdin", io.StringIO("invalid"))
        log_session_summary.main()
        entries = _read_entries(data_dir)
        assert len(entries) == 0
