import json

import pytest

from pink_noise.domain.layouts import BUILT_IN_LAYOUTS, load_custom_layout
from pink_noise.domain.models import ValidationError


def test_builtin_layout_channel_order_and_masks():
    expected = {
        "2.0": (["fl", "fr"], 0x00000003),
        "2.1": (["fl", "fr", "lfe"], 0x0000000B),
        "3.1": (["fl", "fr", "fc", "lfe"], 0x0000000F),
        "5.1": (["fl", "fr", "fc", "lfe", "sl", "sr"], 0x0000060F),
        "7.1": (["fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr"], 0x0000063F),
        "5.1.2": (["fl", "fr", "fc", "lfe", "sl", "sr", "tfl", "tfr"], 0x0000560F),
        "5.1.4": (["fl", "fr", "fc", "lfe", "sl", "sr", "tfl", "tfr", "tbl", "tbr"], 0x0002D60F),
        "7.1.2": (["fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr", "tfl", "tfr"], 0x0000563F),
        "7.1.4": (["fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr", "tfl", "tfr", "tbl", "tbr"], 0x0002D63F),
    }
    for layout_id, (channels, mask) in expected.items():
        layout = BUILT_IN_LAYOUTS[layout_id]
        assert [channel.id for channel in layout.channels] == channels
        assert layout.channel_mask == mask


def test_custom_layout_rejects_ambiguous_aliases(tmp_path):
    path = tmp_path / "layout.json"
    path.write_text(
        json.dumps(
            {
                "kind": "pink-noise.custom-layout",
                "schema_version": "1.0",
                "id": "bad",
                "display_name": "Bad",
                "channel_mask_policy": "directout",
                "channels": [
                    {"id": "left", "label": "Left", "role": "main", "aliases": ["l"]},
                    {"id": "right", "label": "Right", "role": "main", "aliases": ["l"]},
                ],
            }
        )
    )
    with pytest.raises(ValidationError, match="ambiguous"):
        load_custom_layout(path)
