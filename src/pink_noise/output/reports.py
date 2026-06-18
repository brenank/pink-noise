from __future__ import annotations

from typing import Any

from pink_noise.domain.models import CalibrationProfile, CompanionPlaybackFile, GenerationRequest, SpeakerLayout


def render_summary(
    request: GenerationRequest,
    profile: CalibrationProfile,
    layout: SpeakerLayout,
    tracks: list[dict[str, Any]],
    summary_path: str,
    validation_path: str,
    guide_path: str,
    companion_files: list[CompanionPlaybackFile] | None = None,
) -> str:
    companion_files = companion_files or []
    status = "pass" if all(track["status"] == "pass" for track in tracks) else "fail"
    lines = [
        "# Pink Noise Generation Summary",
        "",
        f"- Profile: {profile.id} ({profile.display_name})",
        f"- Layout: {layout.id}",
        f"- Routing intent: {profile.purpose}",
        f"- RMS: {profile.default_rms_dbfs:g} dBFS",
        f"- Band: {profile.default_band_hz[0]:g}-{profile.default_band_hz[1]:g} Hz",
        f"- Duration: {request.duration_seconds or profile.default_duration_seconds:g} seconds",
        f"- Noise mode: {request.noise_mode or profile.noise_mode}",
        f"- Seed: {request.seed if request.seed is not None else 0}",
        f"- Status: {status}",
        f"- Summary: {summary_path}",
        f"- Validation: {validation_path}",
        f"- Calibration guide: {guide_path}",
        "",
        "## Measurement Guidance",
        profile.measurement_guidance,
        "",
    ]
    if profile.purpose == "consumer_speaker":
        lines.extend(
            [
                "For normal consumer speaker trim, use 75 dB SPL, C-weighted, Slow at the main listening position with the AVR at reference 0 dB master volume after safe routing checks.",
                "",
            ]
        )
    lines.extend(
        [
            "## Channel Mapping",
            *[f"- ch{channel.order}: {channel.id} ({channel.label}, {channel.role})" for channel in layout.channels],
            "",
            "## Tracks",
        ]
    )
    for track in tracks:
        lines.append(
            f"- {track['target_channel_id']}: {track['path']} | active ch{track.get('active_channel_index')} | "
            f"silent {track.get('silent_channel_indices', [])} | RMS {track['rms_dbfs']:.2f} dBFS | "
            f"Peak {track.get('peak_dbfs', 0):.2f} dBFS | Crest {track.get('crest_factor_db', 0):.2f} dB | "
            f"Band {track['band_hz'][0]:g}-{track['band_hz'][1]:g} Hz | "
            f"Duration {track.get('duration_seconds', request.duration_seconds or profile.default_duration_seconds):g}s | "
            f"Noise {track.get('noise_mode', request.noise_mode or profile.noise_mode)} | Validation {track['status']}"
        )
    if companion_files:
        lines.extend(["", "## Companion Playback Files"])
        for companion in companion_files:
            lines.append(
                f"- {companion.path}: playback-compatibility copy of {companion.source_reference_track_path} | "
                f"container {companion.container} | lossless audio {companion.audio_encoding} | "
                f"purpose {companion.purpose}"
            )
    if profile.warnings:
        lines.extend(["", "## Warnings", *[f"- {warning}" for warning in profile.warnings]])
    return "\n".join(lines) + "\n"


def render_validation_data(
    request: GenerationRequest,
    profile: CalibrationProfile,
    layout: SpeakerLayout,
    tracks: list[dict[str, Any]],
    summary_path: str,
    validation_path: str,
    guide_path: str,
    companion_files: list[CompanionPlaybackFile] | None = None,
) -> dict[str, Any]:
    companion_files = companion_files or []
    companion_dicts = [_companion_to_dict(companion) for companion in companion_files]
    return {
        "schema_version": "1.0",
        "request": {
            "profile_id": profile.id,
            "layout_id": layout.id,
            "duration_seconds": request.duration_seconds or profile.default_duration_seconds,
            "sample_rate_hz": 48000,
            "bit_depth": 24,
            "noise_mode": request.noise_mode or profile.noise_mode,
            "seed": request.seed,
            "companion_playback": request.companion_playback,
            "routing_intent": profile.purpose,
            "channel_mask": layout.channel_mask,
            "channel_mask_policy": layout.channel_mask_policy,
            "validation_thresholds": profile.validation_thresholds,
        },
        "tracks": tracks,
        "companion_playback_files": companion_dicts,
        "overall_status": "pass" if all(track["status"] == "pass" for track in tracks) else "fail",
        "artifacts": {
            "summary_path": summary_path,
            "validation_data_path": validation_path,
            "calibration_guide_path": guide_path,
            "companion_playback_paths": [str(companion.path) for companion in companion_files],
        },
        "errors": [],
    }


def _companion_to_dict(companion: CompanionPlaybackFile) -> dict[str, Any]:
    data: dict[str, Any] = {
        "path": str(companion.path),
        "source_reference_track_path": str(companion.source_reference_track_path),
        "purpose": companion.purpose,
        "container": companion.container,
        "placeholder_video": companion.placeholder_video,
        "audio_encoding": companion.audio_encoding,
        "status": companion.status,
    }
    if companion.error:
        data["error"] = companion.error
    return data
