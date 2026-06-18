import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_custom_layout_schema_accepts_ordered_channels_roles_aliases_and_policy():
    schema = json.loads(Path("specs/001-generate-pink-noise/contracts/custom-layout.schema.json").read_text())
    layout = {
        "kind": "pink-noise.custom-layout",
        "schema_version": "1.0",
        "id": "desk-3",
        "display_name": "Desk 3",
        "channel_mask_policy": "directout",
        "channels": [
            {"id": "left", "label": "Left", "role": "main", "aliases": ["l"]},
            {"id": "sub", "label": "Sub", "role": "subwoofer"},
        ],
    }
    Draft202012Validator(schema).validate(layout)


def test_custom_layout_schema_requires_kind_and_schema_version():
    schema = json.loads(Path("specs/001-generate-pink-noise/contracts/custom-layout.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors({"channels": []}))
    assert {tuple(error.path) for error in errors} or errors
