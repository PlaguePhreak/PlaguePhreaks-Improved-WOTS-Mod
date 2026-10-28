# Builds a WWII round parachute: 24-gore canopy (scalloped skirt, apex vent), suspension lines to two risers.
# Origin = the harness point, canopy above it (+Z in Blender = up). Sizes in metres.
import bpy, bmesh, math, sys
from PIL import Image, ImageDraw
args=sys.argv[sys.argv.index('--')+1:]
name, col, seam, out = args[0], tuple(int(x) for x in args[1].split(',')), tuple(int(x) for x in args[2].split(',')), args[3]
GORES=24; R=3.6; H=2.3; RINGS=7; LINE_TOP=6.4; VENT=0.25
# texture: left half = panel shade A, right half = shade B, dark seam stripes at the edges
img=Image.new('RGB',(256,256),col); d=ImageDraw.Draw(img)
shadeB=tuple(max(0,c-18) for c in col)
d.rectangle([128,0,255,255],fill=shadeB)
for x in (0,1,126,127,128,129,254,255): d.line([(x,0),(x,255)],fill=seam)
d.rectangle([0,250,255,255],fill=seam)  # skirt band
tex=out.replace('.fbx','_tex.png'); img.save(tex)
bpy.ops.wm.read_factory_settings(use_empty=True)
mesh=bpy.data.meshes.new(name+'_canopy'); bm=bmesh.new(); uv=bm.loops.layers.uv.new()
def pt(i,j):
    # i: gore edge index, j: ring (0 = apex vent, RINGS = skirt)
    t=j/RINGS; a=2*math.pi*i/GORES
    r=VENT+(R-VENT)*math.sin(t*math.pi/2)
    z=LINE_TOP+H*math.cos(t*math.pi/2)
    return (r*math.cos(a), r*math.sin(a), z)
def mid(i,j,bulge):
    t=j/RINGS; a=2*math.pi*(i+0.5)/GORES
    r=(VENT+(R-VENT)*math.sin(t*math.pi/2))*math.cos(math.pi/GORES)+bulge*math.sin(t*math.pi)
    z=LINE_TOP+H*math.cos(t*math.pi/2)
    if j==RINGS: z+=0.14   # scalloped skirt: gore centre rides up between lines
    return (r*math.cos(a), r*math.sin(a), z)
V={}
for i in range(GORES+1):
    for j in range(RINGS+1): V[('e',i%GORES,j)]=V.get(('e',i%GORES,j)) or bm.verts.new(pt(i,j))
for i in range(GORES):
    for j in range(RINGS+1): V[('m',i,j)]=bm.verts.new(mid(i,j,0.18))
off=0.0
for i in range(GORES):
    u0,u1=(0.0,0.5) if i%2==0 else (0.5,1.0); um=(u0+u1)/2
    for j in range(RINGS):
        for (a,b,ua,ub) in ((('e',i,j),('m',i,j),u0,um),(('m',i,j),('e',(i+1)%GORES,j),um,u1)):
            a2=(a[0],a[1],j+1); b2=(b[0],b[1],j+1)
            f=bm.faces.new((V[a],V[b],V[b2],V[a2]))
            for l,(u,v) in zip(f.loops,((ua,1-j/RINGS),(ub,1-j/RINGS),(ub,1-(j+1)/RINGS),(ua,1-(j+1)/RINGS))): l[uv].uv=(u,v)
bm.normal_update()
# inside faces too (seen from below in game): duplicate and flip
geom=bm.faces[:]
dup=bmesh.ops.duplicate(bm,geom=geom)
inner=[g for g in dup['geom'] if isinstance(g,bmesh.types.BMFace)]
bmesh.ops.reverse_faces(bm,faces=inner)
for f in inner:
    for v in f.verts: v.co=v.co-f.normal*0.0  # same place, faces opposite way
bm.to_mesh(mesh); bm.free()
can=bpy.data.objects.new(name+'_canopy',mesh); bpy.context.scene.collection.objects.link(can)
for p in mesh.polygons: p.use_smooth=True
# suspension lines: from each gore edge at the skirt down to two riser points just above the harness
lm=bpy.data.meshes.new(name+'_lines'); bm=bmesh.new(); uv=bm.loops.layers.uv.new()
risers=[(0.30,0,1.1),(-0.30,0,1.1)]   # wide enough to pass beside the airman's head
def tube(p,q,w=0.012):
    import mathutils
    p=mathutils.Vector(p); q=mathutils.Vector(q); dvec=(q-p).normalized()
    s=dvec.cross(mathutils.Vector((0,0,1)))
    if s.length<1e-4: s=mathutils.Vector((1,0,0))
    s.normalize(); t=dvec.cross(s)
    ring=lambda c:[bm.verts.new(c+(s*math.cos(k*math.pi/2)+t*math.sin(k*math.pi/2))*w) for k in range(4)]
    A,B=ring(p),ring(q)
    for k in range(4):
        f=bm.faces.new((A[k],A[(k+1)%4],B[(k+1)%4],B[k]))
        for l in f.loops: l[uv].uv=(0.02,0.02)
for i in range(GORES):
    p=pt(i,RINGS); r=risers[0] if p[0]>=0 else risers[1]
    tube(p,r)
import os   # riser ends: the new airman's harness D-rings (origin = midway between them); env HARNESS_X overrides
HX=float(os.environ.get('HARNESS_X','0.073')); HARNESS=[(HX,0,0),(-HX,0,0)]
for r,h in zip(risers,HARNESS): tube(r,h,0.025)   # webbing risers down to the shoulders
bm.to_mesh(lm); bm.free()
lines=bpy.data.objects.new(name+'_lines',lm); bpy.context.scene.collection.objects.link(lines)
mat=bpy.data.materials.new(name+'_mat'); mat.use_nodes=True
nt=mat.node_tree; t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(tex)
nt.links.new(t.outputs['Color'],nt.nodes['Principled BSDF'].inputs['Base Color']); nt.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.9
for o in (can,lines): o.data.materials.append(mat)
root=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(root)
for o in (can,lines): o.parent=root
bpy.ops.export_scene.fbx(filepath=out, path_mode='COPY', embed_textures=True)
tri=sum(len(p.vertices)-2 for o in (can,lines) for p in o.data.polygons)
print('triangles',tri)
# preview
import mathutils
sc=bpy.context.scene
c=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(c); c.location=(13,-13,6)
c.rotation_euler=(mathutils.Vector((0,0,4.2))-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.6,0.3,0.8); l.data.energy=3
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.45,0.6,0.8)
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=500; sc.render.resolution_y=500; sc.render.filepath=out.replace('.fbx','.png')
bpy.ops.render.render(write_still=True)
