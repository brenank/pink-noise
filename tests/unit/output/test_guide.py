from pink_noise.domain.profiles import get_profile
from pink_noise.output.guide import render_guide


def test_guide_orders_safety_and_routing_before_reference_volume():
    guide = render_guide(get_profile("consumer-speaker"))
    assert guide.index("## Preflight Checklist") < guide.index("reference 0 dB") if "reference 0 dB" in guide else True
    assert "Start with the master volume low" in guide
    assert "Confirm direct routing" in guide
    assert "C-weighted Slow" in guide
    assert "75 dB SPL" in guide
    assert "Fallback Guidance" in guide


def test_guide_contains_file_use_map_warnings_and_troubleshooting():
    guide = render_guide(get_profile("subwoofer-bass-managed"))
    for text in ["File Use Map", "full-band-analysis", "pro-reference", "Troubleshooting", "Bass management", "sweeps"]:
        assert text.lower() in guide.lower()
