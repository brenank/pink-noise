import json

import pytest

from pink_noise.app import _filename, generate
from pink_noise.domain.models import GenerationRequest, ValidationError


def test_consumer_generation_expands_targets_names_artifacts_and_blocks_overwrite(tmp_path):
    request = GenerationRequest("consumer-speaker", "5.1", tmp_path, duration_seconds=1, overwrite=True, seed="x")
    result = generate(request)
    assert len(result.track_paths) == 5
    assert result.summary_path.exists()
    assert result.validation_path.exists()
    assert result.guide_path.name == "CALIBRATION-GUIDE.md"
    assert all("consumer-speaker__5.1__ch" in path.name for path in result.track_paths)
    with pytest.raises(ValidationError, match="already exist"):
        generate(GenerationRequest("consumer-speaker", "5.1", tmp_path, duration_seconds=1, seed="x"))


def test_subwoofer_generation_rules_and_periodic_metadata(tmp_path):
    lfe = generate(GenerationRequest("subwoofer-lfe-check", "5.1", tmp_path / "lfe", duration_seconds=1, overwrite=True))
    assert len(lfe.track_paths) == 1
    bass = generate(GenerationRequest("subwoofer-bass-managed", "5.1", tmp_path / "bass", duration_seconds=1, overwrite=True))
    assert len(bass.track_paths) == 5
    analysis = generate(GenerationRequest("full-band-analysis", "2.0", tmp_path / "analysis", duration_seconds=4, noise_mode="periodic", overwrite=True, seed="same"))
    data = json.loads(analysis.validation_path.read_text())
    assert data["tracks"][0]["noise_mode"] == "periodic"
    assert data["tracks"][0]["periodic_period_seconds"] == 4.0


def test_profile_channel_mismatch_rejected(tmp_path):
    with pytest.raises(ValidationError, match="low-frequency"):
        generate(GenerationRequest("consumer-speaker", "5.1", tmp_path, target_channels=("lfe",), duration_seconds=1, overwrite=True))


def test_filename_convention_under_120_characters():
    path = _filename(__import__("pathlib").Path("out"), "consumer-speaker", "7.1.4", 8, "tfl", (500, 2000), -30, "random")
    assert len(path.name) < 120
    for part in ["consumer-speaker", "7.1.4", "ch8-tfl", "500-2000hz", "-30dbfs", "random"]:
        assert part in path.name
