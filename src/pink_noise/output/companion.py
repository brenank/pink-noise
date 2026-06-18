from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Protocol

from pink_noise.domain.models import CompanionPlaybackFile, ValidationError


class Runner(Protocol):
    def __call__(self, command: list[str], **kwargs) -> subprocess.CompletedProcess[str]: ...


def create_companion_playback(
    source_wav_path: Path,
    output_path: Path,
    *,
    ffmpeg_path: str = "ffmpeg",
    runner: Runner = subprocess.run,
) -> CompanionPlaybackFile:
    if not source_wav_path.exists():
        raise ValidationError(f"companion playback source WAV does not exist: {source_wav_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_path,
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=1280x720:r=1",
        "-i",
        str(source_wav_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "flac",
        "-shortest",
        str(output_path),
    ]
    try:
        result = runner(command, text=True, capture_output=True, check=False)
    except FileNotFoundError as exc:
        raise ValidationError(
            f"companion playback exporter '{ffmpeg_path}' is unavailable; install FFmpeg or use --companion-playback none"
        ) from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "unknown exporter failure").strip()
        raise ValidationError(f"companion playback exporter failed: {detail}")
    if not output_path.exists():
        raise ValidationError(f"companion playback exporter did not create expected file: {output_path}")
    return CompanionPlaybackFile(
        path=output_path,
        source_reference_track_path=source_wav_path,
        purpose="media_browser_compatibility",
        container="matroska",
        placeholder_video=True,
        audio_encoding="flac",
        status="created",
    )
