import pytest

from pink_noise.domain.layouts import get_layout
from pink_noise.domain.profiles import get_profile, is_channel_compatible


def test_profile_defaults_and_warnings():
    consumer = get_profile("consumer-speaker")
    assert consumer.default_band_hz == (500.0, 2000.0)
    assert consumer.default_rms_dbfs == -30.0
    assert "75 dB" in consumer.measurement_guidance
    assert get_profile("subwoofer-lfe-check").default_band_hz == (30.0, 80.0)
    assert get_profile("subwoofer-bass-managed").default_band_hz == (30.0, 80.0)
    assert get_profile("full-band-analysis").allowed_noise_modes == ("random", "periodic")
    assert get_profile("pro-reference").default_rms_dbfs == -20.0


def test_profile_channel_compatibility():
    layout = get_layout("5.1")
    fl = layout.channel_by_id("fl")
    lfe = layout.channel_by_id("lfe")
    assert is_channel_compatible(get_profile("consumer-speaker"), fl)
    assert not is_channel_compatible(get_profile("consumer-speaker"), lfe)
    assert is_channel_compatible(get_profile("subwoofer-lfe-check"), lfe)
    assert not is_channel_compatible(get_profile("subwoofer-lfe-check"), fl)
    assert is_channel_compatible(get_profile("subwoofer-bass-managed"), fl)
    assert not is_channel_compatible(get_profile("subwoofer-bass-managed"), lfe)
