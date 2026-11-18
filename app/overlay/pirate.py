"""Pirate token look (v1.1.16): colours + coin geometry. No Qt in here, so it is unit-tested.

The Pirate Shop token is a gold coin with a skull and crossbones. Everything is drawn in code from
simple shapes (no game art is copied). Geometry is in plain numbers; app/overlay/token_icon.py paints it.
"""
from __future__ import annotations

# RGB colours
BG_TOP = (30, 22, 12)          # dark treasure-chest brown
BG_BOTTOM = (10, 9, 15)        # near black
GOLD_LIGHT = (255, 232, 140)
GOLD = (245, 197, 66)
COPPER = (194, 120, 34)
GOLD_DARK = (112, 68, 14)
BONE = (250, 240, 214)
TEXT = (255, 243, 205)         # warm white for the big number
MUTED = (186, 160, 112)        # muted gold for secondary text


def coin_layout(cx: float, cy: float, r: float) -> dict:
    """Where every part of the coin goes, for a coin centred on (cx, cy) with radius r.

    Keys: rim_outer / rim_inner / ring (radii), skull (cx, cy, radius), jaw (x, y, w, h),
    eyes ((cx, cy, radius) x2), nose (3 points), teeth (x positions at the jaw bottom), bones (2 lines).
    """
    sk_r = 0.30 * r
    sk_cy = cy - 0.10 * r
    jaw_w, jaw_h = 0.34 * r, 0.20 * r
    jaw = (cx - jaw_w / 2, sk_cy + 0.16 * r, jaw_w, jaw_h)
    eye_r = 0.075 * r
    eyes = ((cx - 0.12 * r, sk_cy + 0.02 * r, eye_r), (cx + 0.12 * r, sk_cy + 0.02 * r, eye_r))
    nose = ((cx, sk_cy + 0.09 * r), (cx - 0.035 * r, sk_cy + 0.17 * r), (cx + 0.035 * r, sk_cy + 0.17 * r))
    jaw_bottom = jaw[1] + jaw_h
    teeth = tuple(cx + dx * jaw_w for dx in (-0.25, 0.0, 0.25))
    # crossed bones behind/below the skull: two diagonals, end caps are drawn as small circles
    a = 0.42 * r
    bones = (((cx - a, cy + 0.14 * r), (cx + a, cy + 0.54 * r)),
             ((cx + a, cy + 0.14 * r), (cx - a, cy + 0.54 * r)))
    return {"rim_outer": r, "rim_inner": 0.84 * r, "ring": 0.74 * r,
            "skull": (cx, sk_cy, sk_r), "jaw": jaw, "jaw_bottom": jaw_bottom,
            "eyes": eyes, "nose": nose, "teeth": teeth, "bones": bones, "bone_width": 0.085 * r}


def overlay_look(theme: str) -> dict:
    """Overlay drawing choices for a theme. Only the pirate theme gets the token look."""
    if theme == "pirate":
        return {"pirate": True, "bg_top": BG_TOP, "bg_bottom": BG_BOTTOM,
                "text": TEXT, "muted": MUTED, "watermark_alpha": 40}
    return {"pirate": False, "bg_top": (24, 20, 44), "bg_bottom": (12, 12, 24),
            "text": (245, 245, 255), "muted": (160, 160, 190), "watermark_alpha": 0}
