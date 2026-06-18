from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .audio.generator import generate_pink_noise
from .audio.validation import validate_track
from .audio.wav import write_wav_24
from .domain.layouts import get_layout
from .domain.models import GenerationRequest, NoiseSpecification, ValidationError
from .domain.profiles import compatibility_error, get_profile, is_channel_compatible
from .output.guide import render_guide
from .output.reports import render_summary, render_validation_data


@dataclass(frozen=True)
class GenerationResult:
    track_paths: list[Path]
    summary_path: Path
    validation_path: Path
    guide_path: Path
    validation_data: dict[str, object]


def generate(request: GenerationRequest) -> GenerationResult:
    profile = get_profile(request.profile_id)
    layout = request.custom_layout or get_layout(request.layout_id)
    mode = request.noise_mode or profile.noise_mode
    if mode not in profile.allowed_noise_modes:
        raise ValidationError(f"profile '{profile.id}' does not allow noise mode '{mode}'")
    duration = request.duration_seconds or profile.default_duration_seconds
    targets = _target_channels(request, profile, layout)
    output_dir = request.output_directory
    output_dir.mkdir(parents=True, exist_ok=True)
    planned_paths = [
        _filename(output_dir, profile.id, layout.id, channel.order, channel.id, profile.default_band_hz, profile.default_rms_dbfs, mode)
        for channel in targets
    ]
    summary_path = output_dir / request.summary_name
    validation_path = output_dir / request.validation_name
    guide_path = output_dir / "CALIBRATION-GUIDE.md"
    planned_paths.extend([summary_path, validation_path, guide_path])
    conflicts = [path for path in planned_paths if path.exists()]
    if conflicts and not request.overwrite:
        names = ", ".join(path.name for path in conflicts[:5])
        raise ValidationError(f"output files already exist ({names}); use --overwrite or choose another destination")

    track_results = []
    wav_paths: list[Path] = []
    for index, channel in enumerate(targets):
        spec = NoiseSpecification(
            rms_dbfs=profile.default_rms_dbfs,
            band_hz=profile.default_band_hz,
            duration_seconds=duration,
            noise_mode=mode,
            seed=request.seed if request.seed is not None else f"{profile.id}:{layout.id}:{channel.id}",
        )
        mono = generate_pink_noise(spec.duration_seconds, spec.sample_rate_hz, spec.band_hz, spec.rms_dbfs, spec.seed, spec.noise_mode)
        samples = np.zeros((mono.size, len(layout.channels)), dtype=np.float64)
        samples[:, channel.order] = mono
        wav_path = _filename(output_dir, profile.id, layout.id, channel.order, channel.id, spec.band_hz, spec.rms_dbfs, spec.noise_mode)
        write_wav_24(wav_path, samples, spec.sample_rate_hz, layout.channel_mask)
        validation = validate_track(
            wav_path,
            channel.order,
            channel.id,
            spec.band_hz,
            spec.rms_dbfs,
            layout.channel_mask,
            profile.validation_thresholds["rms_tolerance_db"],
            profile.validation_thresholds["slope_tolerance_db_per_octave"],
            profile.validation_thresholds["silent_channel_max_dbfs"],
        )
        validation["noise_mode"] = spec.noise_mode
        validation["periodic_period_seconds"] = 4.0 if spec.noise_mode == "periodic" else None
        validation["routing_intent"] = profile.purpose
        track_results.append(validation)
        wav_paths.append(wav_path)
        if validation["status"] != "pass":
            raise ValidationError(f"generated track failed validation for channel '{channel.id}': {validation['failures']}")

    validation_data = render_validation_data(request, profile, layout, track_results, str(summary_path), str(validation_path), str(guide_path))
    validation_data["generated_at"] = datetime.now(timezone.utc).isoformat()
    summary = render_summary(request, profile, layout, track_results, str(summary_path), str(validation_path), str(guide_path))
    guide = render_guide(profile)
    summary_path.write_text(summary, encoding="utf-8")
    validation_path.write_text(json.dumps(validation_data, indent=2), encoding="utf-8")
    guide_path.write_text(guide, encoding="utf-8")
    return GenerationResult(wav_paths, summary_path, validation_path, guide_path, validation_data)


def _target_channels(request: GenerationRequest, profile, layout):
    requested = [layout.channel_by_id(channel_id.strip()) for channel_id in request.target_channels] if request.target_channels else list(layout.channels)
    compatible = []
    for channel in requested:
        if is_channel_compatible(profile, channel):
            compatible.append(channel)
        elif request.target_channels:
            raise ValidationError(compatibility_error(profile, channel))
    if not compatible:
        raise ValidationError(f"profile '{profile.id}' has no compatible channels in layout '{layout.id}'")
    return compatible


def _filename(output_dir: Path, profile_id: str, layout_id: str, channel_index: int, channel_id: str, band_hz: tuple[float, float], rms_dbfs: float, mode: str) -> Path:
    name = (
        f"{profile_id}__{layout_id}__ch{channel_index}-{channel_id}__"
        f"{band_hz[0]:g}-{band_hz[1]:g}hz__{rms_dbfs:g}dbfs__{mode}.wav"
    )
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", name)
    if len(safe) > 119:
        safe = safe[:115] + ".wav"
    return output_dir / safe
