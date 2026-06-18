from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


class ValidationError(ValueError):
    """Raised when a request violates calibration or output safety rules."""


ChannelRole = Literal["main", "surround", "height", "lfe", "subwoofer", "custom"]
NoiseMode = Literal["random", "periodic"]
CompanionPlaybackMode = Literal["none", "video-container"]
ProfilePurpose = Literal[
    "consumer_speaker",
    "subwoofer_lfe_check",
    "subwoofer_bass_managed",
    "full_band_analysis",
    "pro_reference",
]


@dataclass(frozen=True)
class SpeakerChannel:
    id: str
    label: str
    role: ChannelRole
    order: int
    wave_bit: int | None = None
    aliases: tuple[str, ...] = ()

    @property
    def is_low_frequency(self) -> bool:
        return self.role in {"lfe", "subwoofer"} or self.id in {"lfe", "sub"}


@dataclass(frozen=True)
class SpeakerLayout:
    id: str
    display_name: str
    channels: tuple[SpeakerChannel, ...]
    channel_mask: int
    channel_mask_policy: Literal["speaker_positions", "directout"] = "speaker_positions"
    is_builtin: bool = True
    source: Literal["built_in", "custom"] = "built_in"

    def __post_init__(self) -> None:
        if not self.channels:
            raise ValidationError("layout channels must include at least one channel")
        ids = [channel.id for channel in self.channels]
        if len(ids) != len(set(ids)):
            raise ValidationError("layout channel ids must be unique")
        orders = [channel.order for channel in self.channels]
        if orders != list(range(len(self.channels))):
            raise ValidationError("layout channel order must be zero-based and contiguous")
        if self.channel_mask_policy == "speaker_positions" and self.channel_mask.bit_count() != len(self.channels):
            raise ValidationError("channel_mask bit count must match channel count")

    def channel_by_id(self, channel_id: str) -> SpeakerChannel:
        normalized = channel_id.lower()
        for channel in self.channels:
            if normalized == channel.id or normalized in channel.aliases:
                return channel
        raise ValidationError(f"unknown channel '{channel_id}' for layout '{self.id}'")


@dataclass(frozen=True)
class CalibrationProfile:
    id: str
    display_name: str
    purpose: ProfilePurpose
    default_rms_dbfs: float
    default_band_hz: tuple[float, float]
    default_duration_seconds: float = 60.0
    min_duration_seconds: float = 1.0
    max_duration_seconds: float = 3600.0
    noise_mode: NoiseMode = "random"
    allowed_noise_modes: tuple[NoiseMode, ...] = ("random",)
    measurement_guidance: str = ""
    warnings: tuple[str, ...] = ()
    validation_thresholds: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class NoiseSpecification:
    rms_dbfs: float
    band_hz: tuple[float, float]
    duration_seconds: float
    sample_rate_hz: int = 48_000
    bit_depth: int = 24
    noise_mode: NoiseMode = "random"
    seed: int | str | None = None
    slope_target_db_per_octave: float = -3.0
    rms_tolerance_db: float = 0.1
    slope_tolerance_db_per_octave: float = 0.5
    silent_channel_max_dbfs: float = -120.0


@dataclass(frozen=True)
class GenerationRequest:
    profile_id: str
    layout_id: str
    output_directory: Path
    target_channels: tuple[str, ...] = ()
    duration_seconds: float | None = None
    overwrite: bool = False
    seed: int | str | None = None
    noise_mode: NoiseMode | None = None
    custom_layout: SpeakerLayout | None = None
    summary_name: str = "SUMMARY.md"
    validation_name: str = "validation-data.json"
    companion_playback: CompanionPlaybackMode = "none"

    def __post_init__(self) -> None:
        if self.companion_playback not in {"none", "video-container"}:
            raise ValidationError("companion_playback must be 'none' or 'video-container'")


@dataclass
class ReferenceTrack:
    path: Path
    profile_id: str
    layout_id: str
    target_channel_id: str
    channel_count: int
    active_channel_index: int
    silent_channel_indices: list[int]
    noise_specification: NoiseSpecification
    validation_result: dict[str, Any]


@dataclass
class CompanionPlaybackFile:
    path: Path
    source_reference_track_path: Path
    purpose: Literal["media_browser_compatibility"]
    container: str
    placeholder_video: bool
    audio_encoding: str
    status: Literal["created", "failed"]
    error: str | None = None


@dataclass
class GenerationSummary:
    generated_at: str
    request: GenerationRequest
    files: list[ReferenceTrack]
    measurement_method: str
    calibration_guide_path: Path
    warnings: list[str]
    validation_overview: str
    companion_playback_files: list[CompanionPlaybackFile] = field(default_factory=list)


@dataclass
class ValidationData:
    schema_version: str
    request: dict[str, Any]
    tracks: list[dict[str, Any]]
    overall_status: Literal["pass", "fail"]
    artifacts: dict[str, str]
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CalibrationGuide:
    path: Path
    preflight_checklist: tuple[str, ...]
    safe_volume_workflow: tuple[str, ...]
    receiver_setup_steps: tuple[str, ...]
    meter_setup_steps: tuple[str, ...]
    speaker_trim_steps: tuple[str, ...]
    file_use_map: tuple[str, ...]
    troubleshooting: tuple[str, ...]
    fallback_guidance: tuple[str, ...]
