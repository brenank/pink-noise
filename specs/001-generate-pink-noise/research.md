# Research: Generate Pink Noise

## Decision: Use Python 3.11+ with NumPy

**Rationale**: Python is a pragmatic fit for an offline generation script. NumPy
provides deterministic array math, FFT-based pink-noise generation, band limiting,
RMS normalization, and validation without pulling in a full audio workstation stack.

**Alternatives considered**:
- Rust: strong for binary distribution and speed, but adds more setup friction for
  the current scaffold and is unnecessary for 60-second generated files.
- Python standard library only: avoids dependencies, but makes FFT and spectral
  validation harder and more error-prone.
- FFmpeg-only shell workflow: useful as a tool, but weaker for deterministic
  validation and machine-readable reports.

## Decision: Generate WAV files with a local writer

**Rationale**: The feature needs 48 kHz, 24-bit PCM WAV files, discrete multichannel
routing, and predictable metadata. A local writer keeps output rules explicit and
testable. The writer can support conventional PCM chunks and extensible channel
metadata where needed for surround layouts.

**Alternatives considered**:
- `wave` module only: simple, but limited for explicit surround-channel metadata in
  some Python versions.
- `soundfile`/libsndfile: capable, but adds a binary dependency for a small output
  surface.
- FLAC primary output: lossless, but WAV is more broadly predictable for AVR/media
  playback and inspection.

## Decision: Use FFT-shaped pink noise with deterministic seeding

**Rationale**: FFT-domain shaping makes the intended 1/f power relationship direct
to generate and validate. Deterministic seeding enables repeatable output for the
same request, which is required by the spec and helpful for audits.

**Alternatives considered**:
- Voss-McCartney pink noise: efficient and common, but approximate and less direct
  to validate against strict slope tolerances.
- Filtered white noise with IIR filters: practical, but filter design choices can
  complicate exact band and slope validation.

## Decision: Provide random and periodic pink-noise modes

**Rationale**: Random pink noise is appropriate for SPL trim checks. Periodic pink
noise is valuable for analyzer/RTA workflows where repeatable spectral bins reduce
averaging/windowing artifacts.

**Alternatives considered**:
- Random-only: simpler, but weaker for analysis workflows called out in the spec.
- Periodic-only: useful for analyzers, but less familiar for simple SPL workflows.

## Decision: Define calibration profiles as data

**Rationale**: Profiles encode RMS level, bandwidth, routing intent, validation
thresholds, warnings, and default duration. This keeps consumer speaker calibration,
subwoofer calibration, full-band analysis, and pro reference behavior explicit and
easy to test.

**Alternatives considered**:
- Hard-coded branches in CLI: faster initially, but harder to validate and extend.
- User-supplied settings only: flexible, but risks wrong defaults for calibration.

## Decision: Use a responsibility-grouped package structure

**Rationale**: A shallow package tree keeps startup intuitive while separating the
parts of the system that fail for different reasons. `cli.py` remains the visible
installed command adapter, `__main__.py` supports `python -m pink_noise`, and
`app.py` coordinates the generation workflow. `domain/` contains calibration
profiles, layouts, and shared models; `audio/` contains signal generation, WAV
writing, and validation; `output/` contains reports and the beginner calibration
guide. This makes the source layout more informative than a flat list without
creating framework-style indirection.

**Alternatives considered**:
- Flat module layout: smallest file count, but audio correctness, domain rules, and
  user documentation responsibilities are harder to scan as the feature grows.
- Deep package tree by implementation pattern: adds indirection that is not useful
  for a single CLI/library package.
- Separate top-level packages: overstates the boundaries and complicates imports
  for a focused generator.

## Decision: Use JSON validation data plus Markdown summary

**Rationale**: The human summary supports real calibration sessions. JSON validation
data supports auditing, regression tests, and later regeneration without parsing
prose.

**Alternatives considered**:
- Markdown only: readable but hard to consume in automated checks.
- JSON only: complete but less friendly during calibration.

## Decision: Generate a standalone beginner calibration guide

**Rationale**: Non-audiophile consumer users need instructions before playback, not
only validation results after generation. A separate `CALIBRATION-GUIDE.md` is easy
to open on every platform, can be linked from the summary, and can be tested for
required safety, routing, SPL-meter, and troubleshooting content.

**Alternatives considered**:
- Embed guidance only in the summary: simpler, but mixes validation results with
  operational instructions and makes the user-facing workflow easier to miss.
- Generate PDF: more polished, but adds document-rendering complexity without
  improving the core calibration workflow.
- CLI-only guidance: visible during generation but easy to lose once files are
  copied to a theater playback system.

## Decision: Validate generated files after writing

**Rationale**: The spec requires generated material to pass before it is reported as
ready. Post-write validation catches routing, clipping, packing, and metadata issues
that pre-write signal validation alone can miss.

**Alternatives considered**:
- Validate arrays before writing only: simpler, but cannot detect WAV serialization
  defects.
- Report-only validation: rejected because calibration-grade outputs require
  pass/fail guarantees.

## Web-Researched Implementation Decisions Before Task Generation

The following decisions resolve the additional research candidates identified in
the implementation plan. Research was performed on 2026-06-18 from primary or
project-owner sources where possible.

## Decision: Pin concrete dependency and contract versions

**Decision**: Package metadata will support Python `>=3.11` with no upper bound,
while the reference development/test interpreter for v1 is Python `3.13.14`.
Runtime dependency constraints are `numpy>=2.4.6,<2.5`. Reproducible validation
baselines should lock NumPy to `2.4.6`. Test/build dependencies are
`pytest>=9.1,<10`, `jsonschema>=4.26,<5`, `hatchling>=1.30.1,<2`, and
`build>=1.5,<2`. Validation and custom-layout schemas use JSON Schema Draft
2020-12. The installed CLI entry point is `pink-noise = "pink_noise.cli:main"`.

**Rationale**: NumPy `2.4.6` is the latest stable NumPy release found on PyPI and
requires Python `>=3.11`; `2.5.0rc1` is a pre-release and should not be the default
implementation target. Pytest `9.1.0`, jsonschema `4.26.0`, hatchling `1.30.1`,
and build `1.5.0` are the current stable project-owner/PyPI versions researched.
JSON Schema lists Draft 2020-12 as current, and the existing validation schema
already uses the 2020-12 metaschema URI. PyPA documents console-script entry points
as installed shell commands that call a no-argument Python function.

**Version table**:

| Area | Version / constraint | Purpose |
|------|----------------------|---------|
| Python support | `>=3.11` | Runtime compatibility floor |
| Python reference test version | `3.13.14` | v1 reproducibility baseline |
| NumPy runtime | `>=2.4.6,<2.5` | FFT, RNG, array math, validation |
| NumPy lock | `==2.4.6` | Reproducible validation fixtures |
| pytest | `>=9.1,<10` | Automated tests |
| jsonschema | `>=4.26,<5` | Contract/schema tests |
| JSON Schema dialect | Draft 2020-12 | Validation and custom layout schemas |
| hatchling | `>=1.30.1,<2` | PEP 517 build backend |
| build | `>=1.5,<2` | Developer build frontend |

**Alternatives considered**:
- Require Python `>=3.13`: clearer reference environment, but unnecessarily
  excludes users whose supported Python `3.11` or `3.12` environments can run
  NumPy `2.4.x`.
- Track NumPy pre-releases: rejected because calibration validation baselines need
  stable behavior.
- Add YAML/TOML support for custom layouts: rejected for v1 to avoid extra parser
  dependencies and keep contracts inspectable with the Python standard library.

**Primary sources**:
- Python 3.13.14 release: https://www.python.org/downloads/release/python-31314/
- NumPy PyPI: https://pypi.org/project/numpy/
- pytest PyPI: https://pypi.org/project/pytest/
- jsonschema PyPI: https://pypi.org/project/jsonschema/
- hatchling PyPI: https://pypi.org/project/hatchling/
- build PyPI: https://pypi.org/project/build/
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- PyPA entry points: https://packaging.python.org/en/latest/specifications/entry-points/

## Decision: Use a custom WAVE_FORMAT_EXTENSIBLE writer for multichannel WAV

**Decision**: `audio/wav.py` will implement a local RIFF/WAVE writer for generated
files. Multichannel files use WAVE_FORMAT_EXTENSIBLE (`0xFFFE`), `fmt ` chunk size
`40`, `cbSize=22`, `SubFormat=KSDATAFORMAT_SUBTYPE_PCM`, PCM GUID
`00000001-0000-0010-8000-00aa00389b71`, `wBitsPerSample=24`,
`wValidBitsPerSample=24`, `nBlockAlign=nChannels*3`, and
`nAvgBytesPerSec=sampleRate*nBlockAlign`. The `dwChannelMask` bit count must match
`nChannels` unless the custom layout intentionally uses DIRECTOUT (`0`).

**Built-in channel masks and interleaved order**:

| Layout | Channel mask | Interleaved order |
|--------|--------------|-------------------|
| `2.0` | `0x00000003` | `FL FR` |
| `2.1` | `0x0000000B` | `FL FR LFE` |
| `3.1` | `0x0000000F` | `FL FR FC LFE` |
| `5.1` | `0x0000060F` | `FL FR FC LFE SL SR` |
| `7.1` | `0x0000063F` | `FL FR FC LFE BL BR SL SR` |
| `5.1.2` | `0x0000560F` | `FL FR FC LFE SL SR TFL TFR` |
| `5.1.4` | `0x0002D60F` | `FL FR FC LFE SL SR TFL TFR TBL TBR` |
| `7.1.2` | `0x0000563F` | `FL FR FC LFE BL BR SL SR TFL TFR` |
| `7.1.4` | `0x0002D63F` | `FL FR FC LFE BL BR SL SR TFL TFR TBL TBR` |

**Rationale**: Microsoft documents `dwChannelMask` as the assignment of stream
channels to speaker positions and states that channels must appear in the order of
the speaker-position flag table. WAVEFORMATEX alone cannot unambiguously describe
formats with more than two channels or valid-bit depth different from container
size. Python `wave` in 3.12+ can read WAVE_FORMAT_EXTENSIBLE PCM headers, but it is
not sufficient as the writer for explicit channel masks. The default consumer 5.1
layout should use side surrounds (`KSAUDIO_SPEAKER_5POINT1_SURROUND`) rather than
legacy rear surrounds. `.2` height layouts use `TFL/TFR` because WAVE_FORMAT_EXTENSIBLE
defines top-front and top-back pairs but not top-middle left/right.

**Alternatives considered**:
- Python `wave` writer only: rejected because the generator needs explicit
  multichannel speaker masks.
- WAVE_FORMAT_PCM for all files: acceptable for mono/stereo, but rejected as the
  default because surround layouts need channel metadata.
- Use `KSAUDIO_SPEAKER_DIRECTOUT` for all layouts: rejected because consumer AVR
  playback benefits from explicit speaker positions when they are known.

**Primary sources**:
- Microsoft WAVEFORMATEXTENSIBLE: https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ksmedia/ns-ksmedia-waveformatextensible
- Microsoft WAVEFORMATEX: https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/ns-mmeapi-waveformatex
- Python `wave` docs: https://docs.python.org/3/library/wave.html

## Decision: Use signed packed 24-bit PCM without dither

**Decision**: Float samples are clipped to `[-1.0, 1.0 - 2^-23]`, converted with
`round(sample * 2^23)`, constrained to signed int24 range `-8388608..8388607`, and
written little-endian as three bytes per sample. Inactive channels are written as
exact `00 00 00` digital silence. No dither is applied in v1.

**Rationale**: Calibration files require deterministic output, exact inactive
channel silence below `-120 dBFS`, and repeatable post-write validation. Dither
would add noise that is unnecessary at 24-bit depth for this use case and would
complicate silent-channel checks. Microsoft documents byte-aligned sample
containers and valid-bit precision rules for WAVE_FORMAT_EXTENSIBLE; using 24 valid
bits in a 24-bit container keeps the representation simple.

**Alternatives considered**:
- Add TPDF dither to active channels only: technically defensible, but unnecessary
  for calibration material and harder to validate reproducibly.
- Store 24 valid bits in a 32-bit container: easier packing, but larger files and
  not the requested 24-bit PCM primary output.

**Primary source**:
- Microsoft WAVEFORMATEXTENSIBLE: https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ksmedia/ns-ksmedia-waveformatextensible

## Decision: Validate decoded post-write PCM with a fixed spectral method

**Decision**: Validation runs against decoded PCM after WAV serialization. RMS is
`20*log10(sqrt(mean(x*x)))`; crest factor is `peak_dbfs - rms_dbfs`; clipping fails
when decoded PCM reaches full-scale integer limits; inactive channels fail above
`-120 dBFS`. Periodic files validate one 4-second period with a rectangular FFT.
Random files validate with Hann-windowed, 50%-overlap FFT averaging using
`n_fft=65536` for speaker/full-band profiles and `n_fft=262144` for 30-80 Hz
subwoofer profiles. Spectral slope groups valid bins into fractional-octave log
bins, computes mean narrow-bin power per group, then regresses
`10*log10(mean_power)` against `log2(frequency)`. The target slope is
`-3.0103 dB/octave` with the existing `+/-0.5 dB/octave` tolerance.

**Rationale**: NumPy documents the FFT frequency helpers and the interpretation of
FFT amplitude and power as `abs(A)` and `abs(A)**2`. A single documented validation
method prevents generated files from passing or failing based on ad hoc analyzer
choices. Larger FFT windows for subwoofer profiles improve low-frequency
resolution.

**Alternatives considered**:
- Validate pre-write float arrays only: rejected because serialization and packing
  defects must be caught.
- Slope from a single unwindowed random FFT: rejected because random variance would
  make tests brittle.
- Octave-band-only validation: easier to explain, but less direct for the
  narrow-band `-3 dB/octave` requirement.

**Primary sources**:
- NumPy FFT reference: https://numpy.org/doc/stable/reference/routines.fft.html
- NumPy `rfft`: https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html
- NumPy `rfftfreq`: https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html
- NumPy Hann window: https://numpy.org/doc/stable/reference/generated/numpy.hanning.html

## Decision: Generate periodic pink noise as a 4-second seamless period

**Decision**: Periodic mode uses a fixed 4-second period at 48 kHz:
`period_samples=192000`, `bin_spacing=0.25 Hz`. Default 60-second files repeat the
period exactly 15 times. Custom periodic durations must be whole-period multiples
or fail with a corrective error. Generation uses `np.fft.rfftfreq`, zeroes DC and
Nyquist bins, assigns in-band magnitude as `1/sqrt(f)`, chooses seeded random
phase with `np.random.default_rng(seed)`, reconstructs with `np.fft.irfft`, RMS
normalizes the period, and tiles it.

**Rationale**: A 4-second period gives stable analyzer bins while keeping the period
short enough for a 60-second file to contain many repeats. NumPy's real FFT APIs
define the positive-frequency bin model needed for deterministic periodic
generation, and `default_rng` gives explicit seeded repeatability.

**Alternatives considered**:
- Make the entire file one period: strongest periodicity, but less practical for
  custom duration handling and fixtures.
- Use 1-second periods: simpler, but 1 Hz bin spacing is coarse for low-frequency
  subwoofer material.
- Allow arbitrary periodic durations: rejected because non-integer period counts
  create discontinuities or require implicit truncation.

**Primary sources**:
- NumPy `rfft`: https://numpy.org/doc/stable/reference/generated/numpy.fft.rfft.html
- NumPy `irfft`: https://numpy.org/doc/stable/reference/generated/numpy.fft.irfft.html
- NumPy `rfftfreq`: https://numpy.org/doc/stable/reference/generated/numpy.fft.rfftfreq.html
- NumPy random Generator: https://numpy.org/doc/stable/reference/random/generator.html

## Decision: Define bass-managed sub-system files as low-frequency main-channel files

**Decision**: Direct LFE checks put 30-80 Hz pink noise in the LFE channel only.
Bass-managed sub-system files put 30-80 Hz pink noise in one non-LFE speaker
channel at a time, preserving the one-active-channel-per-track rule. The guide and
summary must state that these files only test the bass-managed path if the AVR or
processor is configured to redirect that channel's low-frequency content to the
subwoofer system.

**Rationale**: A WAV file cannot force AVR bass management; it can only route
content to channels. Sending low-frequency content through a main/surround/height
channel is the only file-based way to exercise the playback chain's bass-management
redirect path while preserving channel isolation.

**Alternatives considered**:
- Put bass-managed material in LFE: rejected because that only tests the direct LFE
  path.
- Put the same signal in all main channels: rejected because it violates the
  channel-isolated reference-track rule and can change bass summing behavior.
- Omit bass-managed outputs: rejected because the spec explicitly requires them.

## Decision: Use JSON-only custom layout files with a versioned schema

**Decision**: Custom layout files are JSON documents with
`kind="pink-noise.custom-layout"` and `schema_version="1.0.0"`. They are validated
against a JSON Schema Draft 2020-12 schema. Required fields are `layout_id`,
`display_name`, and ordered `channels`. Each channel has `id`, `label`, `role`, and
optional `wave_speaker_position`. `channel_mask_policy` defaults to `auto`; when
all channels map to unique WAVE speaker positions, the writer emits the matching
mask. If not, the layout must explicitly use `channel_mask_policy="directout"` and
the output summary must warn that playback routing must be manually verified.

**Rationale**: JSON avoids adding YAML/TOML parser dependencies, is supported by
the Python standard library, and can be validated with the same Draft 2020-12
contract tooling as validation reports. The Python `json` module preserves input
and output order by default, which is useful for ordered channel lists.

**Alternatives considered**:
- YAML/TOML custom layouts: friendlier to hand-edit, but adds dependencies or
  format-specific behavior not needed for v1.
- Infer channel order from object keys: rejected because explicit arrays are easier
  to validate and preserve.

**Primary sources**:
- Python `json` docs: https://docs.python.org/3/library/json.html
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12

## Decision: Use stable consumer-readable artifact names

**Decision**: WAV filenames use lower-kebab-case ASCII tokens:
`{profile}__{layout}__ch{index}-{channel}__{band}hz__{rms}dbfs__{mode}.wav`.
Negative RMS values use `neg30dbfs` / `neg20dbfs`; frequency bands use
`500-2000hz` or `30-80hz`; channel IDs use canonical short IDs such as `fl`, `fc`,
`lfe`, `sl`, `tfl`. Keep generated WAV filenames under 120 characters.

**Rationale**: The filename exposes the information users need at the listening
position without opening the summary, while avoiding spaces, Unicode symbols, and
punctuation that can be awkward across filesystems or media players.

**Alternatives considered**:
- Human sentence-style filenames: readable, but too long and brittle.
- Dense numeric filenames: compact, but fails the non-audiophile usability goal.

## Decision: Validate guide usability with automated content checks plus one walkthrough

**Decision**: v1 guide acceptance combines automated content checks with one
lightweight novice walkthrough before release. Automated checks must verify the
presence and ordering of the preflight checklist, low-volume start, direct-routing
confirmation, processing/upmixing/normalization warnings, C-weighted Slow meter
setup, 75 dB trim workflow, file-use map, subwoofer caveats, and fallback guidance.
The walkthrough asks one non-audiophile but receiver-familiar user to complete the
preflight checklist and identify one speaker-trim file using only generated output.

**Rationale**: The spec has a 90% consumer-success target, but a formal study is too
heavy for each implementation change. Automated checks protect required safety
content on every build; the walkthrough catches obvious wording or ordering issues
before v1 release.

**Alternatives considered**:
- Automated checks only: useful but cannot prove the guide is understandable.
- Formal usability study on every change: disproportionate for a local generator.

## Decision: Generate optional companion playback files with FFmpeg

**Decision**: Keep 48 kHz, 24-bit PCM WAV as the primary validated calibration
artifact. When the user requests companion playback files, generate one
media-player-compatible video-container file per selected reference track by
invoking an installed FFmpeg executable. The companion file uses a minimal
placeholder video stream and lossless audio derived from the already validated WAV
track. Companion filenames mirror the source track name with a companion suffix and
must be reported as playback-compatibility copies, not independently validated
source tracks.

**Rationale**: Some media browsers hide audio-only files even when their playback
pipeline can handle the audio stream. A video container makes the files visible to
those browsers while keeping the calibration signal lossless and preserving the
primary WAV validation contract. Treating FFmpeg as an optional executable avoids
adding large binary dependencies to the normal generator path and keeps all
companion export failures scoped to users who explicitly request that output.

**Alternatives considered**:
- Make video-container files the primary output: rejected because WAV remains the
  most inspectable, directly validated calibration artifact.
- Generate audio-only FLAC/MKA companions: lossless, but does not address media
  browsers that hide audio-only files.
- Implement container muxing directly in Python: rejected because it adds complex
  media-container behavior outside the calibration domain.
- Require companion files for every run: rejected because most workflows only need
  WAV files and should not depend on an external encoder.
