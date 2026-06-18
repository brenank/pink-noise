# Implementation Plan: Generate Pink Noise

**Branch**: `001-generate-pink-noise` | **Date**: 2026-06-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-generate-pink-noise/spec.md`

## Summary

Build a local command-line generator for calibration-grade pink-noise reference
material. The tool will generate 48 kHz, 24-bit PCM WAV files with discrete
multichannel routing, one active channel per reference track, profile-specific
band limits and RMS levels, paired human-readable plus machine-readable validation
reports, and a standalone beginner-facing `CALIBRATION-GUIDE.md`. The
implementation will focus on deterministic generation, auditable validation, safe
defaults, plain-language consumer guidance for home theater calibration, and
optional companion playback files for media browsers that hide audio-only files.

## Technical Context

**Language/Version**: Python >=3.11 package support; Python 3.13.14 reference
development/test baseline

**Primary Dependencies**: NumPy >=2.4.6,<2.5 for deterministic signal generation,
FFT analysis, and validation math; Python standard library for CLI parsing, file IO,
JSON, and subprocess execution; local WAVE_FORMAT_EXTENSIBLE writer for 24-bit
multichannel WAV output; optional FFmpeg executable for media-player-compatible
companion video-container files with placeholder video and lossless audio; pytest
>=9.1,<10 and jsonschema >=4.26,<5 for tests/contracts; hatchling >=1.30.1,<2 for
packaging

**Storage**: Local filesystem outputs: WAV reference files, optional companion
video-container playback files, Markdown summary, JSON validation data, standalone
Markdown calibration guide

**Testing**: pytest with unit tests for noise generation, profile validation, channel
routing, WAV metadata/writing, companion playback export command construction and
failure handling, report generation, calibration-guide generation, and end-to-end
CLI fixtures

**Target Platform**: Local macOS/Linux/Windows command-line execution

**Project Type**: Single-project CLI/library package

**Constraints**: Offline-capable; no lossy output; generated files must be
repeatable for identical settings; default outputs must be safe for playback at
reference-volume calibration workflows; validation must fail on clipping, RMS,
spectral-slope, or channel-isolation violations; companion playback files are
optional compatibility copies and must not replace the primary validated WAV files

**Scale/Scope**: Built-in layouts for 2.0, 2.1, 3.1, 5.1, 7.1, 5.1.2, 5.1.4,
7.1.2, and 7.1.4, plus custom layouts; generate 60-second default tracks per
target channel with custom duration support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Code Quality**: PASS. The plan uses a small CLI/library structure with a thin
  command adapter, explicit application orchestration, and responsibility-grouped
  domain, audio, and output modules. New dependencies are limited to NumPy because
  FFT-based generation and validation are central to the feature.
- **Source Structure**: PASS. The source tree makes `cli.py`, `__main__.py`, and
  `app.py` visible at package root, while `domain/`, `audio/`, and `output/`
  separate calibration rules, signal infrastructure, and consumer-facing artifacts.
- **Testing**: PASS. The plan defines unit, contract, and integration tests for
  signal math, routing, validation thresholds, reports, and end-to-end generation.
- **User Experience**: PASS. CLI output, filenames, summaries, and errors are
  required to distinguish speaker calibration, subwoofer calibration, full-band
  analysis, pro reference workflows, and optional playback-compatibility copies. A
  standalone beginner calibration guide is required for consumer users before
  reference-volume playback.
- **Simplicity**: PASS. A local CLI with shallow library modules is the smallest
  structure that supports repeatable generation, reports, validation, and future
  reuse while keeping the starting point obvious.

## Project Structure

### Documentation (this feature)

```text
specs/001-generate-pink-noise/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── validation-data.schema.json
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── pink_noise/
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── app.py
    ├── domain/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── profiles.py
    │   └── layouts.py
    ├── audio/
    │   ├── __init__.py
    │   ├── generator.py
    │   ├── wav.py
    │   └── validation.py
    └── output/
        ├── __init__.py
        ├── companion.py
        ├── reports.py
        └── guide.py

tests/
├── contract/
│   ├── test_cli_contract.py
│   └── test_validation_schema.py
├── integration/
│   └── test_generate_reference_set.py
└── unit/
    ├── test_app.py
    ├── domain/
    │   ├── test_models.py
    │   ├── test_profiles.py
    │   └── test_layouts.py
    ├── audio/
    │   ├── test_generator.py
    │   ├── test_wav.py
    │   └── test_validation.py
    └── output/
        ├── test_companion.py
        ├── test_guide.py
        └── test_reports.py
```

**Structure Decision**: Use a single Python package under `src/pink_noise` with
`cli.py` as a thin installed command adapter, `__main__.py` for
`python -m pink_noise`, and `app.py` as the workflow orchestrator. Group source by
responsibility: `domain/` owns profiles, layouts, and shared models; `audio/` owns
generation, WAV writing, and signal validation; `output/` owns reports, the
beginner calibration guide, and optional companion playback files derived from
already validated reference tracks. Keep the tree shallow so consumers and
contributors can identify the entry point quickly while still seeing which modules
affect audio correctness versus user-facing documentation.

## Additional Research Status

Research completed on 2026-06-18 and recorded in [research.md](./research.md).
Decisions now cover:

1. Concrete dependency and contract versions.
2. WAVE_FORMAT_EXTENSIBLE metadata, channel masks, and channel ordering.
3. Signed packed 24-bit PCM conversion without dither.
4. Post-write decoded-PCM validation and spectral slope methodology.
5. Periodic pink-noise period length, bin spacing, and seeded phase generation.
6. Bass-managed sub-system routing semantics.
7. JSON-only custom layout schema versioning.
8. Consumer-readable artifact filename convention.
9. Practical guide usability validation.
10. Optional companion playback container strategy and dependency handling.

## Complexity Tracking

No constitution violations. Optional companion playback export introduces an
external executable dependency only for users who request that compatibility copy;
the core WAV generation and validation path remains dependency-light and offline.
