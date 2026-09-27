"""
Historical record, not part of the build: how the 1.0 glyphs were derived from the arede wordmark
vectors (sources/logo/) on top of a Space Grotesk SemiBold instance UFO (design coordinate 625,
generated with fontmake from the Space Grotesk sources). Paths are those of the original working session.
"""
"""
Arede Grotesk — protótipo v0.1
Base: Space Grotesk 2.0.0 (OFL 1.1), instância interpolada em wght 625 (design) ~ SemiBold.
Letras da logo (a r e d) substituem as originais; b p q n m h u o c derivadas delas.
"""
import json, math, shutil, os
import ufoLib2
from ufoLib2.objects import Glyph, Anchor
from svgpathtools import parse_path, Line
from booleanOperations import BooleanOperationManager
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.boundsPen import BoundsPen

SRC = 'instance_ufos/SpaceGrotesk-SemiBold.ufo'
OUT = 'arede/AredeGroteskProto-Regular.ufo'
LOGO = json.load(open('../logo-letters.json'))

XH = 494.125
S = XH / 73.2          # unidades por pt: x-height plana da logo (r) = 73.2 pt
BASE = 302.4           # linha de base da logo em pt (fundo do r)
ASC = 661              # topo do d da logo, em unidades
DESC = -200            # descendente mantida da Space Grotesk (decisão aberta)
SHIFT = 700 - ASC      # deslocamento das ascendentes minúsculas
bom = BooleanOperationManager()

font = ufoLib2.Font.open(SRC)


# ---------- utilidades ----------
def conv(z, x0):
    return ((z.real - x0) * S, (BASE - z.imag) * S)


def logo_glyph(key, x_left=0.0):
    """Contornos da letra da logo, borda esquerda da tinta em x_left."""
    p = parse_path(LOGO[key])
    x0 = p.bbox()[0]
    g = Glyph()
    pen = g.getPen()
    for sp in p.continuous_subpaths():
        first = conv(sp[0].start, x0)
        pen.moveTo((first[0] + x_left, first[1]))
        segs = list(sp)
        for i, seg in enumerate(segs):
            end = conv(seg.end, x0)
            last = (i == len(segs) - 1)
            if isinstance(seg, Line):
                if last and abs(end[0] - first[0]) < 0.05 and abs(end[1] - first[1]) < 0.05:
                    continue
                pen.lineTo((end[0] + x_left, end[1]))
            else:
                c1 = conv(seg.control1, x0); c2 = conv(seg.control2, x0)
                pen.curveTo((c1[0] + x_left, c1[1]), (c2[0] + x_left, c2[1]), (end[0] + x_left, end[1]))
        pen.closePath()
    fix_orientation(g)
    return g


def contour_area(c):
    pts = [(p.x, p.y) for p in c.points]
    a = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return a / 2


def point_in_contour(pt, c):
    pts = [(p.x, p.y) for p in c.points]
    x, y = pt; inside = False
    for i in range(len(pts)):
        x1, y1 = pts[i]; x2, y2 = pts[(i + 1) % len(pts)]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x: inside = not inside
    return inside


def reversed_contour(c):
    tmp = Glyph()
    from fontTools.pens.pointPen import PointToSegmentPen, SegmentToPointPen
    pen = ReverseContourPen(tmp.getPen())
    ptp = PointToSegmentPen(pen)
    c.drawPoints(ptp)
    return tmp.contours[0]


def fix_orientation(g):
    """Exteriores anti-horários (área > 0), interiores horários — convenção PostScript/UFO."""
    cs = list(g.contours)
    new = []
    for c in cs:
        others = [o for o in cs if o is not c]
        p0 = (c.points[0].x, c.points[0].y)
        depth = sum(1 for o in others if point_in_contour(p0, o))
        want_pos = (depth % 2 == 0)
        if (contour_area(c) > 0) != want_pos:
            new.append(reversed_contour(c))
        else:
            new.append(c)
    g.clearContours()
    for c in new:
        g.contours.append(c)


def transformed(src, T, reverse=False):
    g = Glyph()
    pen = TransformPen(g.getPen(), T)
    src.draw(ReverseContourPen(pen) if reverse else pen)
    return g


def mirror_x(src, axis_x):
    return transformed(src, (-1, 0, 0, 1, 2 * axis_x, 0), reverse=True)


def rotate180(src, cx, cy):
    return transformed(src, (-1, 0, 0, -1, 2 * cx, 2 * cy))


def rect(x0, y0, x1, y1):
    g = Glyph(); pen = g.getPen()
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return g


def union(*glyphs):
    out = Glyph()
    bom.union([c for g in glyphs for c in g.contours], out.getPointPen())
    fix_orientation(out)
    return out


def difference(subject, clip):
    out = Glyph()
    bom.difference(list(subject.contours), list(clip.contours), out.getPointPen())
    fix_orientation(out)
    return out


def intersection(subject, clip):
    out = Glyph()
    bom.intersection(list(subject.contours), list(clip.contours), out.getPointPen())
    fix_orientation(out)
    return out


def bounds(g):
    p = BoundsPen(font); g.draw(p); return p.bounds


def shift(src, dx, dy=0):
    return transformed(src, (1, 0, 0, 1, dx, dy))


def install(name, ink, lsb, rsb, anchors_from=None, unicodes=None):
    """Coloca a tinta no glifo `name` com as margens dadas; recalcula âncoras a partir do original."""
    b = bounds(ink)
    g = shift(ink, lsb - b[0])
    g.width = round(lsb + (b[2] - b[0]) + rsb)
    old = font[name] if name in font else None
    if old is not None:
        g.unicodes = list(old.unicodes)
        ob = bounds(old)
        ref = anchors_from if anchors_from is not None else old
        rb = bounds(ref)
        for a in ref.anchors:
            if rb and (rb[2] - rb[0]) > 0:
                nx = lsb + (a.x - rb[0]) * ((b[2] - b[0]) / (rb[2] - rb[0]))
            else:
                nx = a.x
            ny = a.y
            if ny > 640: ny = ASC          # âncoras no topo das ascendentes
            g.anchors.append(Anchor(x=round(nx, 1), y=round(ny, 1), name=a.name))
        g.lib = dict(old.lib)
    if unicodes: g.unicodes = unicodes
    g._name = name
    font[name] = g
    return g


# ---------- 1. letras exatas da logo ----------
STEM = (498.6 - 481.8) * S     # haste do r da logo ≈ 113 unidades
a_ink = logo_glyph('a')
r_ink = logo_glyph('r')
e_ink = logo_glyph('e1')
d_ink = logo_glyph('d')

install('a', a_ink, 41, 23)
install('r', r_ink, 73, 30)
install('e', e_ink, 49, 45)
install('d', d_ink, 49, 73)

# ---------- 2. derivadas do d: b p q ----------
db = bounds(d_ink)
d_w = db[2] - db[0]
b_ink = mirror_x(d_ink, db[0] + d_w / 2)
p_ink = rotate180(d_ink, db[0] + d_w / 2, XH / 2)   # d girado 180° = p (haste à esquerda)
# estender a haste do p até a descendente da família
for c in p_ink.contours:
    for pt in c.points:
        if pt.y < -150: pt.y = DESC
q_ink = mirror_x(p_ink, db[0] + d_w / 2)
install('b', b_ink, 73, 49)
install('p', p_ink, 73, 49)
install('q', q_ink, 49, 73)

# ---------- 3. derivadas do r: n m h u ----------
rb = bounds(r_ink)
r0 = shift(r_ink, -rb[0])                 # haste começa em x=0
W_N = 473                                 # largura de tinta do n da Space Grotesk
n_ink = union(rect(0, 0, STEM, XH), r0, mirror_x(r0, W_N / 2))
n_alt = union(r0, mirror_x(r0, W_N / 2))  # variante com os dois cantos redondos
u_ink = rotate180(n_ink, W_N / 2, XH / 2)
h_ink = union(n_ink, rect(0, 0, STEM, ASC))
W_M = 713; s = 300
m_ink = union(rect(0, 0, STEM, XH), r0, mirror_x(r0, (s + STEM) / 2),
              shift(r0, s), mirror_x(r0, (2 * s + STEM) / 2))
install('n', n_ink, 73, 69)
install('u', u_ink, 69, 73)
install('h', h_ink, 73, 69)
install('m', m_ink, 73, 69)
install('n.alt', n_alt, 73, 69, anchors_from=font['n'])

# ---------- 4. derivadas do d/e: o c ----------
cx = db[0] + d_w / 2
outer = Glyph(); inner = Glyph()
cs = sorted(d_ink.contours, key=lambda c: abs(contour_area(c)), reverse=True)
outer.contours.append(cs[0]); inner.contours.append(cs[1])
clipL = rect(db[0] - 50, -100, cx, 900)
o_outer_L = intersection(outer, clipL)
o_outer = union(o_outer_L, mirror_x(o_outer_L, cx))
o_inner_L = intersection(inner, clipL)
o_inner = union(o_inner_L, mirror_x(o_inner_L, cx))
o_ink = difference(o_outer, o_inner)
# c: abertura com cortes horizontais, espelhando o terminal do e (y=176)
T_CUT = 176.0
c_ink = difference(o_ink, rect(cx, T_CUT, db[2] + 100, XH - T_CUT))
install('o', o_ink, 49, 49)
install('c', c_ink, 49, 39)

# ---------- 5. ascendentes minúsculas para a altura do d da logo ----------
for name in ['k', 'l', 'f', 'f_f', 'f_f_i', 'f_f_l', 'fi', 'fl', 'f_j.liga', 'f_f_j.liga',
             'f_lcaron.liga', 'lslash', 'thorn', 'longs']:
    if name not in font: continue
    g = font[name]
    for c in g.contours:
        for pt in c.points:
            if pt.y >= 640: pt.y -= SHIFT
    for an in g.anchors:
        if an.y >= 640: an.y -= SHIFT
for name in ['i', 'j']:
    g = font[name]
    for comp in g.components[1:]:
        t = list(comp.transformation); t[5] -= SHIFT; comp.transformation = tuple(t)
    for an in g.anchors:
        if an.y >= 640: an.y -= SHIFT

# ---------- 6. recolocar acentos dos compostos ----------
MOD = {'a', 'r', 'e', 'd', 'b', 'p', 'q', 'n', 'm', 'h', 'u', 'o', 'c', 'k', 'l', 'f', 'i', 'j'}
for g in font:
    if not g.components or g.components[0].baseGlyph not in MOD:
        continue
    base = font[g.components[0].baseGlyph]
    if g.components[0].transformation[4] == 0 and len(g.contours) == 0:
        g.width = base.width
    pos = {a.name: (a.x, a.y) for a in base.anchors}
    for comp in g.components[1:]:
        mark = font[comp.baseGlyph]
        attach = next((a for a in mark.anchors if a.name.startswith('_')), None)
        if attach is None or attach.name[1:] not in pos:
            continue
        ax, ay = pos[attach.name[1:]]
        dx, dy = ax - attach.x, ay - attach.y
        comp.transformation = (1, 0, 0, 1, round(dx, 1), round(dy, 1))
        for a in mark.anchors:
            if not a.name.startswith('_'):
                pos[a.name] = (a.x + dx, a.y + dy)
    # âncoras do próprio composto seguem a base
    for a in g.anchors:
        if a.name in pos and a.name in ('top', 'bottom', 'ogonek'):
            a.x, a.y = pos[a.name]

# ---------- 7. kerning: "arede" reproduz a logo ----------
def logo_gap(k1, k2):
    b1 = parse_path(LOGO[k1]).bbox(); b2 = parse_path(LOGO[k2]).bbox()
    return (b2[0] - b1[1]) * S
pairs = [('a', 'r', logo_gap('a', 'r')), ('r', 'e', logo_gap('r', 'e1')),
         ('e', 'd', logo_gap('e1', 'd')), ('d', 'e', logo_gap('d', 'e2'))]
for l, r_, gap in pairs:
    gl, gr = font[l], font[r_]
    bl, br = bounds(gl), bounds(gr)
    natural = (gl.width - bl[2]) + br[0]
    font.kerning[(l, r_)] = round(gap - natural)
    print('kern', l, r_, round(gap - natural))

# ---------- 8. metadados ----------
info = font.info
info.familyName = 'Arede Grotesk Proto'
info.styleName = 'Regular'
info.styleMapFamilyName = 'Arede Grotesk Proto'
info.styleMapStyleName = 'regular'
info.postscriptFontName = 'AredeGroteskProto-Regular'
info.postscriptFullName = 'Arede Grotesk Proto Regular'
info.openTypeNameUniqueID = 'AredeGroteskProto-Regular;0.1'
info.openTypeOS2WeightClass = 600
info.versionMajor, info.versionMinor = 0, 1
info.openTypeNameVersion = 'Version 0.1 (protótipo)'
info.copyright = ('Copyright 2020 The Space Grotesk Project Authors '
                  '(https://github.com/floriankarsten/space-grotesk). '
                  'Arede Grotesk: modificações 2026 Arede (arede.me).')
info.openTypeNameDesigner = 'Florian Karsten, Květoslav Bartoš; Arede'
info.openTypeNameManufacturer = 'Arede'
info.openTypeNameDescription = 'Protótipo v0.1 derivado da logo arede sobre a Space Grotesk.'
info.openTypeNameLicense = ('This Font Software is licensed under the SIL Open Font License, '
                            'Version 1.1. http://scripts.sil.org/OFL')
info.openTypeNameLicenseURL = 'http://scripts.sil.org/OFL'
info.openTypeOS2VendorID = 'ARDE'

# ss06: n com os dois cantos redondos
font.features.text += '\n\nfeature ss06 {\n    sub n by n.alt;\n} ss06;\n'
if 'n.alt' not in font.lib.get('public.glyphOrder', []):
    font.lib['public.glyphOrder'] = list(font.lib.get('public.glyphOrder', [])) + ['n.alt']

if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs('arede', exist_ok=True)
font.save(OUT)
print('saved', OUT)
for n in ['a', 'r', 'e', 'd', 'b', 'p', 'q', 'n', 'm', 'h', 'u', 'o', 'c', 'n.alt']:
    g = font[n]; print(n, 'adv', g.width, 'bounds', tuple(round(v) for v in bounds(g)), 'contours', len(g.contours))
