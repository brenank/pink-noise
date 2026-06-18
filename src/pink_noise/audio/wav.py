from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

PCM_GUID = bytes.fromhex("0100000000001000800000aa00389b71")


def write_wav_24(path: Path, samples: np.ndarray, sample_rate_hz: int, channel_mask: int) -> None:
    if samples.ndim != 2:
        raise ValueError("samples must be shaped as frames x channels")
    frame_count, channels = samples.shape
    block_align = channels * 3
    byte_rate = sample_rate_hz * block_align
    data = _pack_24(samples)
    fmt_payload = struct.pack(
        "<HHIIHHHHI16s",
        0xFFFE,
        channels,
        sample_rate_hz,
        byte_rate,
        block_align,
        24,
        22,
        24,
        channel_mask,
        PCM_GUID,
    )
    riff_size = 4 + (8 + len(fmt_payload)) + (8 + len(data))
    with path.open("wb") as handle:
        handle.write(b"RIFF")
        handle.write(struct.pack("<I", riff_size))
        handle.write(b"WAVE")
        handle.write(b"fmt ")
        handle.write(struct.pack("<I", len(fmt_payload)))
        handle.write(fmt_payload)
        handle.write(b"data")
        handle.write(struct.pack("<I", len(data)))
        handle.write(data)


def read_wav_24(path: Path) -> tuple[np.ndarray, dict[str, int]]:
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        raise ValueError("not a RIFF/WAVE file")
    offset = 12
    fmt: dict[str, int] | None = None
    pcm = b""
    while offset + 8 <= len(data):
        chunk_id = data[offset : offset + 4]
        size = struct.unpack("<I", data[offset + 4 : offset + 8])[0]
        payload = data[offset + 8 : offset + 8 + size]
        if chunk_id == b"fmt ":
            base = struct.unpack("<HHIIHH", payload[:16])
            fmt = {
                "format_tag": base[0],
                "channels": base[1],
                "sample_rate_hz": base[2],
                "byte_rate": base[3],
                "block_align": base[4],
                "bits_per_sample": base[5],
                "valid_bits_per_sample": struct.unpack("<H", payload[18:20])[0],
                "channel_mask": struct.unpack("<I", payload[20:24])[0],
            }
        elif chunk_id == b"data":
            pcm = payload
        offset += 8 + size + (size % 2)
    if fmt is None:
        raise ValueError("missing fmt chunk")
    channels = fmt["channels"]
    raw = np.frombuffer(pcm, dtype=np.uint8).reshape(-1, 3)
    ints = raw[:, 0].astype(np.int32) | (raw[:, 1].astype(np.int32) << 8) | (raw[:, 2].astype(np.int32) << 16)
    ints = (ints << 8) >> 8
    samples = (ints.astype(np.float64) / (2**23 - 1)).reshape(-1, channels)
    return samples, fmt


def _pack_24(samples: np.ndarray) -> bytes:
    clipped = np.clip(samples, -1.0, 1.0)
    ints = np.rint(clipped * (2**23 - 1)).astype(np.int32).reshape(-1)
    unsigned = ints & 0xFFFFFF
    out = np.empty((unsigned.size, 3), dtype=np.uint8)
    out[:, 0] = unsigned & 0xFF
    out[:, 1] = (unsigned >> 8) & 0xFF
    out[:, 2] = (unsigned >> 16) & 0xFF
    return out.tobytes()
