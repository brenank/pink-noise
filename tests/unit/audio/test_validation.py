import numpy as np

from pink_noise.audio.generator import generate_pink_noise
from pink_noise.audio.validation import validate_track
from pink_noise.audio.wav import write_wav_24


def test_post_write_validation_reports_rms_clipping_silence_bandwidth_and_slope(tmp_path):
    path = tmp_path / "track.wav"
    mono = generate_pink_noise(1, 48000, (500, 2000), -30, 1)
    samples = np.zeros((mono.size, 2))
    samples[:, 0] = mono
    write_wav_24(path, samples, 48000, 0x3)
    result = validate_track(path, 0, "fl", (500, 2000), -30, 0x3)
    assert result["status"] == "pass"
    assert abs(result["rms_dbfs"] - -30) <= result["rms_tolerance_db"]
    assert result["peak_dbfs"] < 0
    assert result["crest_factor_db"] > 0
    assert result["silent_channel_max_dbfs"] == -999.0
    assert result["bandwidth_status"] == "pass"
    assert result["active_channel_count"] == 1
    assert -3.5 < result["pink_slope_db_per_octave"] < -2.5


def test_post_write_validation_fails_when_more_than_one_channel_is_active(tmp_path):
    path = tmp_path / "track.wav"
    mono = generate_pink_noise(1, 48000, (500, 2000), -30, 1)
    samples = np.zeros((mono.size, 2))
    samples[:, 0] = mono
    samples[:, 1] = mono
    write_wav_24(path, samples, 48000, 0x3)
    result = validate_track(path, 0, "fl", (500, 2000), -30, 0x3)
    assert result["status"] == "fail"
    assert "active-channel routing is invalid" in result["failures"]
