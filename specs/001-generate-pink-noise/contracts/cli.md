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
- `--duration <seconds>`: Custom duration. Defaults to 60 seconds.
- `--noise-mode <random|periodic>`: Noise mode. Defaults to the profile default.
- `--seed <value>`: Repeatability value.
- `--overwrite`: Permit replacing existing generated files.
- `--summary-name <name>`: Human-readable summary filename.
- `--validation-name <name>`: Machine-readable validation filename.

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
- One human-readable Markdown summary.
- One machine-readable JSON validation data file.
- One standalone beginner guide named `CALIBRATION-GUIDE.md`.

The command exits with status `0` and prints:

```text
Generated <count> reference tracks
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

Custom layout validation follows the rules in [data-model.md](../data-model.md).
