from pathlib import Path

from pink_noise.domain.models import (
    CalibrationGuide,
    CalibrationProfile,
    CompanionPlaybackFile,
    GenerationRequest,
    GenerationSummary,
    NoiseSpecification,
    ReferenceTrack,
    SpeakerChannel,
    SpeakerLayout,
    ValidationData,
)


def test_domain_entities_are_constructible():
    channel = SpeakerChannel("fl", "Front Left", "main", 0, 1)
    layout = SpeakerLayout("1.0", "Mono", (channel,), 1)
    profile = CalibrationProfile("p", "Profile", "consumer_speaker", -30, (500, 2000))
    spec = NoiseSpecification(-30, (500, 2000), 60)
    request = GenerationRequest("p", "1.0", Path("out"))
    companion = CompanionPlaybackFile(Path("a__companion.mkv"), Path("a.wav"), "media_browser_compatibility", "matroska", True, "flac", "created")
    track = ReferenceTrack(Path("a.wav"), "p", "1.0", "fl", 1, 0, [], spec, {"status": "pass"})
    summary = GenerationSummary("now", request, [track], "75 dB", Path("CALIBRATION-GUIDE.md"), [], "pass")
    data = ValidationData("1.0", {}, [], "pass", {})
    guide = CalibrationGuide(Path("CALIBRATION-GUIDE.md"), (), (), (), (), (), (), (), ())
    assert layout.channels[0] == channel
    assert profile.default_rms_dbfs == -30
    assert summary.validation_overview == "pass"
    assert data.overall_status == "pass"
    assert guide.path.name == "CALIBRATION-GUIDE.md"
    assert companion.source_reference_track_path == Path("a.wav")


def test_generation_request_companion_playback_defaults_to_none():
    request = GenerationRequest("consumer-speaker", "5.1", Path("out"))
    assert request.companion_playback == "none"


def test_companion_playback_file_records_created_metadata():
    companion = CompanionPlaybackFile(
        path=Path("track__companion.mkv"),
        source_reference_track_path=Path("track.wav"),
        purpose="media_browser_compatibility",
        container="matroska",
        placeholder_video=True,
        audio_encoding="flac",
        status="created",
    )
    assert companion.placeholder_video is True
    assert companion.audio_encoding == "flac"
