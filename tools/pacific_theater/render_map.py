"""Render a War on the Sea campaign map (4 quads + water mask) from Natural Earth land polygons.

Usage: python3 render_map.py <lon_west_deg_0_360> <lat_south> <width_deg> <out_dir> [quad_w]
Map is equirectangular, 2:1, north up. Quads: 0=TL 1=TR 2=BL 3=BR.
"""
import sys, os
import shapefile
from PIL import Image, ImageDraw

SEA = (83, 107, 127, 255)
LAND = (0, 0, 0, 255)
NE = '/tmp/claude-0/ne/'

lon0 = float(sys.argv[1]); lat0 = float(sys.argv[2]); wdeg = float(sys.argv[3])
out = sys.argv[4]
qw = int(sys.argv[5]) if len(sys.argv) > 5 else 4096
W, H = qw * 2, qw  # full image; quads are qw x qw/2
hdeg = wdeg / 2
os.makedirs(out, exist_ok=True)

def to_px(lon, lat):
    if lon < lon0 - 1e-9:
        lon += 360
    x = (lon - lon0) / wdeg * W
    y = (lat0 + hdeg - lat) / hdeg * H
    return (x, y)

img = Image.new('RGBA', (W, H), SEA)
d = ImageDraw.Draw(img)
for name in ('ne_10m_land', 'ne_10m_minor_islands'):
    sf = shapefile.Reader(NE + name)
    for shp in sf.shapes():
        bx = shp.bbox
        parts = list(shp.parts) + [len(shp.points)]
        for i in range(len(parts) - 1):
            ring = shp.points[parts[i]:parts[i + 1]]
            # shift ring to 0..360 consistently using its first point
            lons = [p[0] for p in ring]
            shift = 360 if (sum(lons) / len(lons)) < lon0 - 180 or (sum(lons) / len(lons)) < 0 else 0
            pts = []
            for lo, la in ring:
                lo2 = lo + shift
                x = (lo2 - lon0) / wdeg * W
                y = (lat0 + hdeg - la) / hdeg * H
                pts.append((x, y))
            xs = [p[0] for p in pts]
            if max(xs) < 0 or min(xs) > W:
                continue
            if len(pts) < 3:
                continue
            # NE rings: clockwise exterior, counter-clockwise holes
            area = sum(ring[k - 1][0] * ring[k][1] - ring[k][0] * ring[k - 1][1] for k in range(len(ring)))
            hole = area > 0  # shapefile: exterior clockwise (negative), holes counter-clockwise
            d.polygon(pts, fill=SEA if hole else LAND)

# reefs and atolls (lines), like the stock map's atoll rings
for shp in shapefile.Reader(NE + 'ne_10m_reefs').shapes():
    parts = list(shp.parts) + [len(shp.points)]
    for i in range(len(parts) - 1):
        ring = shp.points[parts[i]:parts[i + 1]]
        shift = 360 if sum(p[0] for p in ring) / len(ring) < 0 else 0
        pts = [((lo + shift - lon0) / wdeg * W, (lat0 + hdeg - la) / hdeg * H) for lo, la in ring]
        if len(pts) > 1 and not (max(p[0] for p in pts) < 0 or min(p[0] for p in pts) > W):
            d.line(pts, fill=LAND, width=2)

boxes = [(0, 0), (qw, 0), (0, qw // 2), (qw, qw // 2)]
for i, (x, y) in enumerate(boxes):
    img.crop((x, y, x + qw, y + qw // 2)).save(os.path.join(out, f'pacific{i}.png'))
# water mask: whole map at quad size, white, alpha 255 = land, 0 = sea
small = img.resize((qw, qw // 2), Image.NEAREST)
mask = Image.new('RGBA', small.size, (255, 255, 255, 0))
px = small.load(); mp = mask.load()
for yy in range(small.size[1]):
    for xx in range(small.size[0]):
        if px[xx, yy][0] < 40:
            mp[xx, yy] = (255, 255, 255, 255)
mask.save(os.path.join(out, 'pacificWatermask.png'))
img.resize((2048, 1024), Image.LANCZOS).save(os.path.join(out, 'preview.png'))
print('done', W, H)
