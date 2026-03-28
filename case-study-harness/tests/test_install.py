"""Tests for install.py."""

import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest

import install


@pytest.fixture()
def target_repo(tmp_path: Path) -> Path:
    """Create a minimal target repo structure with .git/ directory."""
    repo = tmp_path / "target"
    repo.mkdir()
    (repo / ".git" / "hooks").mkdir(parents=True)
    return repo


@pytest.fixture()
def source_harness(tmp_path: Path) -> Path:
    """Create a miniature source harness layout for isolated testing."""
    harness = tmp_path / "harness"
    harness.mkdir()

    # hooks/post-commit
    hooks = harness / "hooks"
    hooks.mkdir()
    (hooks / "post-commit").write_text("#!/usr/bin/env bash\n# hook\n")

    # claude/rules/
    rules = harness / "claude" / "rules"
    rules.mkdir(parents=True)
    (rules / "case-study-observer.md").write_text("# Observer Rule\n")

    # claude/skills/
    for skill_name in ("case-study-capture", "case-study-synthesize"):
        skill_dir = harness / "claude" / "skills" / skill_name
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}\n")
        (scripts_dir / "helper.py").write_text(f"# {skill_name} helper\n")

    # claude/hooks-config.json
    config: dict[str, Any] = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 case-study-harness/scripts/log_harness_change.py",
                            "timeout": 10,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": "python3 case-study-harness/scripts/log_turn_summary.py",
                            "timeout": 10,
                        }
                    ],
                }
            ],
        }
    }
    (harness / "claude" / "hooks-config.json").write_text(json.dumps(config, indent=2) + "\n")

    return harness


@pytest.fixture(autouse=True)
def _patch_harness_dir(monkeypatch: pytest.MonkeyPatch, source_harness: Path) -> None:
    """Point all module constants at the test source harness."""
    monkeypatch.setattr(install, "HARNESS_DIR", source_harness)
    monkeypatch.setattr(install, "HOOK_SOURCE", source_harness / "hooks" / "post-commit")
    monkeypatch.setattr(install, "HOOKS_CONFIG", source_harness / "claude" / "hooks-config.json")
    monkeypatch.setattr(install, "RULES_SOURCE", source_harness / "claude" / "rules")
    monkeypatch.setattr(install, "SKILLS_SOURCE", source_harness / "claude" / "skills")


class TestValidateTarget:
    def test_valid_repo_passes(self, target_repo: Path) -> None:
        install.validate_target(target_repo)

    def test_missing_directory_exits(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit):
            install.validate_target(tmp_path / "nonexistent")

    def test_missing_git_dir_exits(self, tmp_path: Path) -> None:
        repo = tmp_path / "no-git"
        repo.mkdir()
        with pytest.raises(SystemExit):
            install.validate_target(repo)


class TestCheckExistingHook:
    def test_no_hook_returns_false(self, target_repo: Path) -> None:
        assert install.check_existing_hook(target_repo) is False

    def test_existing_file_hook_exits(self, target_repo: Path) -> None:
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        hook_path.write_text("#!/bin/sh\necho 'existing'\n")
        with pytest.raises(SystemExit):
            install.check_existing_hook(target_repo)

    def test_existing_wrong_symlink_exits(self, target_repo: Path, tmp_path: Path) -> None:
        other_hook = tmp_path / "other-hook"
        other_hook.write_text("#!/bin/sh\n")
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        os.symlink(str(other_hook), str(hook_path))
        with pytest.raises(SystemExit):
            install.check_existing_hook(target_repo)

    def test_correct_symlink_returns_true(self, target_repo: Path, source_harness: Path) -> None:
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        os.symlink(str(source_harness / "hooks" / "post-commit"), str(hook_path))
        assert install.check_existing_hook(target_repo) is True


class TestCreateDataDir:
    def test_creates_directory(self, target_repo: Path) -> None:
        result = install.create_data_dir(target_repo)
        assert result is not None
        assert (target_repo / "case-study-harness" / "data").is_dir()

    def test_existing_directory_returns_none(self, target_repo: Path) -> None:
        (target_repo / "case-study-harness" / "data").mkdir(parents=True)
        result = install.create_data_dir(target_repo)
        assert result is None


class TestInstallHook:
    def test_creates_symlink(self, target_repo: Path) -> None:
        result = install.install_hook(target_repo)
        assert result is not None
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        assert hook_path.is_symlink()

    def test_symlink_is_relative(self, target_repo: Path) -> None:
        install.install_hook(target_repo)
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        raw_link = os.readlink(str(hook_path))
        assert not os.path.isabs(raw_link)

    def test_symlink_resolves_to_source(self, target_repo: Path, source_harness: Path) -> None:
        install.install_hook(target_repo)
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        assert hook_path.resolve() == (source_harness / "hooks" / "post-commit").resolve()

    def test_creates_hooks_directory_if_missing(self, target_repo: Path) -> None:
        shutil.rmtree(target_repo / ".git" / "hooks")
        install.install_hook(target_repo)
        assert (target_repo / ".git" / "hooks" / "post-commit").is_symlink()

    def test_existing_correct_symlink_returns_none(self, target_repo: Path, source_harness: Path) -> None:
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        os.symlink(str(source_harness / "hooks" / "post-commit"), str(hook_path))
        result = install.install_hook(target_repo)
        assert result is None


class TestCopyRules:
    def test_copies_rule_file(self, target_repo: Path) -> None:
        actions = install.copy_rules(target_repo)
        assert len(actions) == 1
        assert "case-study-observer.md" in actions[0]
        assert (target_repo / ".claude" / "rules" / "case-study-observer.md").exists()

    def test_creates_claude_rules_directory(self, target_repo: Path) -> None:
        install.copy_rules(target_repo)
        assert (target_repo / ".claude" / "rules").is_dir()

    def test_identical_file_skips_silently(self, target_repo: Path, source_harness: Path) -> None:
        dest = target_repo / ".claude" / "rules"
        dest.mkdir(parents=True)
        shutil.copy2(
            str(source_harness / "claude" / "rules" / "case-study-observer.md"),
            str(dest / "case-study-observer.md"),
        )
        actions = install.copy_rules(target_repo)
        assert len(actions) == 0

    def test_different_content_warns_and_skips(self, target_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
        dest = target_repo / ".claude" / "rules"
        dest.mkdir(parents=True)
        (dest / "case-study-observer.md").write_text("# Different content\n")
        actions = install.copy_rules(target_repo)
        assert any("conflict" in a.lower() for a in actions)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err


class TestCopySkills:
    def test_copies_both_skill_directories(self, target_repo: Path) -> None:
        actions = install.copy_skills(target_repo)
        assert len(actions) == 2
        for skill_name in ("case-study-capture", "case-study-synthesize"):
            assert (target_repo / ".claude" / "skills" / skill_name / "SKILL.md").exists()
            assert (target_repo / ".claude" / "skills" / skill_name / "scripts" / "helper.py").exists()

    def test_creates_skills_directory(self, target_repo: Path) -> None:
        install.copy_skills(target_repo)
        assert (target_repo / ".claude" / "skills").is_dir()

    def test_identical_directory_skips_silently(self, target_repo: Path, source_harness: Path) -> None:
        dest = target_repo / ".claude" / "skills"
        for skill_name in ("case-study-capture", "case-study-synthesize"):
            shutil.copytree(
                str(source_harness / "claude" / "skills" / skill_name),
                str(dest / skill_name),
            )
        actions = install.copy_skills(target_repo)
        assert len(actions) == 0

    def test_different_content_warns_and_skips(self, target_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
        dest = target_repo / ".claude" / "skills" / "case-study-capture"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("# Different\n")
        actions = install.copy_skills(target_repo)
        assert any("conflict" in a.lower() and "case-study-capture" in a for a in actions)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err
        # The other skill should still be copied
        assert (target_repo / ".claude" / "skills" / "case-study-synthesize" / "SKILL.md").exists()

    def test_one_conflict_does_not_block_other(self, target_repo: Path) -> None:
        dest = target_repo / ".claude" / "skills" / "case-study-capture"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("# Different\n")
        actions = install.copy_skills(target_repo)
        copied_actions = [a for a in actions if "Copied" in a]
        assert len(copied_actions) == 1
        assert "case-study-synthesize" in copied_actions[0]


class TestMergeHooksConfig:
    def test_creates_settings_json_when_missing(self, target_repo: Path) -> None:
        (target_repo / ".claude").mkdir(parents=True, exist_ok=True)
        actions = install.merge_hooks_config(target_repo)
        assert any("Created" in a for a in actions)
        assert (target_repo / ".claude" / "settings.json").exists()

    def test_adds_hooks_to_empty_settings(self, target_repo: Path) -> None:
        settings_path = target_repo / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text("{}\n")
        actions = install.merge_hooks_config(target_repo)
        assert any("PostToolUse" in a for a in actions)
        assert any("Stop" in a for a in actions)
        settings = json.loads(settings_path.read_text())
        assert "PostToolUse" in settings["hooks"]
        assert "Stop" in settings["hooks"]

    def test_preserves_existing_hooks(self, target_repo: Path) -> None:
        settings_path = target_repo / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        existing: dict[str, Any] = {
            "hooks": {
                "PreToolUse": [
                    {"hooks": [{"type": "command", "command": "echo pre-tool"}]}
                ]
            }
        }
        settings_path.write_text(json.dumps(existing) + "\n")
        install.merge_hooks_config(target_repo)
        settings = json.loads(settings_path.read_text())
        assert "PreToolUse" in settings["hooks"]
        assert len(settings["hooks"]["PreToolUse"]) == 1

    def test_skips_already_present_commands(self, target_repo: Path) -> None:
        settings_path = target_repo / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        # Pre-populate with the same commands
        existing: dict[str, Any] = {
            "hooks": {
                "PostToolUse": [
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python3 case-study-harness/scripts/log_harness_change.py",
                                "timeout": 10,
                            }
                        ],
                    }
                ],
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "python3 case-study-harness/scripts/log_turn_summary.py",
                                "timeout": 10,
                            }
                        ],
                    }
                ],
            }
        }
        settings_path.write_text(json.dumps(existing) + "\n")
        actions = install.merge_hooks_config(target_repo)
        hook_actions = [a for a in actions if "Added hook" in a]
        assert len(hook_actions) == 0

    def test_handles_settings_with_no_hooks_key(self, target_repo: Path) -> None:
        settings_path = target_repo / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text('{"permissions": {}}\n')
        install.merge_hooks_config(target_repo)
        settings = json.loads(settings_path.read_text())
        assert "hooks" in settings
        assert "permissions" in settings

    def test_preserves_non_hook_keys(self, target_repo: Path) -> None:
        settings_path = target_repo / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text('{"permissions": {"allow": ["Read"]}, "hooks": {}}\n')
        install.merge_hooks_config(target_repo)
        settings = json.loads(settings_path.read_text())
        assert settings["permissions"] == {"allow": ["Read"]}


class TestPrintSummary:
    def test_prints_actions(self, capsys: pytest.CaptureFixture[str]) -> None:
        install.print_summary(["Created data/", "Copied rule: observer.md"])
        captured = capsys.readouterr()
        assert "installation complete" in captured.out
        assert "Created data/" in captured.out
        assert "Copied rule: observer.md" in captured.out

    def test_no_actions_prints_already_installed(self, capsys: pytest.CaptureFixture[str]) -> None:
        install.print_summary([])
        captured = capsys.readouterr()
        assert "nothing to do" in captured.out


class TestMainIntegration:
    def test_full_clean_install(self, target_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.argv", ["install.py", str(target_repo)])
        result = install.main()
        assert result == 0
        assert (target_repo / "case-study-harness" / "data").is_dir()
        assert (target_repo / ".git" / "hooks" / "post-commit").is_symlink()
        assert (target_repo / ".claude" / "rules" / "case-study-observer.md").exists()
        assert (target_repo / ".claude" / "skills" / "case-study-capture" / "SKILL.md").exists()
        assert (target_repo / ".claude" / "skills" / "case-study-synthesize" / "SKILL.md").exists()
        assert (target_repo / ".claude" / "settings.json").exists()

    def test_idempotent_double_install(
        self, target_repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr("sys.argv", ["install.py", str(target_repo)])
        install.main()
        capsys.readouterr()  # clear first run output
        result = install.main()
        assert result == 0
        captured = capsys.readouterr()
        assert "nothing to do" in captured.out

    def test_hook_conflict_exits_without_modifications(
        self, target_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        hook_path = target_repo / ".git" / "hooks" / "post-commit"
        hook_path.write_text("#!/bin/sh\necho existing\n")
        monkeypatch.setattr("sys.argv", ["install.py", str(target_repo)])
        with pytest.raises(SystemExit):
            install.main()
        # No modifications should have been made
        assert not (target_repo / "case-study-harness" / "data").exists()
        assert not (target_repo / ".claude").exists()

    def test_prints_summary(
        self, target_repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        monkeypatch.setattr("sys.argv", ["install.py", str(target_repo)])
        install.main()
        captured = capsys.readouterr()
        assert "installation complete" in captured.out
        assert "Symlinked" in captured.out

    def test_missing_argument_returns_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.argv", ["install.py"])
        result = install.main()
        assert result == 1

    def test_help_flag_returns_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.argv", ["install.py", "--help"])
        result = install.main()
        assert result == 0
