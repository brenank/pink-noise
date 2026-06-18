import json

import pytest

import pink_noise.app as app
from pink_noise.app import _filename, generate
from pink_noise.domain.models import CompanionPlaybackFile, GenerationRequest, ValidationError


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
    assert data["generated_at"] == analysis.validation_data["generated_at"]


def test_profile_channel_mismatch_rejected(tmp_path):
    with pytest.raises(ValidationError, match="low-frequency"):
        generate(GenerationRequest("consumer-speaker", "5.1", tmp_path, target_channels=("lfe",), duration_seconds=1, overwrite=True))


def test_consumer_default_excludes_lfe_because_subwoofer_profiles_own_lfe(tmp_path):
    result = generate(GenerationRequest("consumer-speaker", "5.1", tmp_path, duration_seconds=1, overwrite=True))
    assert len(result.track_paths) == 5
    assert all("__ch3-lfe__" not in path.name for path in result.track_paths)


def test_filename_convention_under_120_characters():
    path = _filename(__import__("pathlib").Path("out"), "consumer-speaker", "7.1.4", 8, "tfl", (500, 2000), -30, "random")
    assert len(path.name) < 120
    for part in ["consumer-speaker", "7.1.4", "ch8-tfl", "500-2000hz", "-30dbfs", "random"]:
        assert part in path.name


def test_companion_playback_plans_paths_exports_after_validation_and_reports_metadata(tmp_path, monkeypatch):
    calls = []

    def fake_exporter(source_path, output_path):
        calls.append((source_path, output_path, source_path.exists()))
        output_path.write_text("companion", encoding="utf-8")
        return CompanionPlaybackFile(
            output_path,
            source_path,
            "media_browser_compatibility",
            "matroska",
            True,
            "flac",
            "created",
        )

    monkeypatch.setattr(app, "create_companion_playback", fake_exporter)

    result = generate(
        GenerationRequest(
            "consumer-speaker",
            "5.1",
            tmp_path,
            target_channels=("fc",),
            duration_seconds=1,
            overwrite=True,
            companion_playback="video-container",
        )
    )

    assert len(result.track_paths) == 1
    assert len(result.companion_paths) == 1
    assert calls[0][2] is True
    assert calls[0][0] == result.track_paths[0]
    assert calls[0][1] == result.companion_paths[0]
    data = json.loads(result.validation_path.read_text())
    assert data["request"]["companion_playback"] == "video-container"
    assert data["companion_playback_files"][0]["source_reference_track_path"] == str(result.track_paths[0])
    assert data["artifacts"]["companion_playback_paths"] == [str(result.companion_paths[0])]
    assert data["tracks"][0]["companion_playback_files"][0]["path"] == str(result.companion_paths[0])
    assert "playback-compatibility copy" in result.summary_path.read_text()


def test_companion_playback_existing_output_blocks_without_overwrite(tmp_path):
    companion_path = (
        tmp_path
        / "consumer-speaker__5.1__ch2-fc__500-2000hz__-30dbfs__random__companion.mkv"
    )
    companion_path.write_text("existing", encoding="utf-8")

    with pytest.raises(ValidationError, match="already exist"):
        generate(
            GenerationRequest(
                "consumer-speaker",
                "5.1",
                tmp_path,
                target_channels=("fc",),
                duration_seconds=1,
                companion_playback="video-container",
            )
        )
