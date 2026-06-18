from __future__ import annotations

from typing import Any

from pink_noise.domain.models import CalibrationProfile, GenerationRequest, SpeakerLayout


def render_summary(
    request: GenerationRequest,
    profile: CalibrationProfile,
    layout: SpeakerLayout,
    tracks: list[dict[str, Any]],
    summary_path: str,
    validation_path: str,
    guide_path: str,
) -> str:
    status = "pass" if all(track["status"] == "pass" for track in tracks) else "fail"
    lines = [
        "# Pink Noise Generation Summary",
        "",
        f"- Profile: {profile.id} ({profile.display_name})",
        f"- Layout: {layout.id}",
        f"- Routing intent: {profile.purpose}",
        f"- RMS: {profile.default_rms_dbfs:g} dBFS",
        f"- Band: {profile.default_band_hz[0]:g}-{profile.default_band_hz[1]:g} Hz",
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
        "For normal consumer speaker trim, use 75 dB SPL, C-weighted, Slow at the main listening position with the AVR at reference 0 dB master volume after safe routing checks.",
        "",
        "## Tracks",
    ]
    for track in tracks:
        lines.append(
            f"- {track['target_channel_id']}: {track['path']} | RMS {track['rms_dbfs']:.2f} dBFS | "
            f"Band {track['band_hz'][0]:g}-{track['band_hz'][1]:g} Hz | Validation {track['status']}"
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
) -> dict[str, Any]:
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
            "routing_intent": profile.purpose,
            "channel_mask": layout.channel_mask,
            "channel_mask_policy": layout.channel_mask_policy,
            "validation_thresholds": profile.validation_thresholds,
        },
        "tracks": tracks,
        "overall_status": "pass" if all(track["status"] == "pass" for track in tracks) else "fail",
        "artifacts": {
            "summary_path": summary_path,
            "validation_data_path": validation_path,
            "calibration_guide_path": guide_path,
        },
        "errors": [],
    }
