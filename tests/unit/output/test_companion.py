import subprocess
from pathlib import Path

import pytest

from pink_noise.domain.models import ValidationError
from pink_noise.output.companion import create_companion_playback


def test_companion_exporter_builds_ffmpeg_command_with_placeholder_video_and_lossless_audio(tmp_path):
    source = tmp_path / "source.wav"
    output = tmp_path / "source__companion.mkv"
    source.write_bytes(b"wav")
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        output.write_bytes(b"mkv")
        return subprocess.CompletedProcess(command, 0, "", "")

    companion = create_companion_playback(source, output, ffmpeg_path="ffmpeg-test", runner=runner)

    command, kwargs = calls[0]
    assert command[:6] == ["ffmpeg-test", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=1"]
    assert ["-i", str(source)] == command[6:8]
    assert "-c:a" in command
    assert command[command.index("-c:a") + 1] == "flac"
    assert "-shortest" in command
    assert command[-1] == str(output)
    assert kwargs["capture_output"] is True
    assert companion.path == output
    assert companion.source_reference_track_path == source
    assert companion.container == "matroska"
    assert companion.placeholder_video is True
    assert companion.audio_encoding == "flac"
    assert companion.status == "created"


def test_companion_exporter_missing_executable_is_actionable(tmp_path):
    source = tmp_path / "source.wav"
    output = tmp_path / "source__companion.mkv"
    source.write_bytes(b"wav")

    def runner(command, **kwargs):
        raise FileNotFoundError(command[0])

    with pytest.raises(ValidationError, match="companion playback exporter"):
        create_companion_playback(source, output, ffmpeg_path="missing-ffmpeg", runner=runner)


def test_companion_exporter_nonzero_exit_is_actionable(tmp_path):
    source = tmp_path / "source.wav"
    output = tmp_path / "source__companion.mkv"
    source.write_bytes(b"wav")

    def runner(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", "bad codec")

    with pytest.raises(ValidationError, match="bad codec"):
        create_companion_playback(source, output, runner=runner)


def test_companion_exporter_requires_source_wav(tmp_path):
    with pytest.raises(ValidationError, match="source WAV"):
        create_companion_playback(Path("missing.wav"), tmp_path / "missing__companion.mkv")
