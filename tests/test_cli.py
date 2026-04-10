"""Tests for the open-batch-llm CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from open_batch_llm.cli import main


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def sample_input(tmp_path: Path) -> Path:
    data = [
        {"id": "req-1", "prompt": "What is 2 + 2?"},
        {"id": "req-2", "prompt": "Name the planets."},
    ]
    file = tmp_path / "requests.json"
    file.write_text(json.dumps(data))
    return file


@pytest.fixture()
def invalid_json_file(tmp_path: Path) -> Path:
    file = tmp_path / "bad.json"
    file.write_text("not valid json {{{")
    return file


@pytest.fixture()
def non_array_json_file(tmp_path: Path) -> Path:
    file = tmp_path / "object.json"
    file.write_text(json.dumps({"prompt": "hello"}))
    return file


@pytest.fixture()
def missing_prompt_file(tmp_path: Path) -> Path:
    data = [{"id": "req-1"}, {"id": "req-2", "prompt": "ok"}]
    file = tmp_path / "missing.json"
    file.write_text(json.dumps(data))
    return file


# ---------------------------------------------------------------------------
# --version / --help
# ---------------------------------------------------------------------------


def test_help(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "batch" in result.output.lower()


def test_version(runner: CliRunner) -> None:
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


# ---------------------------------------------------------------------------
# validate command
# ---------------------------------------------------------------------------


def test_validate_valid_file(runner: CliRunner, sample_input: Path) -> None:
    result = runner.invoke(main, ["validate", str(sample_input)])
    assert result.exit_code == 0
    assert "Valid" in result.output


def test_validate_invalid_json(runner: CliRunner, invalid_json_file: Path) -> None:
    result = runner.invoke(main, ["validate", str(invalid_json_file)])
    assert result.exit_code == 1


def test_validate_non_array(runner: CliRunner, non_array_json_file: Path) -> None:
    result = runner.invoke(main, ["validate", str(non_array_json_file)])
    assert result.exit_code == 1


def test_validate_missing_prompt(runner: CliRunner, missing_prompt_file: Path) -> None:
    result = runner.invoke(main, ["validate", str(missing_prompt_file)])
    assert result.exit_code == 1
    assert "prompt" in result.output


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------


def test_run_dry_run(runner: CliRunner, sample_input: Path) -> None:
    result = runner.invoke(main, ["run", "--dry-run", str(sample_input)])
    assert result.exit_code == 0
    assert "Dry-run" in result.output


def test_run_invalid_json(runner: CliRunner, invalid_json_file: Path) -> None:
    result = runner.invoke(main, ["run", str(invalid_json_file)])
    assert result.exit_code == 1


def test_run_non_array(runner: CliRunner, non_array_json_file: Path) -> None:
    result = runner.invoke(main, ["run", str(non_array_json_file)])
    assert result.exit_code == 1


def test_run_outputs_json_to_stdout(runner: CliRunner, sample_input: Path) -> None:
    result = runner.invoke(main, ["run", str(sample_input)])
    assert result.exit_code == 0
    # The last JSON block in stdout should be parseable
    output = result.output
    json_start = output.rfind("[")
    assert json_start != -1, "No JSON array found in output"
    parsed = json.loads(output[json_start:])
    assert len(parsed) == 2


def test_run_outputs_json_to_file(runner: CliRunner, sample_input: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "results.json"
    result = runner.invoke(main, ["run", "-o", str(out_file), str(sample_input)])
    assert result.exit_code == 0
    assert out_file.exists()
    parsed = json.loads(out_file.read_text())
    assert len(parsed) == 2


def test_run_custom_provider_model(runner: CliRunner, sample_input: Path) -> None:
    result = runner.invoke(
        main,
        ["run", "--provider", "anthropic", "--model", "claude-3-haiku", str(sample_input)],
    )
    assert result.exit_code == 0
    assert "anthropic" in result.output
    assert "claude-3-haiku" in result.output
