import json

from pink_noise.app import generate
from pink_noise.audio.wav import read_wav_24
from pink_noise.domain.models import CompanionPlaybackFile, GenerationRequest


def test_generate_5_1_consumer_reference_set(tmp_path):
    result = generate(GenerationRequest("consumer-speaker", "5.1", tmp_path, duration_seconds=1, overwrite=True, seed="fixed"))
    assert len(result.track_paths) == 5
    assert result.summary_path.exists()
    assert result.guide_path.exists()
    data = json.loads(result.validation_path.read_text())
    assert data["overall_status"] == "pass"
    assert data["artifacts"]["calibration_guide_path"].endswith("CALIBRATION-GUIDE.md")
    samples, fmt = read_wav_24(result.track_paths[0])
    assert samples.shape[1] == 6
    assert fmt["channel_mask"] == 0x60F


def test_guide_is_written_and_linked(tmp_path):
    result = generate(GenerationRequest("consumer-speaker", "2.0", tmp_path, duration_seconds=1, overwrite=True))
    assert "CALIBRATION-GUIDE.md" in result.summary_path.read_text()
    guide = result.guide_path.read_text()
    assert "Preflight Checklist" in guide
    assert "Fallback Guidance" in guide


def test_subwoofer_and_analysis_quickstart_scenarios(tmp_path):
    lfe = generate(GenerationRequest("subwoofer-lfe-check", "5.1", tmp_path / "lfe", duration_seconds=1, overwrite=True))
    bass = generate(GenerationRequest("subwoofer-bass-managed", "5.1", tmp_path / "bass", duration_seconds=1, overwrite=True))
    analysis = generate(GenerationRequest("full-band-analysis", "2.0", tmp_path / "analysis", duration_seconds=4, noise_mode="periodic", overwrite=True))
    pro = generate(GenerationRequest("pro-reference", "2.0", tmp_path / "pro", duration_seconds=1, overwrite=True))
    assert len(lfe.track_paths) == 1
    assert len(bass.track_paths) == 5
    assert json.loads(analysis.validation_path.read_text())["request"]["noise_mode"] == "periodic"
    assert json.loads(pro.validation_path.read_text())["request"]["profile_id"] == "pro-reference"


def test_companion_playback_quickstart_scenario(tmp_path, monkeypatch):
    import pink_noise.app as app

    def fake_exporter(source_path, output_path):
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
    data = json.loads(result.validation_path.read_text())
    assert len(result.track_paths) == 1
    assert len(result.companion_paths) == 1
    assert result.track_paths[0].exists()
    assert result.companion_paths[0].exists()
    assert data["overall_status"] == "pass"
    assert data["companion_playback_files"][0]["audio_encoding"] == "flac"
    assert data["companion_playback_files"][0]["purpose"] == "media_browser_compatibility"
    assert "playback-compatibility copy" in result.summary_path.read_text()
