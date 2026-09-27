"""
Historical record, not part of the build: the 1.1 refinements, applied once on top of the 1.0 sources
(sources/AredeGrotesk-Regular.ufo at tag v1.0.0). Running it again on the 1.1 sources would move points
that were already moved, so it refuses to run unless it finds the 1.0 outlines.

Design by Marcio Arêde, reviewed on study boards before touching the sources:

- m: rebuilt as the n arch repeated twice (same notch where the arch leaves the stem, same shoulder),
  without the steps the 1.0 outline had along the x-height. Width and stems unchanged.
- f: the r hook curve now runs down into the stem, removing the corner at the joint; the right edge of
  the stem is a single straight line.
- A, M, N, V, W: the inner vertices move along their own stroke edges until the joint is as thick as the
  horizontal bars of E (108.375 units): apex of A; top and base of M and N; point of V; top and base of W.
  Stroke angles and diagonal weights are unchanged.

Usage (from the repo root, with the build venv active): python3 scripts/refine_v1_1.py
"""
from pathlib import Path

import pathops
import ufoLib2
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen

UFO = Path(__file__).resolve().parent.parent / 'sources/AredeGrotesk-Regular.ufo'
XH = 494.125
BAR = 108.375                       # thickness of the horizontal bars of E
TOP, BOT = 700 - BAR, BAR           # 591.625 and 108.375

font = ufoLib2.Font.open(UFO)
if font['A'].contours[1].points[1].y != 625.4375:
    raise SystemExit('refine_v1_1: sources are not the 1.0 outlines, nothing done')


def set_outline(glyph, rec):
    glyph.clearContours()
    rec.replay(glyph.getPen())


def union(*recs):
    acc = None
    for r in recs:
        p = pathops.Path()
        r.replay(p.getPen())
        acc = p if acc is None else pathops.op(acc, p, pathops.PathOp.UNION)
    out = RecordingPen()
    acc.draw(out)
    return out


def rect(x0, y0, x1, y1):
    r = RecordingPen()
    r.moveTo((x0, y0)); r.lineTo((x1, y0)); r.lineTo((x1, y1)); r.lineTo((x0, y1)); r.closePath()
    return r


# ---------- m: the n arch, repeated ----------
# The arch is n.alt (both shoulders round) with its middle shortened so the counter matches the m.
# Coordinates are snapped so stems are truly vertical and the x-height is one straight line.
STEM_L, STEM_R = 73.0, 186.4057388305664      # stem of n/r
IN_R = 372.4146270751953                       # right inner edge of the first m arch
SHIFT = 432.0088882446289 - IN_R               # n.alt counter minus m counter
OUT_R = IN_R + (STEM_R - STEM_L)               # right outer edge, same stem width


def snap(x, y):
    x = x - SHIFT if x > 309.5 else x
    y = 0.0 if abs(y) < 1 else y
    y = XH if abs(y - XH) < 1 else y
    y = 398.1224899291992 if abs(y - 398.19) < 0.2 else y   # flat top of the counter
    for ref, to in ((73.3, STEM_L), (186.9, STEM_R), (372.3, IN_R), (486.0, OUT_R)):
        if abs(x - ref) < 0.8:
            x = to
    return x, y


arch = RecordingPen()
pen_pts = []
for p in font['n.alt'].contours[0].points:
    if p.x == 309.5:
        continue                                   # midpoints of the flats, not needed once shortened
    xy = snap(p.x, p.y)
    prev = next((q for q in reversed(pen_pts) if q[1] is not None), None)
    if p.type == 'line' and prev and abs(prev[0][0] - xy[0]) < 0.05 and abs(prev[0][1] - xy[1]) < 0.05:
        continue                                   # drop near-duplicate points
    pen_pts.append((xy, p.type))
g = ufoLib2.objects.Glyph()
pp = g.getPointPen(); pp.beginPath()
for (x, y), t in pen_pts:
    pp.addPoint((x, y), segmentType=t)
pp.endPath()
# the shoulders leave the x-height with a horizontal tangent
for c in g.contours:
    pts = c.points
    for i, p in enumerate(pts):
        if p.type == 'curve' and p.y == XH:
            pts[i - 1].y = XH
        if p.type is not None and p.y == XH and i + 1 < len(pts) and pts[i + 1].type is None:
            pts[i + 1].y = XH
g.draw(arch)
arch2 = RecordingPen()
g.draw(TransformPen(arch2, (1, 0, 0, 1, 300, 0)))
set_outline(font['m'], union(rect(STEM_L, 0, STEM_R, XH), arch, arch2))

# ---------- f: no corner where the hook meets the stem ----------
X = 272.4057388305664
f = RecordingPen()
f.moveTo((159, 0)); f.lineTo((X, 0)); f.lineTo((X, 400)); f.lineTo((409, 400)); f.lineTo((409, XH))
f.lineTo((X, XH)); f.lineTo((X, 533.0652052049179))
f.curveTo((X, 560.6730490095626), (300.2, 560.6730490095626), (339.9144250221996, 564.9974865522539))
f.lineTo((391, 565.1279220581055)); f.lineTo((391, 660.9128875732422)); f.lineTo((344.18611907958984, 660.8206939697266))
f.curveTo((287.8893335894809, 660.3724274982922), (230.19500157445356, 647.9264853022539), (193.51639308913954, 603.3373135860654))
f.curveTo((169.65, 574.35), (159, 536.44), (159, 498.6))       # the r hook curve, down to the stem
f.lineTo((159, XH)); f.lineTo((27, XH)); f.lineTo((27, 400)); f.lineTo((159, 400)); f.closePath()
set_outline(font['f'], f)


# ---------- capitals: slide inner vertices along their edges ----------
def slide(name, moves):
    """moves: {(contour, point): (x, y of the far end of the edge, new y)}"""
    pts = {}
    for (ci, pi), (ax, ay, ny) in moves.items():
        p = font[name].contours[ci].points[pi]
        t = (ny - p.y) / (ay - p.y)
        pts[(ci, pi)] = (p.x + (ax - p.x) * t, ny)
    for (ci, pi), (x, y) in pts.items():
        p = font[name].contours[ci].points[pi]
        p.x, p.y = x, y


slide('A', {(1, 1): (213.625, 270, TOP), (1, 2): (419.25, 270, TOP)})
slide('M', {(0, 2): (185.375, 0, TOP), (0, 3): (339.5, 0, TOP),
            (0, 6): (538.0, 0, TOP), (0, 7): (692.125, 0, TOP),
            (0, 12): (585.25, 700, BOT), (0, 13): (292.25, 700, BOT)})
slide('N', {(0, 2): (187.375, 0, TOP), (0, 3): (370.8125, 0, TOP),
            (0, 8): (480.9375, 700, BOT), (0, 9): (297.5, 700, BOT)})
slide('V', {(0, 4): (475.4375, 700, BOT), (0, 5): (142.9375, 700, BOT)})
slide('W', {(0, 2): (337.25, 0, TOP), (0, 3): (554.75, 0, TOP),
            (0, 8): (741.5, 700, BOT), (0, 9): (549.6875, 700, BOT),
            (0, 12): (342.3125, 700, BOT), (0, 13): (150.5, 700, BOT)})

font.save()
print('refine_v1_1: m f A M N V W updated')
