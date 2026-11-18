import math

from app.overlay.model import THEMES
from app.overlay.pirate import coin_layout, overlay_look


def test_coin_parts_stay_inside_the_coin():
    cx, cy, r = 100.0, 80.0, 50.0
    g = coin_layout(cx, cy, r)
    assert g["rim_outer"] > g["rim_inner"] > g["ring"] > 0
    sx, sy, sr = g["skull"]
    assert math.hypot(sx - cx, sy - cy) + sr < g["ring"]
    for (x1, y1), (x2, y2) in g["bones"]:
        for x, y in ((x1, y1), (x2, y2)):
            assert math.hypot(x - cx, y - cy) < g["ring"]
    for ex, ey, er in g["eyes"]:
        assert math.hypot(ex - sx, ey - sy) + er < sr


def test_coin_scales_and_moves_with_radius_and_centre():
    a, b = coin_layout(0, 0, 10), coin_layout(5, 7, 20)
    assert b["rim_outer"] == 2 * a["rim_outer"]
    assert abs(b["skull"][2] - 2 * a["skull"][2]) < 1e-9
    assert abs(b["skull"][0] - 5) < 1e-9
    assert len(b["bones"]) == 2 and len(b["teeth"]) == 3 and len(b["nose"]) == 3


def test_only_the_pirate_theme_gets_the_token_look():
    assert "pirate" in THEMES
    assert overlay_look("pirate")["pirate"] and overlay_look("pirate")["watermark_alpha"] > 0
    for name in THEMES:
        if name != "pirate":
            look = overlay_look(name)
            assert not look["pirate"] and look["watermark_alpha"] == 0
    assert overlay_look("nonsense")["bg_top"] == overlay_look("violet")["bg_top"]
