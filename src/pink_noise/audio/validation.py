from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from .generator import rms
from .wav import read_wav_24

SILENCE_FLOOR_DBFS = -999.0


def dbfs(value: float) -> float:
    if value <= 0:
        return SILENCE_FLOOR_DBFS
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


def bandwidth_leakage_db(samples: np.ndarray, sample_rate_hz: int, band_hz: tuple[float, float]) -> float:
    signal = samples - np.mean(samples)
    spectrum = np.abs(np.fft.rfft(signal)) ** 2
    freqs = np.fft.rfftfreq(signal.size, 1.0 / sample_rate_hz)
    low, high = band_hz
    in_band = (freqs >= low) & (freqs <= high)
    out_band = (freqs > 0) & ~in_band
    in_power = float(np.sum(spectrum[in_band]))
    out_power = float(np.sum(spectrum[out_band]))
    if in_power <= 0:
        return math.inf
    if out_power <= 0:
        return -math.inf
    return 10.0 * math.log10(out_power / in_power)


def validate_track(
    path: Path,
    active_channel_index: int,
    target_channel_id: str,
    band_hz: tuple[float, float],
    target_rms_dbfs: float,
    channel_mask: int,
    rms_tolerance_db: float = 0.1,
    slope_tolerance_db_per_octave: float = 0.5,
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
    max_silent = max(silent_values, default=SILENCE_FLOOR_DBFS)
    if max_silent > silent_channel_max_dbfs:
        failures.append("inactive channel is not silent")
    channel_rms_dbfs = [dbfs(rms(samples[:, idx])) for idx in range(samples.shape[1])]
    active_channel_count = sum(level > silent_channel_max_dbfs for level in channel_rms_dbfs)
    if active_channel_count != 1 or channel_rms_dbfs[active_channel_index] <= silent_channel_max_dbfs:
        failures.append("active-channel routing is invalid")
    leakage_db = bandwidth_leakage_db(active, fmt["sample_rate_hz"], band_hz)
    if leakage_db > -40.0:
        failures.append("out-of-band energy exceeds bandwidth threshold")
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
        "bandwidth_leakage_db": leakage_db,
        "bandwidth_status": "pass" if leakage_db <= -40.0 else "fail",
        "pink_slope_db_per_octave": slope,
        "slope_tolerance_db_per_octave": slope_tolerance_db_per_octave,
        "silent_channel_max_dbfs": max_silent,
        "silent_channel_threshold_dbfs": silent_channel_max_dbfs,
        "channel_rms_dbfs": channel_rms_dbfs,
        "active_channel_count": active_channel_count,
        "status": "fail" if failures else "pass",
        "failures": failures,
        "channel_mask": channel_mask,
        "wav_format": fmt,
        "channel_count": int(samples.shape[1]),
        "duration_seconds": float(samples.shape[0] / fmt["sample_rate_hz"]),
    }
