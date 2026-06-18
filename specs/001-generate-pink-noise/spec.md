# Feature Specification: Generate Pink Noise

**Feature Branch**: `001-generate-pink-noise`

**Created**: 2026-06-18

**Status**: Draft

**Input**: User description: "Build a generation script that can produce lossless pink-noise that will be used for reference material for setting to theater speakers systems to 75db by measuring at reference 0db volume. Will need to support pink noise individually to each channel in any home theater setup. Updated with audiophile calibration guidance: proper pink-noise spectrum, band-limited speaker and subwoofer calibration profiles, consumer AVR reference levels, discrete channel routing, lossless files, and validation reporting."

## Clarifications

### Session 2026-06-18

- Q: Which built-in home theater layouts must be supported for v1? → A: Common consumer presets: 2.0, 2.1, 3.1, 5.1, 7.1, 5.1.2, 5.1.4, 7.1.2, 7.1.4, plus custom layouts.
- Q: How should subwoofer calibration material be routed? → A: Provide separate LFE-channel check and bass-managed sub-system calibration outputs.
- Q: What deliverables should generation produce? → A: Reference WAV files plus a human summary and machine-readable validation data.
- Q: What default track duration should generated material use? → A: 60-second default tracks for all profiles, with custom duration allowed.
- Q: What validation tolerances should generated files use? → A: Calibration-grade validation: no clipping, RMS within +/-0.1 dB, pink slope within +/-0.5 dB/octave, silent channels below -120 dBFS.
- Q: How should beginner instructions be delivered? → A: Generate a separate CALIBRATION-GUIDE.md file and link it from the summary.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Consumer Speaker-Level Calibration Tracks (Priority: P1)

An audio calibrator selects a home theater speaker layout and generates
calibration-grade pink-noise tracks for level matching each main, surround, and
height speaker to 75 dB SPL using a C-weighted, Slow measurement at the main
listening position with the playback system set to reference 0 dB master volume.

**Why this priority**: This is the core use case: reliable manual speaker trim
calibration for consumer home theater systems without relying on compressed or
unknown test material.

**Independent Test**: Generate the default consumer calibration set for a 5.1 layout
and verify that each non-subwoofer speaker track uses 500 Hz-2 kHz band-limited
pink noise at the documented RMS reference level, contains signal only in the
target channel, and labels the intended 75 dB C-weighted Slow measurement method.

**Acceptance Scenarios**:

1. **Given** a 5.1 layout selection, **When** the calibrator generates consumer
   level-calibration material, **Then** the output contains separate lossless tracks
   for left, center, right, left surround, right surround, and LFE/subwoofer.
2. **Given** a generated center-channel calibration track, **When** the track is
   inspected, **Then** 500 Hz-2 kHz pink noise is present only in the center channel
   and every other channel is digital silence.
3. **Given** generated speaker calibration material, **When** the calibrator reviews
   the summary, **Then** it states the intended use: set each speaker to 75 dB SPL,
   C-weighted, Slow, at the main listening position with master volume at 0 dB.

---

### User Story 2 - Follow Beginner Calibration Instructions (Priority: P2)

A consumer home theater user with little audio-calibration experience opens the
generated material and follows a plain-language guide that explains what to play,
what to set on the receiver/player, how to place and configure the SPL meter, how
to adjust speaker trims, and when not to use a given file.

**Why this priority**: The generated files can produce bad calibration results if a
consumer plays them through the wrong path, uses the wrong AVR mode, changes volume
normalization, or misunderstands speaker versus subwoofer files.

**Independent Test**: Give the generated files and guide to a user who is familiar
with their receiver but not with calibration terminology, then verify they can set
up the playback chain, identify the correct channel file, perform a single speaker
trim check, and avoid subwoofer/analysis files without extra documentation.

**Acceptance Scenarios**:

1. **Given** generated consumer calibration material, **When** the user opens the
   beginner guide, **Then** it provides a numbered workflow for disabling processing,
   setting reference 0 dB master volume only when ready, placing the SPL meter at
   ear height, selecting C-weighted Slow, playing one file at a time, and adjusting
   each speaker trim to 75 dB SPL.
2. **Given** the user is about to play calibration material, **When** they read the
   guide, **Then** it instructs them to start at a low volume, confirm only the
   intended speaker is playing, and stop if multiple speakers play unexpectedly.
3. **Given** the user reaches subwoofer material, **When** they read the guide,
   **Then** it explains in plain language that subwoofer level checks are separate
   from full sub integration, phase, delay, and crossover tuning.
4. **Given** the user opens generated output files, **When** they read filenames and
   the guide, **Then** they can identify which files are for normal 75 dB speaker
   trim, which are for subwoofer checks, and which are advanced analysis/pro files.

---

### User Story 3 - Generate Subwoofer Calibration Material (Priority: P3)

An installer generates low-frequency pink-noise material for subwoofer level
matching and can distinguish LFE-channel checks, bass-managed sub-system
calibration, individual sub checks, and final summed sub-system calibration.

**Why this priority**: Subwoofers cannot use the same 500 Hz-2 kHz signal as
speakers, and multi-sub systems need different handling from individual speaker
channels.

**Independent Test**: Generate subwoofer calibration material and verify that it is
low-frequency band-limited, clearly separates LFE-channel check files from
bass-managed sub-system calibration files, and includes guidance for individual sub
checks and final summed sub-system level matching.

**Acceptance Scenarios**:

1. **Given** an LFE/subwoofer target channel, **When** calibration material is
   generated, **Then** the track uses 30 Hz-80 Hz band-limited pink noise by default
   and is labeled as subwoofer-specific material.
2. **Given** a bass-managed sub-system calibration request, **When** material is
   generated, **Then** the output is labeled as using bass management rather than
   direct LFE-channel routing.
3. **Given** a multi-subwoofer setup, **When** the calibrator reviews the summary,
   **Then** it distinguishes individual subwoofer level checks from final summed
   sub-system calibration against the main channels.
4. **Given** a request to use the speaker-calibration band for a subwoofer track,
   **When** generation is requested, **Then** the system rejects or warns against the
   mismatch and recommends the subwoofer calibration profile.

---

### User Story 4 - Produce Analysis and Pro Reference Presets (Priority: P4)

An advanced calibrator generates additional reference material for response
analysis or pro/studio workflows while keeping those files clearly separate from
consumer 75 dB speaker-trim calibration tracks.

**Why this priority**: Audiophile users may want full-band or periodic pink noise
for analysis, and professional workflows may use a different RMS reference level,
but those signals must not be confused with consumer AVR trim tones.

**Independent Test**: Generate the analysis and pro presets and verify that each
output is labeled with its intended use, RMS reference level, bandwidth, noise type,
and warnings about measurement limitations.

**Acceptance Scenarios**:

1. **Given** the full-band analysis preset, **When** material is generated, **Then**
   the output is labeled for analysis/RTA workflows rather than basic SPL trim
   matching.
2. **Given** the pro reference preset, **When** material is generated, **Then** the
   output uses a -20 dBFS RMS reference level and labels the preset as a
   pro/studio-style reference, not the consumer AVR default.
3. **Given** a periodic pink-noise selection, **When** material is generated, **Then**
   the summary labels it for analyzer/RTA workflows and records the selected
   analyzer-friendly settings.

---

### Edge Cases

- A layout contains duplicate, unknown, empty, or ambiguous channel names.
- The requested output destination already contains files with matching names.
- A generated track would contain signal in more than one active channel.
- A player or playback chain might downmix, upmix, normalize, EQ, or otherwise alter
  the file before it reaches the intended speaker.
- A target channel is LFE/subwoofer and the user requests a speaker-calibration
  band.
- A custom layout includes more channels than common consumer layouts.
- A user requests a lossy output format for reference material.
- A requested RMS level, duration, bandwidth, or calibration metadata value falls
  outside supported bounds.
- Low-frequency random noise readings fluctuate during short measurement windows.
- A consumer user attempts to play files through a streaming service, wireless
  casting path, TV audio mode, soundbar upmixer, or AVR listening mode that changes
  channel routing or level.
- A user starts playback at reference volume before confirming routing and safe
  meter setup.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate pink-noise reference material in lossless
  files, with 48 kHz, 24-bit PCM WAV as the primary output format.
- **FR-002**: Generated pink noise MUST follow the standard pink-noise relationship:
  equal energy per octave, 1/f power density, approximately -3 dB per octave or
  -10 dB per decade on a narrow-band spectrum view, and approximately flat readings
  on octave-band or RTA views.
- **FR-003**: The default consumer speaker-calibration profile MUST use 500 Hz-2 kHz
  band-limited pink noise for main, surround, and height speaker level matching.
- **FR-004**: The default consumer speaker-calibration profile MUST use -30 dBFS RMS
  per active channel and label the intended measurement target as 75 dB SPL,
  C-weighted, Slow, at reference 0 dB master volume.
- **FR-005**: The default subwoofer calibration profiles MUST use 30 Hz-80 Hz
  band-limited pink noise and include separately labeled outputs for direct
  LFE-channel checks and bass-managed sub-system calibration.
- **FR-006**: The system MUST support a full-band analysis profile covering the
  audible full-range reference band and label it as analysis material, not the
  recommended basic SPL trim-matching signal.
- **FR-007**: The system MUST support a pro reference profile using -20 dBFS RMS and
  label it separately from the consumer AVR -30 dBFS RMS profile.
- **FR-008**: The system MUST offer random pink noise for SPL trim checks and
  periodic pink noise for analyzer/RTA workflows.
- **FR-009**: The system MUST support built-in home theater layouts for 2.0, 2.1,
  3.1, 5.1, 7.1, 5.1.2, 5.1.4, 7.1.2, and 7.1.4 systems, including
  low-frequency and height channels where present.
- **FR-010**: Users MUST be able to define a custom channel layout when a built-in
  layout does not match their theater system.
- **FR-011**: The system MUST generate discrete multichannel reference files where
  exactly one target channel contains pink noise and every non-target channel is
  digital silence.
- **FR-012**: The system MUST reject lossy output formats for calibration reference
  material.
- **FR-013**: The system MUST prevent accidental overwrite of existing generated
  material unless the user explicitly confirms replacement.
- **FR-014**: The system MUST reject invalid layouts, duplicate channel names,
  unsupported calibration values, unsafe clipping conditions, and mismatched
  speaker/subwoofer calibration profiles with clear error messages.
- **FR-015**: The system MUST validate each generated track for RMS level, peak
  level, crest factor, clipping status, bandwidth, pink-noise spectral conformance,
  active-channel routing, and inactive-channel silence.
- **FR-015a**: Generated tracks MUST fail validation when clipping is detected, RMS
  level differs from the target by more than +/-0.1 dB, pink-noise slope differs
  from the target by more than +/-0.5 dB per octave, or inactive channels exceed
  -120 dBFS.
- **FR-016**: The system MUST generate a human-readable summary report listing
  generated files, selected profile, channel mapping, active channel, silent
  channels, RMS level, peak level, crest factor, bandwidth, duration, noise type,
  layout, intended measurement method, and a link to the beginner calibration
  guide.
- **FR-017**: The system MUST make generated reference material repeatable for the
  same user-selected settings and record the repeatability setting in the summary.
- **FR-018**: The system MUST warn users that streaming services, lossy files,
  volume normalization, wireless playback paths, unknown DSP, downmixing, and
  upmixing can invalidate calibration results.
- **FR-019**: The system MUST state that subwoofer integration, phase, delay,
  crossover behavior, and room-response diagnosis require measurement sweeps or
  equivalent analysis beyond simple pink-noise level matching.
- **FR-020**: The system MUST document that low-frequency pink-noise measurements
  require longer averaging than speaker-band measurements because readings fluctuate
  more at low frequencies.
- **FR-021**: The system MUST explain the difference between direct LFE-channel
  checks and bass-managed sub-system calibration whenever subwoofer material is
  generated.
- **FR-022**: The system MUST generate machine-readable validation data containing
  the same validation outcomes as the human-readable summary so generated material
  can be audited or regenerated later.
- **FR-023**: The system MUST default generated tracks to 60 seconds for all
  profiles and allow users to choose a custom duration within supported bounds.
- **FR-024**: The system MUST generate a separate `CALIBRATION-GUIDE.md`
  beginner-facing calibration guide alongside every successful output set.
- **FR-025**: The beginner-facing calibration guide MUST include a numbered
  consumer workflow covering safe starting volume, disabling processing/upmixing and
  volume normalization, confirming direct multichannel playback, SPL meter
  placement, C-weighted Slow meter setup, reference 0 dB master volume, one-channel
  playback, trim adjustment to 75 dB SPL, and repeating the process for each
  speaker.
- **FR-026**: The beginner-facing calibration guide MUST include a preflight
  checklist that users complete before playing files at reference volume.
- **FR-027**: The beginner-facing calibration guide MUST include a file-use map that
  separates normal speaker trim files, direct LFE-channel checks, bass-managed
  sub-system files, full-band analysis files, and pro reference files.
- **FR-028**: The beginner-facing calibration guide MUST include a troubleshooting
  section for common consumer mistakes: more than one speaker plays, the wrong
  speaker plays, the AVR shows stereo instead of multichannel input, the meter
  reading jumps around, output is too loud, existing files were played through
  streaming/casting, or subwoofer readings do not match main speakers.
- **FR-029**: The system MUST state that users who cannot confirm direct
  multichannel routing or disable processing should use their AVR's internal test
  tones or a measurement workflow instead of the generated files.

### User Experience Requirements *(include for user-facing features)*

- **UX-001**: The feature MUST use clear home-theater terminology for channels,
  layouts, target SPL, C-weighted Slow measurement, RMS level, reference master
  volume, speaker-band calibration, subwoofer calibration, and analysis profiles.
- **UX-002**: The feature MUST present success and error states that identify the
  selected profile, layout, affected channel, output destination, and corrective
  action.
- **UX-003**: The feature MUST produce a concise generation summary suitable for
  use during speaker calibration at the listening position.
- **UX-004**: The feature MUST visually or textually separate consumer speaker
  calibration, subwoofer calibration, full-band analysis, and pro reference outputs
  so users do not apply the wrong signal to the wrong job.
- **UX-005**: The feature MUST label every generated file with enough information to
  identify profile, layout, channel, RMS level, and bandwidth without opening the
  summary report.
- **UX-006**: The feature MUST write beginner-facing guidance in plain language,
  define unavoidable terms on first use, and avoid assuming the user knows
  calibration jargon.
- **UX-007**: The feature MUST make safety and misuse warnings visible before the
  step that instructs users to raise playback to reference volume.

### Key Entities *(include if feature involves data)*

- **Calibration Profile**: A named use case with default RMS level, bandwidth,
  target channel rules, intended measurement method, and user-facing warnings.
- **Speaker Layout**: A named or custom set of speaker channels with an ordered
  channel map.
- **Speaker Channel**: A single playback position such as left, center, right,
  surround, height, or LFE/subwoofer.
- **Reference Track**: A lossless audio file containing pink noise for one target
  channel and digital silence for all other channels.
- **Noise Specification**: The spectral, level, bandwidth, crest-factor,
  inactive-channel silence, and repeatability criteria used to validate generated
  material.
- **Generation Request**: The user's selected profile, layout, target channels,
  duration, destination, overwrite preference, and optional custom settings.
- **Generation Summary**: A human-readable report describing generated files,
  profile, channel mapping, measurement method, validation outcomes, warnings, and
  repeatability details.
- **Validation Data**: A machine-readable record of generated files, settings,
  channel routing, signal measurements, and validation outcomes.
- **Calibration Guide**: A standalone `CALIBRATION-GUIDE.md` document generated
  with the output set that explains how to use the files safely and correctly in a
  consumer home theater.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every supported layout and selected profile, 100% of declared
  target channels receive exactly one generated reference track.
- **SC-002**: 100% of generated channel-isolated tracks contain audible signal only
  in the intended target channel and digital silence in all other channels.
- **SC-003**: 100% of consumer speaker-calibration tracks use the documented
  500 Hz-2 kHz band and -30 dBFS RMS reference level.
- **SC-004**: 100% of subwoofer calibration tracks use the documented 30 Hz-80 Hz
  band and are labeled as either direct LFE-channel checks or bass-managed
  sub-system calibration.
- **SC-005**: 100% of generated tracks pass validation for no clipping, RMS level
  within +/-0.1 dB, pink-noise slope within +/-0.5 dB per octave, bandwidth,
  active-channel routing, and inactive-channel silence below -120 dBFS before being
  reported as ready.
- **SC-006**: 100% of generated summaries identify the intended measurement method,
  including target SPL where applicable, C-weighted Slow measurement, listening
  position, reference master volume, selected profile, and RMS reference level.
- **SC-007**: 100% of successful generation runs produce both a human-readable
  summary and machine-readable validation data.
- **SC-008**: 100% of generated tracks use the 60-second default duration unless
  the user selects a supported custom duration.
- **SC-009**: 100% of invalid layout, format, clipping, overwrite, or mismatched
  profile requests produce an actionable error or warning that identifies the
  rejected field or risky condition.
- **SC-010**: At least 95% of calibration users can identify the correct file for a
  requested speaker or subwoofer channel from the generated file names and summary
  without additional documentation.
- **SC-011**: At least 90% of consumer users with receiver familiarity but no audio
  calibration experience can complete the preflight checklist and one speaker trim
  check using only the generated calibration guide.
- **SC-012**: 100% of generated output sets include a standalone
  `CALIBRATION-GUIDE.md` linked from the human-readable summary, and the guide
  includes safe-volume setup, direct-routing confirmation, C-weighted Slow meter
  setup, 75 dB trim workflow, subwoofer caveats, advanced-file warnings, and
  troubleshooting for common playback mistakes.

## Assumptions

- "Lossless" means generated material is stored in an uncompressed or lossless audio
  format and is not encoded with lossy compression.
- The primary consumer home theater convention is -30 dBFS RMS pink noise intended
  to read 75 dB SPL with C-weighted Slow measurement at reference 0 dB master
  volume.
- The pro reference preset exists for users who intentionally want a -20 dBFS RMS
  studio-style reference level; it is not the default consumer AVR workflow.
- The generated material provides reference playback files and documentation for
  calibration; the measured SPL depends on the user's playback chain, room, meter,
  speaker trim adjustments, and whether the playback path preserves the file
  without normalization, DSP, downmixing, or upmixing.
- Built-in layouts cover 2.0, 2.1, 3.1, 5.1, 7.1, 5.1.2, 5.1.4, 7.1.2, and 7.1.4;
  custom layouts are available for systems outside those presets.
- The initial target user is an installer, calibrator, or advanced home theater user
  who already has an SPL meter or calibrated microphone and understands reference
  master volume.
- Consumer users may understand their receiver's menus but may not know calibration
  terminology, so generated instructions must explain the workflow without relying
  on audiophile vocabulary.
