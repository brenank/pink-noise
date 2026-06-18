from pink_noise.domain.layouts import BUILT_IN_LAYOUTS


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
