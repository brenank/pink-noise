import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_validation_schema_requires_request_track_and_artifact_fields():
    schema = json.loads(Path("specs/001-generate-pink-noise/contracts/validation-data.schema.json").read_text())
    validator = Draft202012Validator(schema)
    valid = {
        "schema_version": "1.0",
        "request": {
            "profile_id": "consumer-speaker",
            "layout_id": "5.1",
            "duration_seconds": 60,
            "sample_rate_hz": 48000,
            "bit_depth": 24,
            "noise_mode": "random",
            "seed": None,
            "routing_intent": "consumer_speaker",
            "channel_mask": 0x60F,
            "channel_mask_policy": "speaker_positions",
            "validation_thresholds": {
                "rms_tolerance_db": 0.1,
                "slope_tolerance_db_per_octave": 0.5,
                "silent_channel_max_dbfs": -120,
            },
        },
        "tracks": [
            {
                "path": "track.wav",
                "target_channel_id": "fl",
                "active_channel_index": 0,
                "silent_channel_indices": [1],
                "rms_dbfs": -30,
                "peak_dbfs": -18,
                "crest_factor_db": 12,
                "band_hz": [500, 2000],
                "pink_slope_db_per_octave": -3,
                "bandwidth_leakage_db": -80,
                "bandwidth_status": "pass",
                "silent_channel_max_dbfs": -144,
                "active_channel_count": 1,
                "channel_count": 2,
                "duration_seconds": 60,
                "status": "pass",
                "routing_intent": "consumer_speaker",
                "channel_mask": 0x60F,
                "noise_mode": "random",
                "periodic_period_seconds": None,
                "wav_format": {},
            }
        ],
        "overall_status": "pass",
        "artifacts": {
            "summary_path": "SUMMARY.md",
            "validation_data_path": "validation-data.json",
            "calibration_guide_path": "CALIBRATION-GUIDE.md",
        },
    }
    validator.validate(valid)


def test_validation_schema_accepts_companion_playback_metadata():
    schema = json.loads(Path("specs/001-generate-pink-noise/contracts/validation-data.schema.json").read_text())
    validator = Draft202012Validator(schema)
    companion = {
        "path": "track__companion.mkv",
        "source_reference_track_path": "track.wav",
        "purpose": "media_browser_compatibility",
        "container": "matroska",
        "placeholder_video": True,
        "audio_encoding": "flac",
        "status": "created",
    }
    valid = {
        "schema_version": "1.0",
        "request": {
            "profile_id": "consumer-speaker",
            "layout_id": "5.1",
            "duration_seconds": 60,
            "sample_rate_hz": 48000,
            "bit_depth": 24,
            "noise_mode": "random",
            "seed": None,
            "companion_playback": "video-container",
            "routing_intent": "consumer_speaker",
            "channel_mask": 0x60F,
            "channel_mask_policy": "speaker_positions",
            "validation_thresholds": {
                "rms_tolerance_db": 0.1,
                "slope_tolerance_db_per_octave": 0.5,
                "silent_channel_max_dbfs": -120,
            },
        },
        "tracks": [
            {
                "path": "track.wav",
                "target_channel_id": "fl",
                "active_channel_index": 0,
                "rms_dbfs": -30,
                "peak_dbfs": -18,
                "crest_factor_db": 12,
                "band_hz": [500, 2000],
                "pink_slope_db_per_octave": -3,
                "bandwidth_leakage_db": -80,
                "bandwidth_status": "pass",
                "silent_channel_max_dbfs": -144,
                "active_channel_count": 1,
                "channel_count": 2,
                "duration_seconds": 60,
                "status": "pass",
                "companion_playback_files": [companion],
            }
        ],
        "companion_playback_files": [companion],
        "overall_status": "pass",
        "artifacts": {
            "summary_path": "SUMMARY.md",
            "validation_data_path": "validation-data.json",
            "calibration_guide_path": "CALIBRATION-GUIDE.md",
            "companion_playback_paths": ["track__companion.mkv"],
        },
    }
    validator.validate(valid)


def test_validation_schema_rejects_missing_required_fields():
    schema = json.loads(Path("specs/001-generate-pink-noise/contracts/validation-data.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors({"schema_version": "1.0"}))
    assert errors
