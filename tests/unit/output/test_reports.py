from pathlib import Path

from pink_noise.domain.layouts import get_layout
from pink_noise.domain.models import GenerationRequest
from pink_noise.domain.profiles import get_profile
from pink_noise.output.reports import render_summary, render_validation_data


def test_reports_include_profile_layout_mapping_rms_band_seed_validation_and_guide():
    request = GenerationRequest("consumer-speaker", "5.1", Path("out"), seed="abc")
    profile = get_profile("consumer-speaker")
    layout = get_layout("5.1")
    tracks = [{"target_channel_id": "fl", "path": "a.wav", "rms_dbfs": -30, "band_hz": [500, 2000], "status": "pass"}]
    summary = render_summary(request, profile, layout, tracks, "SUMMARY.md", "validation.json", "CALIBRATION-GUIDE.md")
    assert "consumer-speaker" in summary
    assert "5.1" in summary
    assert "abc" in summary
    assert "CALIBRATION-GUIDE.md" in summary
    data = render_validation_data(request, profile, layout, tracks, "SUMMARY.md", "validation.json", "CALIBRATION-GUIDE.md")
    assert data["request"]["channel_mask"] == 0x60F
    assert data["overall_status"] == "pass"


def test_reports_label_subwoofer_analysis_pro_and_periodic_metadata():
    for profile_id in ["subwoofer-lfe-check", "subwoofer-bass-managed", "full-band-analysis", "pro-reference"]:
        profile = get_profile(profile_id)
        summary = render_summary(
            GenerationRequest(profile_id, "5.1", Path("out"), noise_mode="periodic" if profile_id != "subwoofer-lfe-check" else None),
            profile,
            get_layout("5.1"),
            [{"target_channel_id": "fl", "path": "a.wav", "rms_dbfs": profile.default_rms_dbfs, "band_hz": list(profile.default_band_hz), "status": "pass"}],
            "SUMMARY.md",
            "validation.json",
            "CALIBRATION-GUIDE.md",
        )
        assert profile.display_name in summary
        assert profile.purpose in summary
