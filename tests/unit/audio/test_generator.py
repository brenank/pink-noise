import numpy as np
import pytest

from pink_noise.audio.generator import generate_pink_noise, rms
from pink_noise.audio.validation import estimate_pink_slope


def test_random_pink_noise_is_seeded_band_limited_and_normalized():
    a = generate_pink_noise(1, 48000, (500, 2000), -30, "seed")
    b = generate_pink_noise(1, 48000, (500, 2000), -30, "seed")
    assert np.allclose(a, b)
    assert abs(20 * np.log10(rms(a)) - -30) < 0.01
    assert -3.8 < estimate_pink_slope(a, 48000, (500, 2000)) < -2.2


def test_periodic_noise_uses_four_second_period_and_tiles_seamlessly():
    signal = generate_pink_noise(8, 48000, (20, 20000), -30, 123, "periodic")
    assert signal[:192000].shape == (192000,)
    assert np.allclose(signal[:192000], signal[192000:])


def test_periodic_noise_rejects_non_period_multiple_duration():
    with pytest.raises(ValueError, match="multiple of 4"):
        generate_pink_noise(5, 48000, (20, 20000), -30, 123, "periodic")
