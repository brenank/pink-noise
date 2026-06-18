# Pink Noise

Local CLI for generating calibration-grade pink-noise WAV reference tracks.

## Install

```bash
python -m pip install .
```

For development:

```bash
uv run --extra test pytest
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
