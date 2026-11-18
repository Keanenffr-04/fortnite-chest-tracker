"""Paints the pirate token (gold coin, skull and crossbones) with QPainter. Geometry: app/overlay/pirate.py."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QRadialGradient

from app.overlay import pirate as P


def _c(rgb, alpha: int = 255) -> QColor:
    return QColor(rgb[0], rgb[1], rgb[2], alpha)


def draw_token(p: QPainter, cx: float, cy: float, r: float, alpha: int = 255) -> None:
    """Draw the coin. alpha (0-255) fades the whole coin, so it can be used as a watermark."""
    g = P.coin_layout(cx, cy, r)
    p.save()
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    def circle(radius, brush, pen=Qt.PenStyle.NoPen):
        p.setBrush(brush)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), radius, radius)

    # coin body: radial gold gradient, darker copper edge
    body = QRadialGradient(QPointF(cx - 0.25 * r, cy - 0.3 * r), 1.3 * r)
    body.setColorAt(0.0, _c(P.GOLD_LIGHT, alpha))
    body.setColorAt(0.55, _c(P.GOLD, alpha))
    body.setColorAt(1.0, _c(P.COPPER, alpha))
    circle(g["rim_outer"], QBrush(body), QPen(_c(P.GOLD_DARK, alpha), max(1.0, 0.04 * r)))
    # raised rim + inner ring
    circle(g["rim_inner"], QBrush(Qt.BrushStyle.NoBrush), QPen(_c(P.GOLD_DARK, alpha), max(1.0, 0.035 * r)))
    circle(g["ring"], QBrush(Qt.BrushStyle.NoBrush), QPen(_c(P.GOLD_LIGHT, int(alpha * 0.7)), max(1.0, 0.02 * r)))

    # crossed bones (drawn first so the skull sits on top)
    bone_pen = QPen(_c(P.BONE, alpha), g["bone_width"], Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    outline = QPen(_c(P.GOLD_DARK, alpha), g["bone_width"] * 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    for pen in (outline, bone_pen):
        p.setPen(pen)
        for (x1, y1), (x2, y2) in g["bones"]:
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    # skull: cranium + jaw
    sx, sy, sr = g["skull"]
    p.setPen(QPen(_c(P.GOLD_DARK, alpha), max(1.0, 0.03 * r)))
    p.setBrush(_c(P.BONE, alpha))
    jx, jy, jw, jh = g["jaw"]
    p.drawRoundedRect(QRectF(jx, jy, jw, jh), 0.05 * r, 0.05 * r)
    p.drawEllipse(QPointF(sx, sy), sr, sr)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(jx + 0.01 * r, jy - 0.02 * r, jw - 0.02 * r, 0.06 * r), 0.02 * r, 0.02 * r)

    # eyes, nose, teeth in dark
    dark = _c(P.GOLD_DARK, alpha)
    p.setBrush(dark)
    p.setPen(Qt.PenStyle.NoPen)
    for ex, ey, er in g["eyes"]:
        p.drawEllipse(QPointF(ex, ey), er, er)
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in g["nose"]]))
    p.setPen(QPen(dark, max(1.0, 0.018 * r)))
    for tx in g["teeth"]:
        p.drawLine(QPointF(tx, jy + 0.03 * r), QPointF(tx, g["jaw_bottom"] - 0.01 * r))
    p.restore()
