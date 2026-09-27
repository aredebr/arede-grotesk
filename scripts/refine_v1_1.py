"""
Historical record, not part of the build: the 1.1 refinements, applied once on top of the 1.0 sources
(sources/AredeGrotesk-Regular.ufo at tag v1.0.0). It has two parts, letters and figures; each one checks
that its glyphs still have the 1.0 outlines and is skipped otherwise, so running it twice changes nothing.

Design by Marcio Arêde, reviewed on study boards before touching the sources:

- m: rebuilt as the n arch repeated twice (same notch where the arch leaves the stem, same shoulder),
  without the steps the 1.0 outline had along the x-height. Width and stems unchanged.
- f: the r hook curve now runs down into the stem, removing the corner at the joint; the right edge of
  the stem is a single straight line.
- A, M, N, V, W: the inner vertices move along their own stroke edges until the joint is as thick as the
  horizontal bars of E (108.375 units): apex of A; top and base of M and N; point of V; top and base of W.
  Stroke angles and diagonal weights are unchanged.
- Lining figures (default, tabular and slashed zero) take the weights of the capitals: bars and the joints
  of bowls as thick as the bars of E, B, P, R (108.375); round tops and bottoms as thick as those of O
  (106.75); the inner vertex of 1 and 4 moved down to the bar line like the apex of A. Widths unchanged.
  Old-style and small figures (fractions, superiors, inferiors) are separate drawings and are not touched.

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
LETTERS = font['A'].contours[1].points[1].y == 625.4375       # letters still as in 1.0
FIGURES = font['one'].contours[0].points[7].y == 616.5         # figures still as in 1.0
if not (LETTERS or FIGURES):
    raise SystemExit('refine_v1_1: sources already refined, nothing done')


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


def refine_letters():
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


# ---------- figures: the weights of the capitals ----------
R_TOP, R_BOT = 607.25, 92.75       # inner top and bottom of O: round strokes 106.75 thick


def vmap(name, ci, idx, knots):
    """Move points idx of contour ci vertically with a piecewise-linear map through knots [(y, new y)].
    Beyond the first and last knot the shift of that knot is kept."""
    for i in idx:
        p = font[name].contours[ci].points[i]
        y = p.y
        if y <= knots[0][0]:
            p.y = y + knots[0][1] - knots[0][0]
        elif y >= knots[-1][0]:
            p.y = y + knots[-1][1] - knots[-1][0]
        else:
            for (y0, n0), (y1, n1) in zip(knots, knots[1:]):
                if y0 <= y <= y1:
                    p.y = n0 + (y - y0) * (n1 - n0) / (y1 - y0)
                    break


def sety(name, ci, idx, y):
    for i in idx:
        font[name].contours[ci].points[i].y = y


def edge(name, ci, i):
    p = font[name].contours[ci].points[i]
    return p.x, p.y


def refine_figures():
    # 0: round top and bottom like O; slashed zero keeps the points where the slash cuts the counter
    vmap('zero', 1, range(14), [(89.125, R_BOT), (610.875, R_TOP)])
    vmap('zero.zero', 1, [0, 1, 2, 5, 6, 7], [(89.125, R_BOT), (259.6875, 259.6875)])
    vmap('zero.zero', 2, range(1, 7), [(442.125, 442.125), (610.875, R_TOP)])
    # 1: inner vertex of the flag down to the bar line (default and tabular)
    for n in ('one', 'one.tf'):
        slide(n, {(0, 6): edge(n, 0, 5) + (TOP,), (0, 7): edge(n, 0, 0) + (TOP,)})
    # 2: round top, base bar
    vmap('two', 0, range(21, 30), [(375.0, 375.0), (610.875, R_TOP)])
    sety('two', 0, [2, 3], BOT)
    # 3: top bar, joint of the bowl, round bottom
    sety('three', 0, [13, 14], TOP)
    vmap('three', 0, range(17, 29), [(89.125, R_BOT), (212.7, 212.7), (318.8125, 403.3125 - BAR)])
    # 4: inner vertex down to the bar line, crossbar as thick as the bars (default and tabular)
    for n in ('four', 'four.tf'):
        bar_top = font[n].contours[0].points[2].y + BAR
        slide(n, {(1, 2): edge(n, 1, 1) + (TOP,), (1, 3): edge(n, 1, 4) + (TOP,)})
        sety(n, 0, [4, 5], bar_top)
        sety(n, 1, [0, 4], bar_top)
    # 5: top bar, joint of the bowl, round bottom
    sety('five', 0, [12, 13], TOP)
    vmap('five', 0, range(18, 31), [(89.125, R_BOT), (232.6, 232.6), (370.5, 466.8125 - BAR)])
    # 6: round top of the hook; bowl with round bottom and joint as thick as the bars
    vmap('six', 0, range(12, 18), [(469.5, 469.5), (610.875, R_TOP)])
    vmap('six', 1, range(14), [(89.125, R_BOT), (360.5, 453.5 - BAR)])
    # 7: top bar (default and tabular)
    sety('seven', 0, [9, 10], TOP)
    sety('seven.tf', 0, [9, 10], TOP)
    # 8: round top and bottom, waist as thick as the bars
    waist = (BAR - (411.125 - 308.0)) / 2
    vmap('eight', 1, range(14), [(89.125, R_BOT), (308.0, 308.0 - waist)])
    vmap('eight', 2, range(14), [(411.125, 411.125 + waist), (610.875, R_TOP)])
    # 9: bowl with round top and joint as thick as the bars; round bottom of the tail
    vmap('nine', 0, range(20, 25), [(89.125, R_BOT), (230.5, 230.5)])
    vmap('nine', 1, range(14), [(339.5, 246.5 + BAR), (610.875, R_TOP)])


if LETTERS:
    refine_letters()
    print('refine_v1_1: m f A M N V W updated')
if FIGURES:
    refine_figures()
    print('refine_v1_1: figures updated')
font.save()
