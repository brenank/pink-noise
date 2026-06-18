import numpy as np

from pink_noise.audio.wav import read_wav_24, write_wav_24


def test_wav_writer_uses_extensible_24_bit_pcm_header_and_channel_mask(tmp_path):
    path = tmp_path / "test.wav"
    samples = np.zeros((8, 2))
    samples[:, 0] = 0.1
    write_wav_24(path, samples, 48000, 0x3)
    decoded, fmt = read_wav_24(path)
    assert fmt["format_tag"] == 0xFFFE
    assert fmt["bits_per_sample"] == 24
    assert fmt["valid_bits_per_sample"] == 24
    assert fmt["channel_mask"] == 0x3
    assert np.allclose(decoded[:, 1], 0)
    assert np.allclose(decoded[:, 0], samples[:, 0], atol=1e-6)
