# Tasks: Generate Pink Noise

**Input**: Design documents from `/specs/001-generate-pink-noise/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Automated tests are REQUIRED by the project constitution and feature
specification. Write tests before implementation tasks in each phase and confirm
they fail for the intended reason.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing. Source-file tasks follow the plan structure:
`cli.py` and `__main__.py` are thin entry points, `app.py` orchestrates workflows,
`domain/` owns profiles/layouts/models, `audio/` owns signal/WAV/validation, and
`output/` owns reports and guide content.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python package, test harness, and source tree.

- [X] T001 Create Python package metadata with Python >=3.11, NumPy >=2.4.6,<2.5, pytest >=9.1,<10, jsonschema >=4.26,<5, hatchling >=1.30.1,<2, build >=1.5,<2, and `pink-noise = "pink_noise.cli:main"` in pyproject.toml
- [X] T002 Create package directories and empty package files in src/pink_noise/__init__.py, src/pink_noise/__main__.py, src/pink_noise/cli.py, src/pink_noise/app.py, src/pink_noise/domain/__init__.py, src/pink_noise/audio/__init__.py, and src/pink_noise/output/__init__.py
- [X] T003 [P] Create planned test directories and package markers in tests/contract/.gitkeep, tests/integration/.gitkeep, tests/unit/domain/.gitkeep, tests/unit/audio/.gitkeep, and tests/unit/output/.gitkeep
- [X] T004 [P] Configure pytest test discovery and warning behavior for tests/ in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish contracts, domain rules, audio primitives, and validation
helpers that every user story depends on.

**CRITICAL**: No user story work begins until this phase is complete.

### Contract and Schema Tests

- [X] T005 [P] Add validation-data schema contract tests for required request, track, and artifact fields in tests/contract/test_validation_schema.py
- [X] T006 [P] Add CLI contract tests for argument parsing, success text, non-zero error behavior, and `python -m pink_noise` delegation in tests/contract/test_cli_contract.py
- [X] T007 [P] Add custom layout JSON Schema contract tests for `kind`, `schema_version`, ordered channels, roles, aliases, and `channel_mask_policy` in tests/contract/test_custom_layout_schema.py

### Contract and Schema Implementation

- [X] T008 Update validation report schema with routing intent, channel mask, WAV format metadata, validation thresholds, and noise-mode details in specs/001-generate-pink-noise/contracts/validation-data.schema.json
- [X] T009 Add custom layout JSON Schema Draft 2020-12 contract in specs/001-generate-pink-noise/contracts/custom-layout.schema.json
- [X] T010 Update CLI contract with JSON custom layout format, `schema_version`, `kind`, `channel_mask_policy`, and periodic duration behavior in specs/001-generate-pink-noise/contracts/cli.md
- [X] T011 Update data model with channel masks, WAVE speaker positions, `channel_mask_policy`, periodic period metadata, filename convention, and validation thresholds in specs/001-generate-pink-noise/data-model.md

### Domain Tests

- [X] T012 [P] Add domain model tests for CalibrationProfile, SpeakerLayout, SpeakerChannel, NoiseSpecification, GenerationRequest, ReferenceTrack, GenerationSummary, ValidationData, and CalibrationGuide in tests/unit/domain/test_models.py
- [X] T013 [P] Add built-in layout tests for 2.0, 2.1, 3.1, 5.1, 7.1, 5.1.2, 5.1.4, 7.1.2, 7.1.4 channel order and WAVE channel masks in tests/unit/domain/test_layouts.py
- [X] T014 [P] Add calibration profile tests for consumer-speaker, subwoofer-lfe-check, subwoofer-bass-managed, full-band-analysis, and pro-reference defaults in tests/unit/domain/test_profiles.py

### Domain Implementation

- [X] T015 Implement typed domain entities and validation errors in src/pink_noise/domain/models.py
- [X] T016 Implement built-in layouts, channel IDs, WAVE speaker positions, channel masks, and custom layout parsing in src/pink_noise/domain/layouts.py
- [X] T017 Implement calibration profile definitions, compatibility checks, default bands, RMS levels, warnings, and duration bounds in src/pink_noise/domain/profiles.py

### Audio Tests

- [X] T018 [P] Add pink-noise generator tests for deterministic random mode, 1/sqrt(f) shaping, RMS normalization, band limits, and seeded repeatability in tests/unit/audio/test_generator.py
- [X] T019 [P] Add periodic pink-noise tests for 4-second period, 192000 samples at 48 kHz, 0.25 Hz bin spacing, seamless tiling, and rejection of non-period-multiple durations in tests/unit/audio/test_generator.py
- [X] T020 [P] Add WAV writer tests for WAVE_FORMAT_EXTENSIBLE headers, PCM GUID, channel masks, interleaved order, signed packed 24-bit samples, and inactive-channel zero bytes in tests/unit/audio/test_wav.py
- [X] T021 [P] Add validation tests for post-write PCM decoding, RMS tolerance, clipping, crest factor, silence threshold, bandwidth, and pink-slope regression in tests/unit/audio/test_validation.py

### Audio Implementation

- [X] T022 Implement random and periodic FFT pink-noise generation using NumPy in src/pink_noise/audio/generator.py
- [X] T023 Implement WAVE_FORMAT_EXTENSIBLE 24-bit PCM writer and PCM decoder/readback helper in src/pink_noise/audio/wav.py
- [X] T024 Implement post-write validation for RMS, peak, crest factor, clipping, bandwidth, channel isolation, silence, and spectral slope in src/pink_noise/audio/validation.py

**Checkpoint**: Foundation complete. Domain contracts, audio primitives, WAV
serialization, and validation are ready for user-story workflows.

---

## Phase 3: User Story 1 - Generate Consumer Speaker-Level Calibration Tracks (Priority: P1) MVP

**Goal**: Generate consumer speaker-trim reference tracks for a selected home
theater layout, with one active channel per file, 500 Hz-2 kHz pink noise, -30 dBFS
RMS, validation reports, and 75 dB C-weighted Slow measurement guidance.

**Independent Test**: Generate a 5.1 consumer-speaker set and verify the non-LFE
speaker tracks use 500 Hz-2 kHz, -30 dBFS RMS, one active target channel, silent
inactive channels, WAVE channel metadata, and 75 dB C-weighted Slow guidance.

### Tests for User Story 1

- [X] T025 [P] [US1] Add CLI contract test for 5.1 consumer-speaker generation success output and artifact paths in tests/contract/test_cli_contract.py
- [X] T026 [P] [US1] Add application unit tests for consumer-speaker request validation, target-channel expansion, overwrite protection, and artifact naming in tests/unit/test_app.py
- [X] T027 [P] [US1] Add report unit tests for consumer speaker summaries with profile, layout, channel mapping, RMS, bandwidth, seed, validation results, and guide link in tests/unit/output/test_reports.py
- [X] T028 [US1] Add end-to-end 5.1 consumer-speaker integration test covering generated WAVs, summary, validation JSON, and CALIBRATION-GUIDE.md presence in tests/integration/test_generate_reference_set.py

### Implementation for User Story 1

- [X] T029 [US1] Implement consumer-speaker generation orchestration, request validation, overwrite handling, and artifact planning in src/pink_noise/app.py
- [X] T030 [US1] Implement consumer-readable WAV filename generation using `{profile}__{layout}__ch{index}-{channel}__{band}hz__{rms}dbfs__{mode}.wav` in src/pink_noise/app.py
- [X] T031 [US1] Implement Markdown summary rendering for consumer speaker calibration outputs in src/pink_noise/output/reports.py
- [X] T032 [US1] Implement validation JSON rendering from post-write validation results in src/pink_noise/output/reports.py
- [X] T033 [US1] Implement argparse CLI `pink-noise generate` command, status output, and non-zero error paths in src/pink_noise/cli.py
- [X] T034 [US1] Implement `python -m pink_noise` delegation to the CLI main function in src/pink_noise/__main__.py

**Checkpoint**: User Story 1 is independently functional and can produce validated
consumer speaker-calibration files.

---

## Phase 4: User Story 2 - Follow Beginner Calibration Instructions (Priority: P2)

**Goal**: Generate plain-language beginner guidance that lets a consumer safely use
the files, identify the right material, avoid common playback-chain mistakes, and
fall back to AVR tones or measurement workflows when routing cannot be confirmed.

**Independent Test**: Open the generated `CALIBRATION-GUIDE.md` and confirm it
contains preflight, safe-volume setup, direct routing confirmation, receiver/player
settings, SPL meter setup, 75 dB trim workflow, file-use map, subwoofer caveats,
troubleshooting, and fallback guidance before reference-volume instructions.

### Tests for User Story 2

- [X] T035 [P] [US2] Add calibration guide content and ordering tests for preflight, low-volume start, direct-routing confirmation, C-weighted Slow setup, 75 dB workflow, and fallback guidance in tests/unit/output/test_guide.py
- [X] T036 [P] [US2] Add guide integration assertions that consumer generation writes CALIBRATION-GUIDE.md and links it from the summary in tests/integration/test_generate_reference_set.py
- [X] T037 [P] [US2] Add guide usability acceptance checklist test for required file-use map, advanced-file warnings, and troubleshooting entries in tests/unit/output/test_guide.py

### Implementation for User Story 2

- [X] T038 [US2] Implement beginner guide rendering with preflight, safety, receiver setup, meter setup, speaker trim, file-use map, troubleshooting, and fallback sections in src/pink_noise/output/guide.py
- [X] T039 [US2] Integrate CALIBRATION-GUIDE.md writing and summary linking into successful generation workflow in src/pink_noise/app.py
- [X] T040 [US2] Add guide review checklist artifact for the one lightweight novice walkthrough in specs/001-generate-pink-noise/checklists/guide-usability.md

**Checkpoint**: User Story 2 is independently verifiable through generated guide
content and guide-linked consumer outputs.

---

## Phase 5: User Story 3 - Generate Subwoofer Calibration Material (Priority: P3)

**Goal**: Generate low-frequency subwoofer material that clearly separates direct
LFE checks from bass-managed sub-system checks and prevents speaker-band/subwoofer
profile misuse.

**Independent Test**: Generate direct LFE and bass-managed sub-system material for
5.1, then verify 30 Hz-80 Hz band limits, routing intent, one-active-channel
tracks, direct-LFE versus bass-managed labels, and mismatch rejection for LFE with
speaker-band calibration.

### Tests for User Story 3

- [X] T041 [P] [US3] Add profile compatibility tests for LFE, subwoofer, bass-managed main-channel routing, and speaker-band mismatch rejection in tests/unit/domain/test_profiles.py
- [X] T042 [P] [US3] Add subwoofer app tests for direct LFE generation and bass-managed non-LFE low-frequency tracks in tests/unit/test_app.py
- [X] T043 [P] [US3] Add report and guide tests for direct LFE labels, bass-managed warnings, longer averaging guidance, and sweep/integration caveats in tests/unit/output/test_reports.py
- [X] T044 [US3] Add integration tests for subwoofer-lfe-check and subwoofer-bass-managed quickstart scenarios in tests/integration/test_generate_reference_set.py

### Implementation for User Story 3

- [X] T045 [US3] Implement subwoofer direct LFE and bass-managed target-channel expansion rules in src/pink_noise/app.py
- [X] T046 [US3] Implement subwoofer profile warnings, mismatch errors, and low-frequency measurement guidance in src/pink_noise/domain/profiles.py
- [X] T047 [US3] Extend report and guide output with direct LFE labels, bass-managed routing semantics, low-frequency averaging warning, and sub integration caveats in src/pink_noise/output/reports.py
- [X] T048 [US3] Extend beginner guide subwoofer sections for individual sub checks, summed sub-system level, bass management confirmation, and sweep-based integration caveats in src/pink_noise/output/guide.py

**Checkpoint**: User Story 3 is independently functional for subwoofer calibration
material and rejects unsafe/mismatched speaker-band usage.

---

## Phase 6: User Story 4 - Produce Analysis and Pro Reference Presets (Priority: P4)

**Goal**: Generate clearly labeled full-band analysis and pro reference material,
including periodic pink noise for analyzer workflows and -20 dBFS pro/studio
reference files separated from consumer AVR defaults.

**Independent Test**: Generate full-band analysis with periodic mode and pro
reference material, then verify output labels, RMS level, bandwidth, noise type,
periodic metadata, and warnings that these are not normal 75 dB consumer trim
files.

### Tests for User Story 4

- [X] T049 [P] [US4] Add analysis and pro profile tests for full-band limits, -20 dBFS pro RMS, labeling, and consumer-default separation in tests/unit/domain/test_profiles.py
- [X] T050 [P] [US4] Add periodic generation app tests for whole-period duration enforcement, analyzer metadata, and seeded repeatability in tests/unit/test_app.py
- [X] T051 [P] [US4] Add report tests for analysis/RTA warnings, pro reference warnings, and periodic noise metadata in tests/unit/output/test_reports.py
- [X] T052 [US4] Add integration test for full-band-analysis periodic quickstart scenario and pro-reference generation in tests/integration/test_generate_reference_set.py

### Implementation for User Story 4

- [X] T053 [US4] Implement full-band-analysis and pro-reference workflow handling in src/pink_noise/app.py
- [X] T054 [US4] Extend profile definitions for full-band analysis and pro reference labeling, RMS defaults, warnings, and allowed noise modes in src/pink_noise/domain/profiles.py
- [X] T055 [US4] Extend reports with analysis/RTA labels, pro/studio reference labels, RMS reference separation, and periodic-mode metadata in src/pink_noise/output/reports.py

**Checkpoint**: User Story 4 is independently functional for advanced analysis and
pro reference workflows.

---

## Phase 7: User Story 1 Addendum - Optional Companion Playback Export

**Goal**: Extend the primary generation workflow so users can optionally create
media-player-compatible companion video-container files from validated WAV
reference tracks when a media browser hides audio-only files.

**Independent Test**: Generate a single center-channel consumer-speaker track with
`--companion-playback video-container`, verify the WAV is generated and validated
first, exactly one companion playback file is created from that WAV, the summary
labels it as a compatibility copy, and validation JSON records its source track,
container, lossless audio encoding, and compatibility purpose.

### Tests for User Story 1 Addendum

- [X] T063 [P] [US1] Add validation-data schema contract tests for `request.companion_playback`, root `companion_playback_files`, per-track `companion_playback_files`, and `artifacts.companion_playback_paths` in tests/contract/test_validation_schema.py
- [X] T064 [P] [US1] Add CLI contract tests for `--companion-playback none`, `--companion-playback video-container`, companion count success output, invalid choice rejection, and exporter failure behavior in tests/contract/test_cli_contract.py
- [X] T065 [P] [US1] Add domain model tests for `CompanionPlaybackFile` fields and `GenerationRequest.companion_playback` default/allowed values in tests/unit/domain/test_models.py
- [X] T066 [P] [US1] Add companion exporter unit tests for FFmpeg command construction, placeholder video settings, lossless audio encoding, source WAV path handling, missing executable errors, and non-zero exporter failures in tests/unit/output/test_companion.py
- [X] T067 [P] [US1] Add application unit tests for companion output path planning, overwrite conflict detection, post-validation export ordering, and companion metadata passed to reports in tests/unit/test_app.py
- [X] T068 [US1] Add integration coverage for the quickstart `--companion-playback video-container` scenario with a controlled companion exporter in tests/integration/test_generate_reference_set.py

### Implementation for User Story 1 Addendum

- [X] T069 [US1] Extend `GenerationRequest`, `GenerationResult`, `ValidationData`, and add `CompanionPlaybackFile` domain data in src/pink_noise/domain/models.py
- [X] T070 [US1] Implement optional companion playback exporter with FFmpeg executable discovery, command construction, subprocess execution, and actionable errors in src/pink_noise/output/companion.py
- [X] T071 [US1] Add companion playback filename planning and overwrite conflict detection alongside WAV, summary, validation, and guide artifacts in src/pink_noise/app.py
- [X] T072 [US1] Integrate companion playback export after each source WAV passes validation and before summary/validation JSON writing in src/pink_noise/app.py
- [X] T073 [US1] Extend summary and validation JSON rendering with companion file path, source reference track, container, lossless audio encoding, and compatibility-purpose metadata in src/pink_noise/output/reports.py
- [X] T074 [US1] Add `--companion-playback <none|video-container>` parsing, request mapping, success count output, and error handling to the generate command in src/pink_noise/cli.py
- [X] T075 [US1] Update generated-artifact documentation with the optional companion playback prerequisite, CLI example, and compatibility-copy warning in README.md

**Checkpoint**: Optional companion playback export is independently functional for
the primary generation workflow without replacing validated WAV reference files.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, validation, and quality gates across all user
stories.

- [X] T056 [P] Add quickstart validation notes for WAVE_FORMAT_EXTENSIBLE channel masks, custom-layout schema validation, and periodic duration behavior in specs/001-generate-pink-noise/quickstart.md
- [X] T057 [P] Add package README with install, CLI examples, safe playback warning, and generated artifact overview in README.md
- [X] T058 Run formatter and lint-equivalent checks for Python and Markdown files documented in pyproject.toml
- [X] T059 Run full pytest suite and fix failures across tests/contract, tests/unit, and tests/integration
- [X] T060 Run quickstart scenarios manually or through integration fixtures and record results in specs/001-generate-pink-noise/checklists/requirements.md
- [X] T061 Verify generated filenames stay under 120 characters and include profile, layout, channel, band, RMS, and mode in tests/unit/test_app.py
- [X] T062 Verify no generated WAV, FLAC, MP3, out/, outputs/, or generated/ artifacts are tracked by git using .gitignore
- [X] T076 Run companion playback contract, unit, and integration tests in tests/contract/test_cli_contract.py, tests/contract/test_validation_schema.py, tests/unit/output/test_companion.py, tests/unit/test_app.py, tests/integration/test_generate_reference_set.py plus compileall checks documented in pyproject.toml
- [X] T077 [P] Verify companion playback documentation remains generic and contains no player/vendor-specific references in specs/001-generate-pink-noise/spec.md, specs/001-generate-pink-noise/quickstart.md, specs/001-generate-pink-noise/contracts/cli.md, and README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks every user story.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 output, but guide content remains independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational; can proceed after US1 CLI/orchestration exists.
- **User Story 4 (Phase 6)**: Depends on Foundational; can proceed after US1 CLI/orchestration exists.
- **User Story 1 Addendum (Phase 7)**: Depends on US1 and Foundational; can be
  implemented after the primary generation/reporting workflow exists.
- **Polish (Phase 8)**: Depends on all selected stories and the companion playback
  addendum.

### User Story Dependencies

- **US1**: MVP and primary CLI/output path.
- **US2**: Requires guide integration into successful generation; content tests can start after Foundational.
- **US3**: Reuses app/CLI/report paths from US1 and extends them for subwoofer profiles.
- **US4**: Reuses app/CLI/report paths from US1 and extends them for analysis/pro profiles.
- **US1 Addendum**: Reuses US1 app/CLI/report paths and adds optional companion
  playback copies after source WAV validation.

### Within Each User Story

- Tests precede implementation.
- Domain/profile/layout rules precede app orchestration when story-specific rules are needed.
- App orchestration precedes CLI integration when command behavior changes.
- Output/report/guide rendering precedes integration fixture completion.

---

## Parallel Opportunities

- Setup T003 and T004 can run after T001/T002 decisions are understood.
- Foundation contract tests T005-T007 can run in parallel.
- Foundation domain tests T012-T014 can run in parallel.
- Foundation audio tests T018-T021 can run in parallel.
- US1 tests T025-T027 can run in parallel before T028.
- US2 tests T035-T037 can run in parallel.
- US3 tests T041-T043 can run in parallel before T044.
- US4 tests T049-T051 can run in parallel before T052.
- Companion addendum tests T063-T067 can run in parallel before T068.
- Companion implementation tasks T070 and T073 can proceed in parallel after T069.
- Polish documentation tasks T056, T057, and T077 can run in parallel.

## Parallel Example: User Story 1

```bash
Task: "T025 [P] [US1] Add CLI contract test for 5.1 consumer-speaker generation success output and artifact paths in tests/contract/test_cli_contract.py"
Task: "T026 [P] [US1] Add application unit tests for consumer-speaker request validation, target-channel expansion, overwrite protection, and artifact naming in tests/unit/test_app.py"
Task: "T027 [P] [US1] Add report unit tests for consumer speaker summaries with profile, layout, channel mapping, RMS, bandwidth, seed, validation results, and guide link in tests/unit/output/test_reports.py"
```

## Parallel Example: User Story 2

```bash
Task: "T035 [P] [US2] Add calibration guide content and ordering tests for preflight, low-volume start, direct-routing confirmation, C-weighted Slow setup, 75 dB workflow, and fallback guidance in tests/unit/output/test_guide.py"
Task: "T037 [P] [US2] Add guide usability acceptance checklist test for required file-use map, advanced-file warnings, and troubleshooting entries in tests/unit/output/test_guide.py"
```

## Parallel Example: User Story 3

```bash
Task: "T041 [P] [US3] Add profile compatibility tests for LFE, subwoofer, bass-managed main-channel routing, and speaker-band mismatch rejection in tests/unit/domain/test_profiles.py"
Task: "T042 [P] [US3] Add subwoofer app tests for direct LFE generation and bass-managed non-LFE low-frequency tracks in tests/unit/test_app.py"
Task: "T043 [P] [US3] Add report and guide tests for direct LFE labels, bass-managed warnings, longer averaging guidance, and sweep/integration caveats in tests/unit/output/test_reports.py"
```

## Parallel Example: User Story 4

```bash
Task: "T049 [P] [US4] Add analysis and pro profile tests for full-band limits, -20 dBFS pro RMS, labeling, and consumer-default separation in tests/unit/domain/test_profiles.py"
Task: "T050 [P] [US4] Add periodic generation app tests for whole-period duration enforcement, analyzer metadata, and seeded repeatability in tests/unit/test_app.py"
Task: "T051 [P] [US4] Add report tests for analysis/RTA warnings, pro reference warnings, and periodic noise metadata in tests/unit/output/test_reports.py"
```

## Parallel Example: User Story 1 Addendum

```bash
Task: "T063 [P] [US1] Add validation-data schema contract tests for companion playback metadata in tests/contract/test_validation_schema.py"
Task: "T064 [P] [US1] Add CLI contract tests for --companion-playback behavior in tests/contract/test_cli_contract.py"
Task: "T066 [P] [US1] Add companion exporter unit tests in tests/unit/output/test_companion.py"
Task: "T067 [P] [US1] Add application unit tests for companion export planning in tests/unit/test_app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Complete Phase 3 US1.
4. Stop and validate the 5.1 consumer-speaker quickstart scenario.

### Incremental Delivery

1. Deliver US1 consumer speaker calibration as the MVP.
2. Add US2 beginner guide usability and safety support.
3. Add US3 subwoofer direct LFE and bass-managed workflows.
4. Add US4 full-band analysis, periodic mode, and pro reference workflows.
5. Add the US1 companion playback export addendum when media-browser compatibility
   copies are needed.
6. Complete Phase 8 polish and quality gates.

### Notes

- `[P]` tasks touch distinct files or can be completed without depending on another incomplete task.
- Each user story has its own tests and independent acceptance checkpoint.
- Do not begin implementation tasks in a phase until that phase's tests have been written and observed failing for the intended reason.
- Keep generated audio files under ignored output directories and do not commit generated media.
