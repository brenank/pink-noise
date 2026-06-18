import subprocess
import sys

import pytest

import pink_noise.cli as cli
from pink_noise.cli import build_parser, main
from pink_noise.domain.models import ValidationError


def test_cli_argument_parsing():
    args = build_parser().parse_args(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--output", "out"])
    assert args.profile == "consumer-speaker"
    assert args.layout == "5.1"
    assert args.companion_playback == "none"


def test_cli_parses_companion_playback_video_container():
    args = build_parser().parse_args(
        [
            "generate",
            "--profile",
            "consumer-speaker",
            "--layout",
            "5.1",
            "--output",
            "out",
            "--companion-playback",
            "video-container",
        ]
    )
    assert args.companion_playback == "video-container"


def test_cli_rejects_invalid_companion_playback_choice():
    with pytest.raises(SystemExit):
        build_parser().parse_args(
            [
                "generate",
                "--profile",
                "consumer-speaker",
                "--layout",
                "5.1",
                "--output",
                "out",
                "--companion-playback",
                "aac",
            ]
        )


def test_cli_success_text_and_artifact_paths(tmp_path, capsys):
    code = main(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--output", str(tmp_path), "--duration", "1", "--overwrite"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Generated 5 reference tracks" in out
    assert "Companion playback files: 0" in out
    assert "Summary:" in out
    assert "Validation:" in out
    assert "Calibration guide:" in out
    assert "Status: pass" in out


def test_cli_nonzero_error_behavior(tmp_path, capsys):
    code = main(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--channels", "lfe", "--output", str(tmp_path), "--duration", "1", "--overwrite"])
    assert code != 0
    assert "low-frequency" in capsys.readouterr().err


def test_cli_rejects_duration_outside_supported_bounds(tmp_path, capsys):
    code = main(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--output", str(tmp_path), "--duration", "0.5", "--overwrite"])
    assert code != 0
    assert "between 1 and 3600 seconds" in capsys.readouterr().err


def test_cli_companion_playback_exporter_failure_is_nonzero(tmp_path, capsys, monkeypatch):
    def fake_generate(request):
        raise ValidationError("companion playback exporter failed: unavailable")

    monkeypatch.setattr(cli, "generate", fake_generate)
    code = main(
        [
            "generate",
            "--profile",
            "consumer-speaker",
            "--layout",
            "2.0",
            "--channels",
            "fl",
            "--output",
            str(tmp_path),
            "--duration",
            "1",
            "--overwrite",
            "--companion-playback",
            "video-container",
        ]
    )
    assert code != 0
    assert "companion playback exporter" in capsys.readouterr().err.lower()


def test_python_module_delegates_to_cli(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pink_noise",
            "generate",
            "--profile",
            "consumer-speaker",
            "--layout",
            "2.0",
            "--output",
            str(tmp_path),
            "--duration",
            "1",
            "--overwrite",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Generated 2 reference tracks" in result.stdout
