"""Render the whole-world campaign map (4 quads + water mask) from Natural Earth land polygons.

Usage: python3 render_world.py <lon_west_deg_0_360> <out_dir> <prefix> [quad_w]
Equirectangular, 2:1, pole to pole, north up, 360 degrees wide starting at lon_west. Quads: 0=TL 1=TR 2=BL 3=BR.
Polygons are drawn three times (shifted by -360, 0, +360 degrees) so land crossing the seam is complete on both sides.
"""
import sys, os
import numpy as np
import shapefile
from PIL import Image, ImageDraw

SEA = (83, 107, 127, 255)
LAND = (0, 0, 0, 255)
NE = '/tmp/claude-0/ne/'

lon0 = float(sys.argv[1]); out = sys.argv[2]; prefix = sys.argv[3]
qw = int(sys.argv[4]) if len(sys.argv) > 4 else 4096
W, H = qw * 2, qw
os.makedirs(out, exist_ok=True)
PX = W / 360.0


def unwrap(ring):
    """lon sequence made continuous (no 360 jumps), then shifted so it starts in [lon0, lon0+360)."""
    lons = []
    prev = None
    for lo, la in ring:
        if prev is not None:
            while lo - prev > 180: lo -= 360
            while lo - prev < -180: lo += 360
        lons.append(lo); prev = lo
    base = lons[0]
    while base < lon0: base += 360; lons = [l + 360 for l in lons]
    while base >= lon0 + 360: base -= 360; lons = [l - 360 for l in lons]
    return [(l, la) for l, (lo, la) in zip(lons, ring)]


def draw_ring(d, ring, fill, width=None):
    pts0 = unwrap(ring)
    for shift in (-360, 0, 360):
        pts = [((lo + shift - lon0) * PX, (90 - la) / 180 * H) for lo, la in pts0]
        xs = [p[0] for p in pts]
        if max(xs) < 0 or min(xs) > W:
            continue
        if width:
            if len(pts) > 1: d.line(pts, fill=fill, width=width)
        elif len(pts) >= 3:
            d.polygon(pts, fill=fill)


img = Image.new('RGBA', (W, H), SEA)
d = ImageDraw.Draw(img)
for name in ('ne_10m_land', 'ne_10m_minor_islands'):
    for shp in shapefile.Reader(NE + name).shapes():
        parts = list(shp.parts) + [len(shp.points)]
        for i in range(len(parts) - 1):
            ring = shp.points[parts[i]:parts[i + 1]]
            if len(ring) < 3: continue
            area = sum(ring[k - 1][0] * ring[k][1] - ring[k][0] * ring[k - 1][1] for k in range(len(ring)))
            hole = area > 0
            draw_ring(d, ring, SEA if hole else LAND)
# big lakes as sea colour so they look like water (ships cannot reach them anyway)
for shp in shapefile.Reader(NE + 'ne_10m_lakes').shapes():
    parts = list(shp.parts) + [len(shp.points)]
    for i in range(len(parts) - 1):
        ring = shp.points[parts[i]:parts[i + 1]]
        if len(ring) < 3: continue
        bx = shp.bbox
        if (bx[2] - bx[0]) * (bx[3] - bx[1]) < 0.5: continue   # small lakes skipped
        draw_ring(d, ring, SEA)
for shp in shapefile.Reader(NE + 'ne_10m_reefs').shapes():
    parts = list(shp.parts) + [len(shp.points)]
    for i in range(len(parts) - 1):
        draw_ring(d, shp.points[parts[i]:parts[i + 1]], LAND, width=2)

boxes = [(0, 0), (qw, 0), (0, qw // 2), (qw, qw // 2)]
for i, (x, y) in enumerate(boxes):
    img.crop((x, y, x + qw, y + qw // 2)).save(os.path.join(out, f'{prefix}{i}.png'))
# water mask at quad size: alpha 255 = land
small = np.array(img.resize((qw, qw // 2), Image.NEAREST))
land = small[:, :, 0] < 40
mask = np.zeros((qw // 2, qw, 4), dtype=np.uint8)
mask[:, :, :3] = 255
mask[:, :, 3] = np.where(land, 255, 0)
Image.fromarray(mask, 'RGBA').save(os.path.join(out, f'{prefix}Watermask.png'))
img.resize((2048, 1024), Image.LANCZOS).save(os.path.join(out, 'preview.png'))
print('done', W, H, 'land fraction', float(land.mean()))
