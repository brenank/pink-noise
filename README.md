# Pink Noise

Local CLI for generating calibration-grade pink-noise WAV reference tracks.

## Requirements

- Python 3.11+
- `uv` for the standard macOS/development workflow

## Install

On macOS, use `uv` as the standard setup path. It creates an isolated environment
from the project metadata and lockfile, and avoids relying on the older system
Python that ships with macOS.

```bash
brew install uv
uv sync --extra test
uv run pink-noise --help
```

Run commands through `uv run`:

```bash
uv run pink-noise generate --profile consumer-speaker --layout 5.1 --output out/5.1-consumer --overwrite
```

For development and validation:

```bash
uv run --extra test pytest
uv run --extra test python -m compileall -q src tests
```

Alternative virtualenv install:

```bash
brew install python@3.13
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
pink-noise --help
```

## Examples

Generate consumer speaker-trim files for a 5.1 system:

```bash
pink-noise generate --profile consumer-speaker --layout 5.1 --output out/5.1-consumer --overwrite
```

Generate a direct LFE-channel check:

```bash
pink-noise generate --profile subwoofer-lfe-check --layout 5.1 --output out/5.1-lfe --overwrite
```

Generate periodic full-band analysis material:

```bash
pink-noise generate --profile full-band-analysis --layout 2.0 --noise-mode periodic --duration 60 --output out/2.0-analysis --overwrite
```

Generate with a custom direct-output layout:

```bash
pink-noise generate --profile consumer-speaker --layout custom-layout.json --output out/custom --overwrite
```

Custom layout files are JSON:

```json
{
  "kind": "pink-noise.custom-layout",
  "schema_version": "1.0",
  "id": "front-stage",
  "display_name": "Front Stage",
  "channel_mask_policy": "directout",
  "channels": [
    { "id": "left", "label": "Left", "role": "main", "aliases": ["l"] },
    { "id": "center", "label": "Center", "role": "main", "aliases": ["c"] },
    { "id": "right", "label": "Right", "role": "main", "aliases": ["r"] }
  ]
}
```

## CLI Options

```text
pink-noise generate --profile <profile> --layout <layout> --output <directory> [options]
```

- `--profile`: `consumer-speaker`, `subwoofer-lfe-check`, `subwoofer-bass-managed`,
  `full-band-analysis`, or `pro-reference`.
- `--layout`: built-in layout ID (`2.0`, `2.1`, `3.1`, `5.1`, `7.1`, `5.1.2`,
  `5.1.4`, `7.1.2`, `7.1.4`) or a custom layout JSON path.
- `--channels`: comma-separated channel IDs. Defaults to all compatible channels.
- `--duration`: custom duration from 1 to 3600 seconds. Defaults to 60 seconds.
- `--noise-mode`: `random` or `periodic`. Periodic mode requires a duration that
  is a multiple of 4 seconds.
- `--seed`: repeatability value.
- `--overwrite`: allow replacing existing generated files.
- `--summary-name` / `--validation-name`: custom report filenames.

## Safety

Start playback at low volume, confirm direct channel routing, and only then raise
toward reference volume. Consumer speaker-trim files are intended for 75 dB SPL
C-weighted Slow checks. Subwoofer, full-band analysis, and pro-reference profiles
are deliberately labeled separately because they are not normal consumer AVR trim
defaults.

## Generated Artifacts

Each successful run writes:

- One 48 kHz, 24-bit PCM WAVE_FORMAT_EXTENSIBLE WAV per target channel.
- `SUMMARY.md` with profile, layout, channel, validation, and guide links.
- `validation-data.json` with machine-readable measurements and WAV metadata.
- `CALIBRATION-GUIDE.md` with beginner-facing calibration instructions.

Generated audio and output directories are ignored by git.
