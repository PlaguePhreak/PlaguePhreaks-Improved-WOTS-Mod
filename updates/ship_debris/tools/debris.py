# Ship debris kit (Claude, 28 Oct 2026). Headless Blender (bpy).
#   python3 debris.py -- <atlas.png> <out_dir>
# Writes one OBJ per piece (metres, Y up, like the parachute pack; the game scales x0.1), debris_kit.fbx (all pieces
# laid out for review in Blender) and debris_kit.blend. All pieces share debris_atlas.png (4x4 tiles, see tex.py).
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix, noise
a=sys.argv[sys.argv.index('--')+1:]
ATLAS, OUT = a[0], a[1]; os.makedirs(OUT, exist_ok=True)
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------- helpers ----------
def new_bm(): 
    bm=bmesh.new(); bm.faces.layers.int.new('tile'); bm.faces.layers.int.new('raw'); bm.loops.layers.uv.new('rawuv'); return bm
def L(bm,n): return bm.faces.layers.int[n]
def box(bm, cx,cy,cz, lx,ly,lz, tile, nx=1, rot=None):
    """segmented box (nx segments along x). returns its verts grouped as rings"""
    rings=[]
    for i in range(nx+1):
        x=cx-lx/2+lx*i/nx
        r=[bm.verts.new((x,cy+sy*ly/2,cz+sz*lz/2)) for sy,sz in ((-1,-1),(1,-1),(1,1),(-1,1))]
        rings.append(r)
    fs=[]
    for i in range(nx):
        a,b=rings[i],rings[i+1]
        for k in range(4):
            fs.append(bm.faces.new((a[k],a[(k+1)%4],b[(k+1)%4],b[k])))
    fs.append(bm.faces.new(tuple(reversed(rings[0])))); fs.append(bm.faces.new(tuple(rings[-1])))
    for f in fs: f[L(bm,'tile')]=tile
    if rot is not None:
        bmesh.ops.rotate(bm, verts=[v for r in rings for v in r], cent=(cx,cy,cz), matrix=rot)
    return rings, fs
def cyl(bm, cx,cy,cz, r, h, seg, tile, axis='z', capTile=None, rings_z=None):
    """cylinder along axis with optional extra rings (list of (t 0..1, radius scale)); raw UV u = angle"""
    zs=rings_z or [(0,1),(1,1)]
    rings=[]
    for t,s in zs:
        rr=[]
        for k in range(seg):
            ang=2*math.pi*k/seg; p=Vector((r*s*math.cos(ang), r*s*math.sin(ang), -h/2+h*t))
            if axis=='x': p=Vector((p.z,p.x,p.y))
            if axis=='y': p=Vector((p.x,p.z,p.y))
            rr.append(bm.verts.new(p+Vector((cx,cy,cz))))
        rings.append(rr)
    fs=[]
    for i in range(len(rings)-1):
        for k in range(seg):
            f=bm.faces.new((rings[i][k],rings[i][(k+1)%seg],rings[i+1][(k+1)%seg],rings[i+1][k]))
            f[L(bm,'tile')]=tile; f[L(bm,'raw')]=1
            for lp in f.loops:
                kk=rings[i].index(lp.vert) if lp.vert in rings[i] else rings[i+1].index(lp.vert)
                ii=i if lp.vert in rings[i] else i+1
                u=kk/seg
                if kk==0 and any(rings[i][seg-1] is l2.vert or rings[i+1][seg-1] is l2.vert for l2 in f.loops): u=1.0
                lp[bm.loops.layers.uv['rawuv']].uv=(u, zs[ii][0])
            fs.append(f)
    ct=capTile if capTile is not None else tile
    for rr,rev in ((rings[0],True),(rings[-1],False)):
        f=bm.faces.new(tuple(reversed(rr)) if rev else tuple(rr)); f[L(bm,'tile')]=ct; fs.append(f)
    return rings, fs
def torus(bm, R, r, segU, segV, tile, sx=1.0, sy=1.0, cz=0.0):
    vs=[[None]*segV for _ in range(segU)]
    for i in range(segU):
        a=2*math.pi*i/segU
        for j in range(segV):
            b=2*math.pi*j/segV
            rr=R+r*math.cos(b)
            vs[i][j]=bm.verts.new((rr*math.cos(a)*sx, rr*math.sin(a)*sy, cz+r*math.sin(b)))
    for i in range(segU):
        for j in range(segV):
            i2,j2=(i+1)%segU,(j+1)%segV
            f=bm.faces.new((vs[i][j],vs[i2][j],vs[i2][j2],vs[i][j2]))
            f[L(bm,'tile')]=tile; f[L(bm,'raw')]=1
            uvl=bm.loops.layers.uv['rawuv']
            for lp,(ii,jj) in zip(f.loops,((i,j),(i+1,j),(i+1,j+1),(i,j+1))):
                lp[uvl].uv=(ii/segU, jj/segV)
def jitter(vs, amt, seed=0, axes=(1,1,1)):
    for v in vs:
        n=noise.noise_vector(v.co*3.1+Vector((seed,seed*2,seed*3)))
        v.co+=Vector((n.x*axes[0],n.y*axes[1],n.z*axes[2]))*amt
def splinter(ring, dx, sgn):
    # pull the corners of an end ring out by different amounts: a torn, splintered end
    for k,v in enumerate(ring):
        v.co.x+=sgn*dx*random.choice((0.0,0.35,1.0,0.6))
        v.co.y*=random.uniform(0.6,1.0); v.co.z*=random.uniform(0.7,1.0)

def finish(bm, name):
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts)>4])
    # final UVs: box projection (or the raw UV) scaled into the face's atlas tile
    uv=bm.loops.layers.uv.new('UVMap'); raw=bm.loops.layers.uv['rawuv']
    mn=Vector((min(v.co.x for v in bm.verts),min(v.co.y for v in bm.verts),min(v.co.z for v in bm.verts)))
    mx=Vector((max(v.co.x for v in bm.verts),max(v.co.y for v in bm.verts),max(v.co.z for v in bm.verts)))
    size=max((mx-mn).x,(mx-mn).y,(mx-mn).z,1e-3)
    ins=0.012
    for f in bm.faces:
        t=f[L(bm,'tile')]; r,c=divmod(t,4); u0=c/4; v0=1-(r+1)/4
        n=f.normal; ax=max(range(3),key=lambda i:abs(n[i]))
        for lp in f.loops:
            if f[L(bm,'raw')]: p=Vector(lp[raw].uv)
            else:
                q=(lp.vert.co-mn)/size
                p=Vector((q.y,q.z)) if ax==0 else (Vector((q.x,q.z)) if ax==1 else Vector((q.x,q.y)))
            p.x=min(max(p.x,0),1); p.y=min(max(p.y,0),1)
            lp[uv].uv=(u0+ins+p.x*(0.25-2*ins), v0+ins+p.y*(0.25-2*ins))
    bm.loops.layers.uv.remove(raw)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=False
    ob=bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(MAT)
    return ob
def smooth_parts(ob):
    ob.data.shade_smooth() if hasattr(ob.data,'shade_smooth') else None

# material with the atlas
MAT=bpy.data.materials.new('debris'); MAT.use_nodes=True
nt=MAT.node_tree; bsdf=nt.nodes.get('Principled BSDF'); img=nt.nodes.new('ShaderNodeTexImage')
img.image=bpy.data.images.load(ATLAS); nt.links.new(img.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=0.85

pieces=[]
# 1 plank: long splintered deck plank
bm=new_bm(); rings,_=box(bm,0,0,0,3.6,0.22,0.06,0,nx=6)
splinter(rings[0],0.35,-1); splinter(rings[-1],0.5,1); jitter([v for r in rings[1:-1] for v in r],0.01,1)
pieces.append(finish(bm,'plank'))
# 2 plank_short: broken plank, burnt along one end
bm=new_bm(); rings,fs=box(bm,0,0,0,1.6,0.24,0.06,0,nx=4)
for f in fs:
    if f.calc_center_median().x>0.35: f[L(bm,'tile')]=1
splinter(rings[0],0.25,-1); splinter(rings[-1],0.3,1)
pieces.append(finish(bm,'plank_short'))
# 3 deck_section: 6 deck planks of uneven length on two cross beams
bm=new_bm()
for i in range(6):
    y=-0.6+0.205*i+0.1; ln=random.uniform(1.6,2.6); x0=random.uniform(-0.25,0.25)
    rings,_=box(bm,x0,y,0.0,ln,0.195,0.07,0 if i%3 else 1,nx=3); splinter(rings[0],0.25,-1); splinter(rings[-1],0.3,1)
for x in (-0.55,0.6):
    box(bm,x,0,-0.1,0.14,1.35,0.13,0,rot=Matrix.Rotation(math.radians(random.uniform(-4,4)),3,'Z'))
pieces.append(finish(bm,'deck_section'))
# 4 crate
bm=new_bm(); box(bm,0,0,0,0.8,0.56,0.56,2)
for x in (-0.36,0,0.36): box(bm,x,0,0,0.06,0.6,0.6,0)
pieces.append(finish(bm,'crate'))
# 5 drum (55 gal / 200 l), two rolling hoops, a dent
bm=new_bm()
prof=[(0,0.97),(0.02,1),(0.32,1),(0.335,1.05),(0.35,1),(0.65,1),(0.665,1.05),(0.68,1),(0.98,1),(1,0.97)]
rings,_=cyl(bm,0,0,0,0.29,0.88,14,5,axis='z',capTile=12,rings_z=prof)
for v in rings[5]+rings[6]:
    if v.co.x>0.2: v.co.x-=0.04
pieces.append(finish(bm,'drum'))
# 6 ammo box (olive), lid lip and a handle
bm=new_bm(); box(bm,0,0,0,0.62,0.3,0.28,6); box(bm,0,0,0.12,0.64,0.32,0.05,6); box(bm,0,0,0.165,0.18,0.03,0.04,12)
pieces.append(finish(bm,'ammo_box'))
# 7 Carley float: oval ring tube with a slatted floor (the raft every navy carried)
bm=new_bm(); torus(bm,0.95,0.17,22,7,7,sx=1.55,sy=0.75)
for i in range(5): box(bm,-1.1+0.55*i,0,-0.08,0.07,1.1-0.35*abs(i-2)**1.4,0.03,15)
box(bm,0,0,-0.07,2.4,0.07,0.03,15)
pieces.append(finish(bm,'carley_float'))
# 8 life ring (white with 4 red bands)
bm=new_bm(); torus(bm,0.36,0.075,20,8,8); pieces.append(finish(bm,'life_ring'))
# 9 hatch cover: planks in a steel frame
bm=new_bm()
for i in range(6): box(bm,0,-0.5+0.2*i,0,1.2,0.19,0.07,0)
for y in (-0.62,0.62): box(bm,0,y,0.01,1.3,0.06,0.1,3)
for x in (-0.62,0.62): box(bm,x,0,0.01,0.06,1.3,0.1,3)
pieces.append(finish(bm,'hatch_cover'))
# 10 steel plate: torn, bent, scorched
bm=new_bm(); nx,ny=8,5; lx,ly,th=2.2,1.4,0.03; grid={}
for side in (0,1):
    for i in range(nx+1):
        for j in range(ny+1):
            x=-lx/2+lx*i/nx; y=-ly/2+ly*j/ny
            if i in (0,nx) or j in (0,ny): x+=random.uniform(-0.08,0.08); y+=random.uniform(-0.08,0.08)
            z=0.25*math.sin(x*1.3)+0.12*(y/ly)**2+0.04*noise.noise(Vector((x,y,3))) + (th if side else 0)
            grid[side,i,j]=bm.verts.new((x,y,z))
for side in (0,1):
    for i in range(nx):
        for j in range(ny):
            q=(grid[side,i,j],grid[side,i+1,j],grid[side,i+1,j+1],grid[side,i,j+1])
            f=bm.faces.new(q if side else tuple(reversed(q))); f[L(bm,'tile')]=4 if side else 12
edge=[(i,0) for i in range(nx)]+[(nx,j) for j in range(ny)]+[(i,ny) for i in range(nx,0,-1)]+[(0,j) for j in range(ny,0,-1)]
nxt={(i,0):(i+1,0) for i in range(nx)}; nxt.update({(nx,j):(nx,j+1) for j in range(ny)}); nxt.update({(i,ny):(i-1,ny) for i in range(nx,0,-1)}); nxt.update({(0,j):(0,j-1) for j in range(ny,0,-1)})
for e in edge:
    e2=nxt[e]; f=bm.faces.new((grid[0,e[0],e[1]],grid[0,e2[0],e2[1]],grid[1,e2[0],e2[1]],grid[1,e[0],e[1]])); f[L(bm,'tile')]=11
pieces.append(finish(bm,'steel_plate'))
# 11 spar: broken mast / boom, splintered and charred at the break
bm=new_bm(); prof=[(0,1),(0.3,0.97),(0.6,0.93),(0.9,0.9),(1,0.85)]
rings,fs=cyl(bm,0,0,0,0.12,4.8,8,0,axis='x',capTile=11,rings_z=prof)
for v in rings[-1]: v.co.x+=random.choice((0,0.15,0.45,0.25)); v.co.y*=random.uniform(0.5,1); v.co.z*=random.uniform(0.5,1)
for f in fs:
    if f.calc_center_median().x>1.8: f[L(bm,'tile')]=1
pieces.append(finish(bm,'spar'))
# 12 kapok life vest (two lumpy pads)
bm=new_bm()
for y in (-0.13,0.13):
    rings,_=box(bm,0,y,0,0.55,0.24,0.1,9,nx=3); jitter([v for r in rings for v in r],0.015,int(y*100))
pieces.append(finish(bm,'life_vest'))
# 13 capsized ship's boat (whaleboat, 7.6 m), keel up: red bottom and keel above the water, white sheer below
bm=new_bm(); Lb,Bb,Db=7.6,2.1,0.95; nL,nV=14,7; vs={}
for i in range(nL+1):
    t=-1+2*i/nL; x=t*Lb/2
    hw=Bb/2*(1-abs(t)**2.4)**0.55+0.02; dep=Db*(1-0.25*abs(t)**3)
    for j in range(-nV,nV+1):
        s=j/nV; ang=s*math.pi/2
        y=hw*math.sin(ang); z=Db*0.15-dep*math.cos(ang)**1.5   # section: round bilge
        vs[i,j]=bm.verts.new((x,y,z))
for i in range(nL):
    for j in range(-nV,nV):
        f=bm.faces.new((vs[i,j],vs[i+1,j],vs[i+1,j+1],vs[i,j+1]))
        zc=f.calc_center_median().z; f[L(bm,'tile')]=13 if zc< -0.25 else 14
box(bm,0,0,Db*0.15-Db-0.05,Lb*0.8,0.08,0.14,13,nx=4)   # keel
# gunwale cap closes the open top (seen from below the water only, but keeps it solid)
for i in range(nL):
    f=bm.faces.new((vs[i,nV],vs[i,-nV],vs[i+1,-nV],vs[i+1,nV])); f[L(bm,'tile')]=0
bmesh.ops.rotate(bm, verts=bm.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.pi,3,'X'))   # keel up
pieces.append(finish(bm,'boat_capsized'))
# 14 charred timber chunk
bm=new_bm(); rings,fs=box(bm,0,0,0,1.1,0.32,0.22,11,nx=3)
splinter(rings[0],0.2,-1); splinter(rings[-1],0.25,1); jitter([v for r in rings for v in r],0.03,5)
for f in fs:
    if abs(f.normal.z)>0.7 and f.calc_center_median().z>0: f[L(bm,'tile')]=1
pieces.append(finish(bm,'timber_burnt'))

# ---------- export ----------
info=[]
for ob in pieces:
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT,'debris_'+ob.name+'.obj'), export_selected_objects=True,
        export_materials=False, forward_axis='NEGATIVE_Z', up_axis='Y', export_triangulated_mesh=True)
    d=ob.dimensions; info.append(f'{ob.name:14s} {len(ob.data.polygons):4d} faces  {d.x:.2f} x {d.y:.2f} x {d.z:.2f} m')
# lay them out in a grid for the FBX/blend review copy
for k,ob in enumerate(pieces):
    ob.location=((k%5)*5.0-10, -(k//5)*4.0+4, 0)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=os.path.join(OUT,'debris_kit.fbx'), use_selection=True, add_leaf_bones=False,
    path_mode='COPY', embed_textures=True, axis_forward='-Z', axis_up='Y')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'debris_kit.blend'))
open(os.path.join(OUT,'debris_list.txt'),'w').write('\n'.join(info)+'\n')
print('\n'.join(info))
