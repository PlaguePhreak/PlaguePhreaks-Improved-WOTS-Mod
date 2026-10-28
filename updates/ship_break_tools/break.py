# Break a ship OBJ in two at z = cut (game units, + = bow) with a torn, jagged edge, crumpled plating, a dark
# burnt interior (inner walls + a bulkhead) and burnt plating along the tear.
# python3 break.py -- in.obj cut out_prefix [seed]
#   writes <out_prefix>_bow.obj and <out_prefix>_stern.obj (+ .mtl), pieces left exactly in place.
import bpy, bmesh, sys, math, random, mathutils
from mathutils import Vector, noise
a=sys.argv[sys.argv.index('--')+1:]
src, cut, outp = a[0], float(a[1]), a[2]
seed=int(a[3]) if len(a)>3 else 1
DECK=float(a[4]) if len(a)>4 else 0.36   # deckLevel from <ship>_data.txt (game units above the waterline)
random.seed(seed)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src, forward_axis='NEGATIVE_Z', up_axis='Y')
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
# drop rigging (thin wires look wrong torn) and join everything
for o in objs:
    if any(s.material and s.material.name.startswith('rigging') for s in o.material_slots): bpy.data.objects.remove(o)
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join()
ship=bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
burnt=bpy.data.materials.new('burnt'); burnt.use_nodes=True
ship.data.materials.append(burnt); BURNT=len(ship.data.materials)-1
hullIdx=[i for i,m in enumerate(ship.data.materials) if m and m.name.startswith('hull')]
# Blender axes after import: game z (bow) = Blender -Y?  find it from the bounds: game z is the long axis
def gz(v):   # game z of a Blender point
    return -v.y
def gy(v): return v.z
def gx(v): return -v.x   # OBJ x is game -x; Blender x = OBJ x
ext=[max(gz(v.co) for v in ship.data.vertices), min(gz(v.co) for v in ship.data.vertices)]
L=ext[0]-ext[1]
ymin=min(v.co.z for v in ship.data.vertices); ymax=max(v.co.z for v in ship.data.vertices)
off=Vector((random.random()*50,random.random()*50,random.random()*50))
def tear(bx,by):
    # jagged tear surface: the cut in game z at Blender (x, height)
    p=Vector((bx*3.0,by*3.0,0))+off
    n=noise.fractal(p,0.6,2.2,4)*0.11 + noise.noise(Vector((bx*0.7,by*0.7,1))+off)*0.18
    return cut+n
# 1) refine the mesh around the cut so the tear can follow the noise
bm=bmesh.new(); bm.from_mesh(ship.data)
step=0.045
def near(f): 
    c=f.calc_center_median(); return abs(gz(c)-cut)<0.75 or any(abs(gz(v.co)-cut)<0.45 for v in f.verts)
for k in range(-9,10):
    geom=[e for e in bm.edges]+[f for f in bm.faces if near(f)]
    geom=list({id(g):g for g in geom}.values())
    zz=cut+k*step*1.5
    bmesh.ops.bisect_plane(bm, geom=[f for f in bm.faces if near(f)]+list({e for f in bm.faces if near(f) for e in f.edges})+list({v for f in bm.faces if near(f) for v in f.verts}), plane_co=Vector((0,-zz,0)), plane_no=Vector((0,1,0)))
for ax,lo,hi in ((2,ymin,ymax),(0,-1.2,1.2)):
    t=lo
    while t<hi:
        fs=[f for f in bm.faces if near(f)]
        geom=fs+list({e for f in fs for e in f.edges})+list({v for f in fs for v in f.verts})
        co=Vector((0,0,0)); no=Vector((0,0,0)); co[ax]=t; no[ax]=1
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
        t+=step
bm.to_mesh(ship.data); bm.free()
print("refined", len(ship.data.polygons))
def make_piece(bow):
    o=ship.copy(); o.data=ship.data.copy(); bpy.context.scene.collection.objects.link(o)
    o.name='bow' if bow else 'stern'
    bm=bmesh.new(); bm.from_mesh(o.data)
    kill=[]
    for f in bm.faces:
        c=f.calc_center_median()
        side=gz(c)>tear(c.x,c.z)
        if side!=bow: kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.verts.ensure_lookup_table()
    # 2) crumple the plating along the tear and burn it
    sgn=1 if bow else -1
    for v in bm.verts:
        d=(gz(v.co)-tear(v.co.x,v.co.z))*sgn     # distance into the piece
        if d<0.22:
            w=1-max(d,0)/0.22
            n=noise.noise_vector(v.co*9+off)
            v.co+=Vector((n.x*0.035, n.y*0.05, n.z*0.03 - 0.025))*w
            # plating bends outward a little at the edge
            v.co.x+= math.copysign(0.025*w*w, v.co.x)
    for f in bm.faces:
        c=f.calc_center_median(); d=(gz(c)-tear(c.x,c.z))*sgn
        if d<0.07+0.05*noise.noise(c*5+off): f.material_index=BURNT
    # 3) dark inner walls: hull faces near the break, copied, flipped and pulled inward
    inner=[f for f in bm.faces if f.material_index in hullIdx or f.material_index==BURNT]
    inner=[f for f in inner if (gz(f.calc_center_median())-cut)*sgn<1.3 and f.calc_center_median().z<DECK+0.03]
    ret=bmesh.ops.duplicate(bm, geom=inner)
    nf=[g for g in ret['geom'] if isinstance(g,bmesh.types.BMFace)]
    nv={g for g in ret['geom'] if isinstance(g,bmesh.types.BMVert)}
    for v in nv: v.co.x*=0.96; v.co.z=v.co.z*0.98+0.005
    for f in nf: f.material_index=BURNT
    bmesh.ops.reverse_faces(bm, faces=nf)
    # 4) a torn bulkhead a little way in, so you can't see down the empty hull
    zb=cut+sgn*0.75
    pts=[]
    for e in bm.edges:
        if not (e.link_faces and e.link_faces[0].material_index in hullIdx): continue
        a1,b1=e.verts[0].co,e.verts[1].co
        za,zb2=gz(a1),gz(b1)
        if (za-zb)*(zb2-zb)<0:
            t=(zb-za)/(zb2-za); p=a1.lerp(b1,t)
            if p.z<=DECK+0.02: pts.append((p.x,p.z))
    if len(pts)>=3:
        import itertools
        pts=sorted(set((round(x,3),round(y,3)) for x,y in pts))
        def cross(o_,a_,b_): return (a_[0]-o_[0])*(b_[1]-o_[1])-(a_[1]-o_[1])*(b_[0]-o_[0])
        lo=[];up=[]
        for p in pts:
            while len(lo)>=2 and cross(lo[-2],lo[-1],p)<=0: lo.pop()
            lo.append(p)
        for p in reversed(pts):
            while len(up)>=2 and cross(up[-2],up[-1],p)<=0: up.pop()
            up.append(p)
        hullpts=lo[:-1]+up[:-1]
        cx=sum(p[0] for p in hullpts)/len(hullpts); cy=sum(p[1] for p in hullpts)/len(hullpts)
        cv=bm.verts.new((cx,-zb,cy)); ring=[bm.verts.new((x*0.97,-zb+random.uniform(-0.03,0.03),y)) for x,y in hullpts]
        for i in range(len(ring)):
            f=bm.faces.new((cv,ring[i],ring[(i+1)%len(ring)]) if bow else (cv,ring[(i+1)%len(ring)],ring[i]))
            f.material_index=BURNT
        # internal decks between the tear and the bulkhead, torn at the break
        ys=[p[1] for p in hullpts]; ylo,yhi=min(ys),max(ys)
        for h in (ylo+(yhi-ylo)*0.35, ylo+(yhi-ylo)*0.62):
            xs=[]
            for i in range(len(hullpts)):
                (x1,y1),(x2,y2)=hullpts[i],hullpts[(i+1)%len(hullpts)]
                if (y1-h)*(y2-h)<0: xs.append(x1+(h-y1)/(y2-y1)*(x2-x1))
            if len(xs)<2: continue
            hw=(max(xs)-min(xs))/2*0.95; xc=(max(xs)+min(xs))/2
            nx=8; rows=[]
            for i in range(nx+1):
                x=xc-hw+2*hw*i/nx
                zt=tear(x,h)+sgn*random.uniform(0.0,0.12)
                rows.append((bm.verts.new((x,-zt,h+random.uniform(-0.01,0.01))), bm.verts.new((x,-zb,h))))
            rows2=[(bm.verts.new(a_.co+Vector((0,0,-0.006))), bm.verts.new(b_.co+Vector((0,0,-0.006)))) for a_,b_ in rows]
            for i in range(nx):
                q=(rows[i][0],rows[i+1][0],rows[i+1][1],rows[i][1])
                f=bm.faces.new(q if bow else tuple(reversed(q))); f.material_index=BURNT
                q2=(rows2[i][0],rows2[i+1][0],rows2[i+1][1],rows2[i][1])
                f2=bm.faces.new(tuple(reversed(q2)) if bow else q2); f2.material_index=BURNT
    # bent plates: a few hull panels at the tear folded outwards
    edge=[f for f in bm.faces if f.material_index==BURNT and f.calc_area()>0.0004 and abs(f.normal.x)>0.6]
    random.shuffle(edge)
    for f in edge[:14]:
        r2=bmesh.ops.duplicate(bm, geom=[f]); g=[x for x in r2['geom'] if isinstance(x,bmesh.types.BMFace)][0]
        piv=g.calc_center_median(); ang=random.uniform(0.4,1.1)*(1 if piv.x>0 else -1)
        R=mathutils.Matrix.Rotation(ang*sgn,3,'Z')
        for v in g.verts:
            d=v.co-piv; v.co=piv+R@d+Vector((math.copysign(0.03,piv.x),0,0))
        bmesh.ops.scale(bm, vec=Vector((1.2,1.2,1.2)), space=mathutils.Matrix.Translation(-piv), verts=list(g.verts))
        g2=bmesh.ops.duplicate(bm, geom=[g]); gf=[x for x in g2['geom'] if isinstance(x,bmesh.types.BMFace)][0]
        bmesh.ops.reverse_faces(bm, faces=[gf])
    # burnt UVs: box projection so the soot texture isn't stretched
    uv=bm.loops.layers.uv.active
    for f in bm.faces:
        if f.material_index==BURNT:
            nrm=f.normal; axis=max(range(3),key=lambda i:abs(nrm[i]))
            for l in f.loops:
                c=l.vert.co; u=[c.y,c.x,c.x][axis]; w_=[c.z,c.z,c.y][axis]
                l[uv].uv=(u*1.5,w_*1.5)
    bm.normal_update(); bm.to_mesh(o.data); bm.free()
    return o
bow=make_piece(True); stern=make_piece(False)
bpy.data.objects.remove(ship)
# soot texture
import numpy as np
N=512; img=bpy.data.images.new('burnt',N,N)
n1=np.zeros((N,N)); n2=np.zeros((N,N))
for yy in range(N):
    for xx in range(N):
        q=Vector((xx/N*6,yy/N*6,0.5))
        n1[yy,xx]=noise.fractal(q,0.8,2.0,5, noise_basis='PERLIN_ORIGINAL')
        n2[yy,xx]=noise.noise(q*2.3+Vector((7,3,1)), noise_basis='VORONOI_F1')
soot=np.clip(0.09+0.06*n1,0.02,0.3)
streak=np.clip(n2,0,1)*0.10
rust=np.clip(n1*0.6-0.15,0,1)*0.35
rgb=np.stack([soot+streak+rust*0.55, soot+streak*0.95+rust*0.25, soot+streak*0.9+rust*0.08],-1)
px=np.concatenate([rgb,np.ones((N,N,1))],-1).astype(np.float32)
img.pixels.foreach_set(px.ravel()); img.filepath_raw=outp.rsplit('/',1)[0]+'/burnt.png'; img.file_format='PNG'; img.save()
nt=burnt.node_tree; t=nt.nodes.new('ShaderNodeTexImage'); t.image=img
nt.links.new(t.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
nt.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.95
for o,nm in ((bow,'bow'),(stern,'stern')):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
    bpy.ops.wm.obj_export(filepath=f"{outp}_{nm}.obj", export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y', path_mode='STRIP', export_normals=True, export_uv=True, export_materials=True)
    print(nm, len(o.data.vertices), "verts")
