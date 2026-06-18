from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SpeakerChannel, SpeakerLayout, ValidationError


WAVE_BITS = {
    "fl": 0x1,
    "fr": 0x2,
    "fc": 0x4,
    "lfe": 0x8,
    "bl": 0x10,
    "br": 0x20,
    "sl": 0x200,
    "sr": 0x400,
    "tfl": 0x1000,
    "tfr": 0x4000,
    "tbl": 0x8000,
    "tbr": 0x20000,
}


CHANNEL_LABELS = {
    "fl": ("Front Left", "main"),
    "fr": ("Front Right", "main"),
    "fc": ("Center", "main"),
    "lfe": ("LFE", "lfe"),
    "bl": ("Back Left", "surround"),
    "br": ("Back Right", "surround"),
    "sl": ("Side Left", "surround"),
    "sr": ("Side Right", "surround"),
    "tfl": ("Top Front Left", "height"),
    "tfr": ("Top Front Right", "height"),
    "tbl": ("Top Back Left", "height"),
    "tbr": ("Top Back Right", "height"),
}


def _layout(layout_id: str, ordered_ids: tuple[str, ...]) -> SpeakerLayout:
    channels = []
    mask = 0
    for order, channel_id in enumerate(ordered_ids):
        label, role = CHANNEL_LABELS[channel_id]
        bit = WAVE_BITS[channel_id]
        mask |= bit
        channels.append(SpeakerChannel(channel_id, label, role, order, bit))
    return SpeakerLayout(layout_id, f"{layout_id} speaker layout", tuple(channels), mask)


BUILT_IN_LAYOUTS = {
    "2.0": _layout("2.0", ("fl", "fr")),
    "2.1": _layout("2.1", ("fl", "fr", "lfe")),
    "3.1": _layout("3.1", ("fl", "fr", "fc", "lfe")),
    "5.1": _layout("5.1", ("fl", "fr", "fc", "lfe", "sl", "sr")),
    "7.1": _layout("7.1", ("fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr")),
    "5.1.2": _layout("5.1.2", ("fl", "fr", "fc", "lfe", "sl", "sr", "tfl", "tfr")),
    "5.1.4": _layout("5.1.4", ("fl", "fr", "fc", "lfe", "sl", "sr", "tfl", "tfr", "tbl", "tbr")),
    "7.1.2": _layout("7.1.2", ("fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr", "tfl", "tfr")),
    "7.1.4": _layout("7.1.4", ("fl", "fr", "fc", "lfe", "bl", "br", "sl", "sr", "tfl", "tfr", "tbl", "tbr")),
}


def get_layout(layout_id_or_path: str) -> SpeakerLayout:
    if layout_id_or_path in BUILT_IN_LAYOUTS:
        return BUILT_IN_LAYOUTS[layout_id_or_path]
    path = Path(layout_id_or_path)
    if path.exists():
        return load_custom_layout(path)
    raise ValidationError(f"unknown layout '{layout_id_or_path}'; choose a built-in layout or JSON custom layout")


def load_custom_layout(path: Path) -> SpeakerLayout:
    try:
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"custom layout JSON is invalid: {exc.msg}") from exc
    if data.get("kind") != "pink-noise.custom-layout":
        raise ValidationError("custom layout field 'kind' must be 'pink-noise.custom-layout'")
    if data.get("schema_version") != "1.0":
        raise ValidationError("custom layout field 'schema_version' must be '1.0'")
    policy = data.get("channel_mask_policy", "directout")
    if policy not in {"directout", "speaker_positions"}:
        raise ValidationError("custom layout channel_mask_policy must be directout or speaker_positions")
    raw_channels = data.get("channels")
    if not isinstance(raw_channels, list) or not raw_channels:
        raise ValidationError("custom layout requires a non-empty ordered channels array")
    channels = []
    mask = 0
    for order, raw in enumerate(raw_channels):
        channel_id = str(raw.get("id", "")).lower()
        label = str(raw.get("label", channel_id)).strip()
        role = raw.get("role", "custom")
        if not channel_id or not label:
            raise ValidationError("custom layout channels require non-empty id and label")
        if role not in {"main", "surround", "height", "lfe", "subwoofer", "custom"}:
            raise ValidationError(f"custom layout channel '{channel_id}' has invalid role")
        aliases = tuple(str(alias).lower() for alias in raw.get("aliases", []))
        bit = WAVE_BITS.get(channel_id)
        if policy == "speaker_positions" and bit is None:
            raise ValidationError(f"custom layout channel '{channel_id}' cannot be mapped to a WAVE speaker bit")
        if bit is not None:
            mask |= bit
        channels.append(SpeakerChannel(channel_id, label, role, order, bit, aliases))
    return SpeakerLayout(
        id=str(data.get("id", path.stem)),
        display_name=str(data.get("display_name", path.stem)),
        channels=tuple(channels),
        channel_mask=mask if policy == "speaker_positions" else 0,
        channel_mask_policy=policy,
        is_builtin=False,
        source="custom",
    )
