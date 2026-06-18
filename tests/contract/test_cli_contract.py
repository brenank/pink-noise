import subprocess
import sys

from pink_noise.cli import build_parser, main


def test_cli_argument_parsing():
    args = build_parser().parse_args(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--output", "out"])
    assert args.profile == "consumer-speaker"
    assert args.layout == "5.1"


def test_cli_success_text_and_artifact_paths(tmp_path, capsys):
    code = main(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--output", str(tmp_path), "--duration", "1", "--overwrite"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Generated 5 reference tracks" in out
    assert "Summary:" in out
    assert "Validation:" in out
    assert "Calibration guide:" in out
    assert "Status: pass" in out


def test_cli_nonzero_error_behavior(tmp_path, capsys):
    code = main(["generate", "--profile", "consumer-speaker", "--layout", "5.1", "--channels", "lfe", "--output", str(tmp_path), "--duration", "1", "--overwrite"])
    assert code != 0
    assert "low-frequency" in capsys.readouterr().err


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
