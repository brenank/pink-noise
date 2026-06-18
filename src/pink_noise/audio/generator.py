from __future__ import annotations

import hashlib
import math

import numpy as np


PERIODIC_SECONDS = 4.0


def seed_to_int(seed: int | str | None) -> int:
    if seed is None:
        return 0
    if isinstance(seed, int):
        return seed
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "little", signed=False)


def dbfs_to_amplitude(rms_dbfs: float) -> float:
    return 10.0 ** (rms_dbfs / 20.0)


def rms(signal: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(signal, dtype=np.float64))))


def normalize_rms(signal: np.ndarray, target_dbfs: float) -> np.ndarray:
    current = rms(signal)
    if current == 0:
        return signal
    return signal * (dbfs_to_amplitude(target_dbfs) / current)


def generate_pink_noise(
    duration_seconds: float,
    sample_rate_hz: int,
    band_hz: tuple[float, float],
    rms_dbfs: float,
    seed: int | str | None = None,
    mode: str = "random",
) -> np.ndarray:
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive")
    if mode not in {"random", "periodic"}:
        raise ValueError("noise mode must be random or periodic")
    if mode == "periodic" and not math.isclose(duration_seconds % PERIODIC_SECONDS, 0.0, abs_tol=1e-9):
        raise ValueError("periodic noise duration must be a multiple of 4 seconds")
    sample_count = int(round(duration_seconds * sample_rate_hz))
    period_samples = int(PERIODIC_SECONDS * sample_rate_hz) if mode == "periodic" else sample_count
    base = _generate_period(period_samples, sample_rate_hz, band_hz, rms_dbfs, seed_to_int(seed))
    if mode == "periodic":
        return np.tile(base, sample_count // period_samples).astype(np.float64)
    return base.astype(np.float64)


def _generate_period(
    sample_count: int,
    sample_rate_hz: int,
    band_hz: tuple[float, float],
    rms_dbfs: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    freqs = np.fft.rfftfreq(sample_count, 1.0 / sample_rate_hz)
    spectrum = np.zeros(freqs.shape, dtype=np.complex128)
    low, high = band_hz
    active = (freqs >= low) & (freqs <= high)
    active[0] = False
    phases = rng.uniform(0.0, 2.0 * np.pi, active.sum())
    magnitudes = np.zeros_like(freqs)
    magnitudes[active] = 1.0 / np.sqrt(freqs[active])
    spectrum[active] = magnitudes[active] * (np.cos(phases) + 1j * np.sin(phases))
    signal = np.fft.irfft(spectrum, n=sample_count)
    signal = signal - np.mean(signal)
    return normalize_rms(signal, rms_dbfs)
