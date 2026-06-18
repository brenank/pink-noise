from __future__ import annotations

from .models import CalibrationProfile, SpeakerChannel, ValidationError


DEFAULT_THRESHOLDS = {
    "rms_tolerance_db": 0.1,
    "slope_tolerance_db_per_octave": 0.5,
    "silent_channel_max_dbfs": -120.0,
}


BUILT_IN_PROFILES = {
    "consumer-speaker": CalibrationProfile(
        "consumer-speaker",
        "Consumer speaker trim",
        "consumer_speaker",
        -30.0,
        (500.0, 2000.0),
        measurement_guidance="Set the SPL meter to C-weighted Slow and adjust speaker trims to 75 dB SPL.",
        warnings=("Do not use speaker trim files for direct subwoofer calibration.",),
        validation_thresholds=DEFAULT_THRESHOLDS,
    ),
    "subwoofer-lfe-check": CalibrationProfile(
        "subwoofer-lfe-check",
        "Direct LFE channel check",
        "subwoofer_lfe_check",
        -30.0,
        (30.0, 80.0),
        measurement_guidance="Use longer averaging for low-frequency readings and confirm the LFE channel routes directly.",
        warnings=("Direct LFE checks do not validate crossover, delay, phase, or integration.",),
        validation_thresholds=DEFAULT_THRESHOLDS,
    ),
    "subwoofer-bass-managed": CalibrationProfile(
        "subwoofer-bass-managed",
        "Bass-managed sub-system check",
        "subwoofer_bass_managed",
        -30.0,
        (30.0, 80.0),
        measurement_guidance="Play low-frequency main-channel files through bass management to evaluate the summed sub-system.",
        warnings=("Confirm speakers are set to small and bass management is active.",),
        validation_thresholds=DEFAULT_THRESHOLDS,
    ),
    "full-band-analysis": CalibrationProfile(
        "full-band-analysis",
        "Full-band analyzer reference",
        "full_band_analysis",
        -30.0,
        (20.0, 20000.0),
        noise_mode="periodic",
        allowed_noise_modes=("random", "periodic"),
        measurement_guidance="Use for analyzer/RTA workflows, not basic 75 dB consumer trim matching.",
        warnings=("Full-band analysis files are not the recommended basic SPL trim signal.",),
        validation_thresholds=DEFAULT_THRESHOLDS,
    ),
    "pro-reference": CalibrationProfile(
        "pro-reference",
        "Pro/studio reference",
        "pro_reference",
        -20.0,
        (20.0, 20000.0),
        allowed_noise_modes=("random", "periodic"),
        measurement_guidance="Use only when a pro/studio -20 dBFS reference workflow is intended.",
        warnings=("Pro reference files are separated from consumer AVR 75 dB trim defaults.",),
        validation_thresholds=DEFAULT_THRESHOLDS,
    ),
}


def get_profile(profile_id: str) -> CalibrationProfile:
    try:
        return BUILT_IN_PROFILES[profile_id]
    except KeyError as exc:
        raise ValidationError(f"unknown profile '{profile_id}'") from exc


def is_channel_compatible(profile: CalibrationProfile, channel: SpeakerChannel) -> bool:
    if profile.purpose == "consumer_speaker":
        return not channel.is_low_frequency
    if profile.purpose == "subwoofer_lfe_check":
        return channel.role == "lfe"
    if profile.purpose == "subwoofer_bass_managed":
        return not channel.is_low_frequency
    return True


def compatibility_error(profile: CalibrationProfile, channel: SpeakerChannel) -> str:
    if profile.purpose == "consumer_speaker" and channel.is_low_frequency:
        return f"channel '{channel.id}' is low-frequency; use subwoofer-lfe-check or subwoofer-bass-managed"
    if profile.purpose == "subwoofer_lfe_check" and channel.role != "lfe":
        return f"channel '{channel.id}' is not LFE; direct LFE checks require an LFE channel"
    if profile.purpose == "subwoofer_bass_managed" and channel.is_low_frequency:
        return f"channel '{channel.id}' bypasses bass management; choose a main channel for bass-managed checks"
    return f"profile '{profile.id}' is incompatible with channel '{channel.id}'"
