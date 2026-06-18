# CLI Contract: Generate Pink Noise

## Command

```text
pink-noise generate --profile <profile> --layout <layout> --output <directory> [options]
```

## Required Arguments

- `--profile <profile>`: Calibration profile to generate.
  - `consumer-speaker`
  - `subwoofer-lfe-check`
  - `subwoofer-bass-managed`
  - `full-band-analysis`
  - `pro-reference`
- `--layout <layout>`: Built-in layout ID or path to a custom layout file.
- `--output <directory>`: Destination for WAV files, summary, and validation data.

## Optional Arguments

- `--channels <list>`: Comma-separated channel IDs. Defaults to all compatible
  channels for the selected profile.
- `--duration <seconds>`: Custom duration from 1 to 3600 seconds. Defaults to 60
  seconds.
- `--noise-mode <random|periodic>`: Noise mode. Defaults to the profile default.
- `--seed <value>`: Repeatability value.
- `--overwrite`: Permit replacing existing generated files.
- `--summary-name <name>`: Human-readable summary filename.
- `--validation-name <name>`: Machine-readable validation filename.
- `--companion-playback <none|video-container>`: Optional compatibility copies for
  media browsers that hide audio-only files. Defaults to `none`. When set to
  `video-container`, the command writes one companion video-container file per
  selected reference track using placeholder video and lossless audio derived from
  the validated WAV file.

## Built-In Layout IDs

- `2.0`
- `2.1`
- `3.1`
- `5.1`
- `7.1`
- `5.1.2`
- `5.1.4`
- `7.1.2`
- `7.1.4`

## Success Behavior

On success the command writes:

- One or more 48 kHz, 24-bit PCM WAV files.
- Optional companion video-container playback files, when requested.
- One human-readable Markdown summary.
- One machine-readable JSON validation data file.
- One standalone beginner guide named `CALIBRATION-GUIDE.md`.

The command exits with status `0` and prints:

```text
Generated <count> reference tracks
Companion playback files: <count>
Summary: <path>
Validation: <path>
Calibration guide: <path>
Status: pass
```

## Failure Behavior

The command exits non-zero and writes no ready status when:

- Input layout is invalid.
- Requested profile and target channel are incompatible.
- Output files already exist and `--overwrite` is not set.
- A lossy output format is requested.
- Companion playback files are requested but the required compatibility exporter is
  unavailable or fails.
- Generated or written tracks fail validation.
- The output directory is unavailable.

Error output must include the rejected field or risky condition and a corrective
action.

## Custom Layout File

Custom layout files provide:

- Layout ID and display name.
- Ordered channel list.
- Channel role for each channel.
- Optional channel aliases.
- `kind: "pink-noise.custom-layout"` and `schema_version: "1.0"`.
- `channel_mask_policy`, either `speaker_positions` for known WAVE speaker bits
  or `directout` for custom/direct channel order with a zero channel mask.

Custom layout validation follows the rules in [data-model.md](../data-model.md).

Periodic pink noise is generated in seamless 4-second periods. Requests using
`--noise-mode periodic` must use a duration that is an exact multiple of 4 seconds.

## Companion Playback Files

Companion playback files are compatibility copies for media browsers that hide
audio-only files. They do not replace the primary validated WAV files and must be
generated only after the source WAV passes validation. The summary and validation
data must identify each companion file's source reference track, lossless audio
encoding, container, and compatibility purpose.
