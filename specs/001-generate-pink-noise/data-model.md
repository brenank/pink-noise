# Data Model: Generate Pink Noise

## CalibrationProfile

Represents a named generation use case.

**Fields**
- `id`: Stable profile identifier. Required, unique.
- `display_name`: Human-readable name.
- `purpose`: One of `consumer_speaker`, `subwoofer_lfe_check`,
  `subwoofer_bass_managed`, `full_band_analysis`, `pro_reference`.
- `default_rms_dbfs`: Target RMS level per active channel.
- `default_band_hz`: Lower and upper band limit.
- `default_duration_seconds`: Defaults to 60.
- `min_duration_seconds`: 1.
- `max_duration_seconds`: 3600.
- `noise_mode`: `random`, `periodic`, or user-selectable.
- `measurement_guidance`: Human-readable calibration instructions.
- `warnings`: Profile-specific misuse warnings.
- `validation_thresholds`: Link to the validation tolerances used for generated
  tracks.

**Validation Rules**
- Consumer speaker profile uses 500 Hz-2 kHz and -30 dBFS RMS.
- Subwoofer profiles use 30 Hz-80 Hz and are labeled as direct LFE-channel checks
  or bass-managed sub-system calibration.
- Pro reference profile uses -20 dBFS RMS and is never labeled as the consumer
  default.
- Full-band analysis profile is not labeled as basic SPL trim material.

## SpeakerLayout

Represents a built-in or custom channel map.

**Fields**
- `id`: Stable layout identifier.
- `display_name`: Human-readable name.
- `channels`: Ordered list of `SpeakerChannel` entries.
- `channel_mask`: WAVE speaker-position bit mask. Built-ins use explicit masks;
  custom direct-output layouts use `0`.
- `channel_mask_policy`: `speaker_positions` or `directout`.
- `is_builtin`: Boolean.
- `source`: `built_in` or `custom`.

**Validation Rules**
- Built-in layouts include 2.0, 2.1, 3.1, 5.1, 7.1, 5.1.2, 5.1.4, 7.1.2, and
  7.1.4.
- Custom layouts require at least one channel.
- Channel names must be non-empty and unique within a layout.
- Channel order must be explicit.
- Built-in WAVE channel order follows the WAVE speaker-position bit order used by
  WAVE_FORMAT_EXTENSIBLE.
- `channel_mask_policy: speaker_positions` requires a channel-mask bit for each
  channel. `directout` records channel order without speaker-position metadata.

## SpeakerChannel

Represents one output position in a layout.

**Fields**
- `id`: Stable channel identifier, unique within layout.
- `label`: User-facing channel name.
- `role`: One of `main`, `surround`, `height`, `lfe`, `subwoofer`, `custom`.
- `order`: Zero-based channel index in the multichannel file.
- `is_low_frequency`: Boolean.

**Validation Rules**
- LFE/subwoofer channels cannot use speaker-band calibration profiles without a
  warning or rejection.
- Main, surround, and height channels use speaker-band calibration by default.

## NoiseSpecification

Defines signal requirements for a generated track.

**Fields**
- `rms_dbfs`: Target RMS level.
- `band_hz`: Lower and upper band limit.
- `duration_seconds`: Requested duration.
- `sample_rate_hz`: 48000 by default.
- `bit_depth`: 24 by default.
- `noise_mode`: `random` or `periodic`.
- `seed`: Deterministic repeatability value.
- `periodic_period_seconds`: 4 seconds for periodic mode, absent/null for random.
- `slope_target_db_per_octave`: -3 dB per octave target.
- `rms_tolerance_db`: +/-0.1 dB.
- `slope_tolerance_db_per_octave`: +/-0.5 dB per octave.
- `silent_channel_max_dbfs`: -120 dBFS.

**Validation Rules**
- Output must not clip.
- Duration must be from 1 to 3600 seconds inclusive.
- RMS must be within tolerance.
- Pink-noise slope must be within tolerance.
- Inactive channels must remain below the silence threshold.
- Periodic noise duration must be a whole multiple of the 4-second period.

## GenerationRequest

Captures a user request to generate reference material.

**Fields**
- `profile_id`: Requested calibration profile.
- `layout_id`: Built-in layout ID or custom layout reference.
- `target_channels`: Optional subset of channels; defaults to all applicable
  channels.
- `duration_seconds`: Optional override.
- `output_directory`: Destination path.
- `overwrite`: Explicit overwrite permission.
- `seed`: Optional repeatability override.
- `custom_layout`: Optional custom `SpeakerLayout`.
- `companion_playback`: Optional companion playback export mode. Defaults to
  `none`; `video-container` requests one playback-compatibility copy per selected
  reference track.

**Validation Rules**
- Output directory must be writable.
- Existing files are not overwritten unless `overwrite` is true.
- Requested profile must be compatible with each target channel or produce a clear
  warning/rejection.
- Companion playback export requires all source reference tracks to pass validation
  first.

## ReferenceTrack

Represents one generated WAV file.

**Fields**
- `path`: Output file path.
- `profile_id`: Calibration profile used.
- `layout_id`: Layout used.
- `target_channel_id`: Active target channel.
- `channel_count`: Number of channels in the file.
- `active_channel_index`: Active channel index.
- `silent_channel_indices`: All inactive channel indices.
- `noise_specification`: Applied `NoiseSpecification`.
- `validation_result`: Result summary.

**Validation Rules**
- Exactly one active target channel for channel-isolated tracks.
- All inactive channels contain digital silence below -120 dBFS.
- File name identifies profile, layout, channel, RMS level, and bandwidth.
- File names follow
  `{profile}__{layout}__ch{index}-{channel}__{band}hz__{rms}dbfs__{mode}.wav`
  and stay under 120 characters.

## CompanionPlaybackFile

Represents an optional media-player-compatible copy of a validated reference track.

**Fields**
- `path`: Output file path.
- `source_reference_track_path`: Source `ReferenceTrack` path.
- `purpose`: `media_browser_compatibility`.
- `container`: Video-container format used for browsing compatibility.
- `placeholder_video`: Boolean indicating that video content is non-calibration
  placeholder media.
- `audio_encoding`: Lossless audio encoding used inside the container.
- `status`: `created` or `failed`.
- `error`: Failure message when creation fails.

**Validation Rules**
- Must be generated only from a `ReferenceTrack` whose `validation_result` is pass.
- Must preserve the selected reference track's duration and channel count.
- Must use lossless audio and must not be described as a separate calibration
  signal.
- File name must identify the source track and companion playback purpose.

## GenerationSummary

Human-readable report for calibration sessions.

**Fields**
- `generated_at`: Timestamp.
- `request`: Summary of the `GenerationRequest`.
- `files`: List of generated `ReferenceTrack` entries.
- `measurement_method`: Intended SPL and meter guidance.
- `calibration_guide_path`: Link to the standalone beginner guide.
- `companion_playback_files`: Optional list of `CompanionPlaybackFile` entries.
- `warnings`: Playback-chain and calibration warnings.
- `validation_overview`: Pass/fail summary.

**Validation Rules**
- Summary must link to `CALIBRATION-GUIDE.md` for every successful output set.
- Summary must label companion playback files as compatibility copies and identify
  their source reference tracks.

## ValidationData

Machine-readable audit record.

**Fields**
- `schema_version`: Contract version.
- `request`: Full request data.
- `tracks`: Per-track measurements and validation outcomes.
- `companion_playback_files`: Optional list of companion file paths, source tracks,
  audio encoding, container, and compatibility purpose.
- `routing_intent`, `channel_mask`, WAV format metadata, validation thresholds,
  and noise-mode details are included for auditability.
- `overall_status`: `pass` or `fail`.
- `errors`: Validation or generation failures.

## CalibrationGuide

Standalone beginner-facing Markdown document generated with each successful output
set.

**Fields**
- `path`: Always `CALIBRATION-GUIDE.md` within the output directory.
- `preflight_checklist`: Steps to complete before playback at reference volume.
- `safe_volume_workflow`: Instructions to start low, confirm routing, and only then
  raise playback to reference volume.
- `receiver_setup_steps`: Plain-language instructions to disable processing,
  upmixing, normalization, and other modes that alter levels or routing.
- `meter_setup_steps`: Instructions for SPL meter placement and C-weighted Slow
  setup.
- `speaker_trim_steps`: Numbered workflow to play one speaker file at a time and
  adjust trims to 75 dB SPL.
- `file_use_map`: Explanation of speaker trim, direct LFE check, bass-managed
  sub-system, full-band analysis, and pro reference files.
- `troubleshooting`: Common mistakes and corrective actions.
- `fallback_guidance`: Direction to use AVR internal tones or a measurement workflow
  when direct multichannel routing cannot be confirmed.

**Validation Rules**
- Must be generated for every successful output set.
- Must be linked from `GenerationSummary`.
- Must define unavoidable calibration terms in plain language.
- Must put safety and misuse warnings before any step that raises playback to
  reference volume.

## State Transitions

```text
GenerationRequest
  -> validated request
  -> generated signal arrays
  -> written ReferenceTrack files
  -> post-write validation
  -> optional CompanionPlaybackFile export
  -> GenerationSummary + ValidationData + CalibrationGuide
  -> ready outputs
```

Invalid input, unsafe clipping, failed tolerance checks, or overwrite conflicts
transition to an error state and must not be reported as ready outputs. Requested
companion playback export failures also transition to an error state, but only
after the primary reference tracks have been generated and validated.
