"""
Historical record, not part of the build: the two refinements that turned the prototype into 1.0
(the f with the hook of the r, the i with a rounded-square dot). Paths are those of the original working session.
"""
"""v1: refina só o f (gancho do r) e o i (ponto quadrado arredondado). Nada mais muda."""
import os, shutil, re, json
import ufoLib2
from ufoLib2.objects import Glyph, Anchor
from booleanOperations import BooleanOperationManager
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from svgpathtools import parse_path, Line

SRC = 'arede/AredeGroteskProto-Regular.ufo'
OUT = 'arede/AredeGrotesk-Regular.ufo'
font = ufoLib2.Font.open(SRC)
bom = BooleanOperationManager()
XH = 494.125; ASC = 661
LOGO = json.load(open('../logo-letters.json'))
S = XH / 73.2; BASE = 302.4
STEM = (498.6 - 481.8) * S


def bounds(g):
    p = BoundsPen(font); g.draw(p); return p.bounds


def rect(x0, y0, x1, y1):
    g = Glyph(); pen = g.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return g


def contour_area(c):
    pts = [(p.x, p.y) for p in c.points]; a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]; a += x1 * y2 - x2 * y1
    return a / 2


def point_in_contour(pt, c):
    pts = [(p.x, p.y) for p in c.points]; x, y = pt; inside = False
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x: inside = not inside
    return inside


def reversed_contour(c):
    from fontTools.pens.reverseContourPen import ReverseContourPen
    from fontTools.pens.pointPen import PointToSegmentPen
    tmp = Glyph(); c.drawPoints(PointToSegmentPen(ReverseContourPen(tmp.getPen()))); return tmp.contours[0]


def fix_orientation(g):
    cs = list(g.contours); new = []
    for c in cs:
        others = [o for o in cs if o is not c]
        depth = sum(1 for o in others if point_in_contour((c.points[0].x, c.points[0].y), o))
        want_pos = (depth % 2 == 0)
        new.append(reversed_contour(c) if (contour_area(c) > 0) != want_pos else c)
    g.clearContours()
    for c in new: g.contours.append(c)


def union(*glyphs):
    out = Glyph(); bom.union([c for g in glyphs for c in g.contours], out.getPointPen()); fix_orientation(out); return out


def intersection(a, b):
    out = Glyph(); bom.intersection(list(a.contours), list(b.contours), out.getPointPen()); fix_orientation(out); return out


def shift(src, dx, dy=0):
    g = Glyph(); src.draw(TransformPen(g.getPen(), (1, 0, 0, 1, dx, dy))); return g


def logo_glyph(key):
    p = parse_path(LOGO[key]); x0 = p.bbox()[0]
    g = Glyph(); pen = g.getPen()
    conv = lambda z: ((z.real - x0) * S, (BASE - z.imag) * S)
    for sp in p.continuous_subpaths():
        first = conv(sp[0].start); pen.moveTo(first); segs = list(sp)
        for i, seg in enumerate(segs):
            end = conv(seg.end)
            if isinstance(seg, Line):
                if i == len(segs) - 1 and abs(end[0] - first[0]) < 0.05 and abs(end[1] - first[1]) < 0.05: continue
                pen.lineTo(end)
            else:
                pen.curveTo(conv(seg.control1), conv(seg.control2), end)
        pen.closePath()
    fix_orientation(g); return g


# ---------- f: o gancho do r no topo ----------
f_old = font['f']
fb = bounds(f_old)
stem_l = 159.0; stem_r = stem_l + STEM          # haste do f (mesma largura do r)
arm_end = 391.0                                  # onde o braço do f terminava na Space Grotesk
r0 = logo_glyph('r'); rb = bounds(r0); r0 = shift(r0, -rb[0])
hook = shift(r0, stem_l, ASC - XH)               # topo do braço em 661
hook = intersection(hook, rect(stem_l - 1, 300, arm_end, ASC + 5))   # corta o braço na vertical em x=391
crossbar = rect(27, 400, 409, XH)
stem = rect(stem_l, 0, stem_r, ASC - 100)
f_new = union(stem, crossbar, hook)
f_new.width = f_old.width; f_new.unicodes = list(f_old.unicodes); f_new.lib = dict(f_old.lib)
f_new._name = 'f'; font['f'] = f_new

# ---------- i: ponto quadrado arredondado ----------
i_old = font['i']
i_new = Glyph(); pen = i_new.getPen()
pen.moveTo((73, 0)); pen.lineTo((187, 0)); pen.lineTo((187, XH)); pen.lineTo((73, XH)); pen.closePath()
cx, size, rad, y0 = 130.0, 146.0, 50.0, 519.0
x0, x1, y1 = cx - size / 2, cx + size / 2, y0 + size
k = 0.55 * rad
pen.moveTo((x0 + rad, y0))
pen.lineTo((x1 - rad, y0)); pen.curveTo((x1 - rad + k, y0), (x1, y0 + rad - k), (x1, y0 + rad))
pen.lineTo((x1, y1 - rad)); pen.curveTo((x1, y1 - rad + k), (x1 - rad + k, y1), (x1 - rad, y1))
pen.lineTo((x0 + rad, y1)); pen.curveTo((x0 + rad - k, y1), (x0, y1 - rad + k), (x0, y1 - rad))
pen.lineTo((x0, y0 + rad)); pen.curveTo((x0, y0 + rad - k), (x0 + rad - k, y0), (x0 + rad, y0))
pen.closePath()
fix_orientation(i_new)
i_new.width = i_old.width; i_new.unicodes = list(i_old.unicodes); i_new.lib = dict(i_old.lib)
for a in i_old.anchors:
    i_new.anchors.append(Anchor(x=a.x, y=(y1 + 12 if a.name == 'top' else a.y), name=a.name))
i_new._name = 'i'; font['i'] = i_new

# ---------- ligaduras do f saem do liga (o f novo não colide com i nem l) ----------
t = font.features.text
t = re.sub(r'sub f[^;]*;\n', '', t)
font.features.text = t

# ---------- metadados v1 ----------
info = font.info
info.familyName = 'Arede Grotesk'
info.styleMapFamilyName = 'Arede Grotesk'
info.postscriptFontName = 'AredeGrotesk-Regular'
info.postscriptFullName = 'Arede Grotesk Regular'
info.openTypeNameUniqueID = 'AredeGrotesk-Regular;1.0'
info.versionMajor, info.versionMinor = 1, 0
info.openTypeNameVersion = 'Version 1.000'
info.openTypeNameDescription = 'Arede Grotesk v1: derivada da logo arede sobre a Space Grotesk 2.0.0.'

if os.path.exists(OUT): shutil.rmtree(OUT)
font.save(OUT)
print('saved', OUT)
for n in ['f', 'i']:
    print(n, font[n].width, bounds(font[n]), len(font[n].contours))
