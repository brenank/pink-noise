# Quickstart: Generate Pink Noise

This guide validates the feature end-to-end once implementation tasks are complete.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- An output directory that can be safely overwritten during testing

## 1. Generate Consumer Speaker Calibration Material

```bash
pink-noise generate \
  --profile consumer-speaker \
  --layout 5.1 \
  --output out/5.1-consumer \
  --overwrite
```

Expected outcomes:

- Five WAV files are generated for the 5.1 consumer speaker layout: left, right,
  center, left surround, and right surround. LFE material is generated with the
  subwoofer profiles.
- Non-subwoofer tracks use 500 Hz-2 kHz pink noise.
- Tracks use -30 dBFS RMS per active channel.
- Exactly one channel is active in each channel-isolated file.
- The summary states 75 dB SPL, C-weighted, Slow, main listening position, and
  reference 0 dB master volume.
- The summary links to `CALIBRATION-GUIDE.md`.
- `CALIBRATION-GUIDE.md` exists in the output directory.
- Validation data reports `overall_status: pass`.

## 2. Validate Beginner Calibration Guide

Open `out/5.1-consumer/CALIBRATION-GUIDE.md`.

Expected outcomes:

- The guide begins with a preflight checklist before reference-volume playback.
- The guide tells users to start at low volume, confirm only the intended speaker is
  playing, and stop if multiple speakers play unexpectedly.
- The guide explains how to disable processing/upmixing and volume normalization.
- The guide explains SPL meter placement and C-weighted Slow setup in plain
  language.
- The guide provides numbered steps to adjust each speaker trim to 75 dB SPL.
- The guide includes a file-use map separating speaker trim, direct LFE check,
  bass-managed sub-system, full-band analysis, and pro reference files.
- The guide includes troubleshooting for wrong speaker, multiple speakers, stereo
  input display, unstable meter readings, unsafe volume, casting/streaming playback,
  and subwoofer mismatch.
- The guide tells users to use AVR internal test tones or a measurement workflow if
  they cannot confirm direct multichannel routing or disable processing.

## 3. Generate Direct LFE Check Material

```bash
pink-noise generate \
  --profile subwoofer-lfe-check \
  --layout 5.1 \
  --output out/5.1-lfe \
  --overwrite
```

Expected outcomes:

- The generated subwoofer/LFE material uses 30 Hz-80 Hz pink noise.
- The summary labels the output as a direct LFE-channel check.
- The report explains that sub integration, phase, delay, and crossover behavior
  need sweeps or equivalent analysis.

## 4. Generate Bass-Managed Sub-System Material

```bash
pink-noise generate \
  --profile subwoofer-bass-managed \
  --layout 5.1 \
  --output out/5.1-bass-managed \
  --overwrite
```

Expected outcomes:

- The summary distinguishes bass-managed sub-system calibration from direct
  LFE-channel checks.
- Validation data records routing intent and 30 Hz-80 Hz bandwidth.

## 5. Generate Full-Band Analysis Material

```bash
pink-noise generate \
  --profile full-band-analysis \
  --layout 2.0 \
  --noise-mode periodic \
  --output out/2.0-analysis \
  --overwrite
```

Expected outcomes:

- The output is labeled for analyzer/RTA workflows.
- The summary warns that this is not the recommended basic SPL trim-matching signal.
- Validation records periodic noise mode.

## 6. Confirm Overwrite Protection

Run a previously successful command again without `--overwrite`.

Expected outcome:

- The command exits non-zero.
- Existing files remain unchanged.
- Error output identifies the conflicting output files and suggests using
  `--overwrite` or another destination.

## 7. Confirm Validation Failure for Invalid Profile/Channel Pairing

Request a speaker-band calibration profile for an LFE/subwoofer-only target.

Expected outcome:

- The command exits non-zero or emits a blocking warning.
- The message recommends the subwoofer calibration profile.

## 8. Inspect Validation Data

Open the generated validation JSON and confirm each track includes:

- RMS level and tolerance result.
- Peak level and clipping status.
- Crest factor.
- Band limits.
- Pink-noise slope.
- Active target channel.
- Inactive channel silence result below -120 dBFS.
- Overall pass/fail status.
- Artifact paths for the summary, validation JSON, and `CALIBRATION-GUIDE.md`.

The JSON structure must match [validation-data.schema.json](./contracts/validation-data.schema.json).

## 9. Inspect WAV Metadata And Custom Layout Contracts

Expected outcomes:

- Surround WAV files use WAVE_FORMAT_EXTENSIBLE metadata with a 24-bit PCM subtype.
- Built-in layouts record the expected channel mask, such as `0x60F` for 5.1.
- Custom layouts validate against [custom-layout.schema.json](./contracts/custom-layout.schema.json).
- Custom layouts with `channel_mask_policy: directout` keep ordered channels and
  record a zero channel mask.

## 10. Confirm Periodic Duration Behavior

Run a periodic request with a non-multiple-of-4 duration.

Expected outcome:

- The command exits non-zero.
- The error explains that periodic noise duration must be a multiple of 4 seconds.

## 11. Confirm Supported Duration Bounds

Run a request with `--duration 0.5` or `--duration 3601`.

Expected outcome:

- The command exits non-zero.
- The error explains that duration must be between 1 and 3600 seconds.
