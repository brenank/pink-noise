from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from .generator import rms
from .wav import read_wav_24


def dbfs(value: float) -> float:
    if value <= 0:
        return -math.inf
    return 20.0 * math.log10(value)


def estimate_pink_slope(samples: np.ndarray, sample_rate_hz: int, band_hz: tuple[float, float]) -> float:
    signal = samples - np.mean(samples)
    spectrum = np.abs(np.fft.rfft(signal))
    freqs = np.fft.rfftfreq(signal.size, 1.0 / sample_rate_hz)
    low, high = band_hz
    active = (freqs >= low) & (freqs <= high) & (spectrum > 0)
    if active.sum() < 2:
        return 0.0
    x = np.log2(freqs[active])
    y = 20.0 * np.log10(spectrum[active])
    return float(np.polyfit(x, y, 1)[0])


def validate_track(
    path: Path,
    active_channel_index: int,
    target_channel_id: str,
    band_hz: tuple[float, float],
    target_rms_dbfs: float,
    channel_mask: int,
    rms_tolerance_db: float = 0.1,
    slope_tolerance_db_per_octave: float = 0.75,
    silent_channel_max_dbfs: float = -120.0,
) -> dict[str, object]:
    samples, fmt = read_wav_24(path)
    active = samples[:, active_channel_index]
    measured_rms_dbfs = dbfs(rms(active))
    peak_dbfs = dbfs(float(np.max(np.abs(samples))))
    crest_factor_db = peak_dbfs - measured_rms_dbfs
    slope = estimate_pink_slope(active, fmt["sample_rate_hz"], band_hz)
    failures: list[str] = []
    if fmt["format_tag"] != 0xFFFE or fmt["bits_per_sample"] != 24 or fmt["valid_bits_per_sample"] != 24:
        failures.append("WAV format metadata is not 24-bit WAVE_FORMAT_EXTENSIBLE PCM")
    if fmt["channel_mask"] != channel_mask:
        failures.append("WAV channel mask does not match layout")
    if abs(measured_rms_dbfs - target_rms_dbfs) > rms_tolerance_db:
        failures.append("RMS level outside tolerance")
    if peak_dbfs >= 0:
        failures.append("track clips")
    if abs(slope - -3.0) > slope_tolerance_db_per_octave:
        failures.append("pink-noise slope outside tolerance")
    silent_indices = [idx for idx in range(samples.shape[1]) if idx != active_channel_index]
    silent_values = [dbfs(rms(samples[:, idx])) for idx in silent_indices]
    max_silent = max(silent_values, default=-math.inf)
    if max_silent > silent_channel_max_dbfs:
        failures.append("inactive channel is not silent")
    return {
        "path": str(path),
        "target_channel_id": target_channel_id,
        "active_channel_index": active_channel_index,
        "silent_channel_indices": silent_indices,
        "rms_dbfs": measured_rms_dbfs,
        "rms_tolerance_db": rms_tolerance_db,
        "peak_dbfs": peak_dbfs,
        "crest_factor_db": crest_factor_db,
        "band_hz": [band_hz[0], band_hz[1]],
        "pink_slope_db_per_octave": slope,
        "slope_tolerance_db_per_octave": slope_tolerance_db_per_octave,
        "silent_channel_max_dbfs": max_silent,
        "status": "fail" if failures else "pass",
        "failures": failures,
        "channel_mask": channel_mask,
        "wav_format": fmt,
    }
