# Break a ship (OBJ from ship2mesh.py) at several cuts. For each cut it writes
#   <out>/<name>_<tag>_bow.obj / _stern.obj   whole pieces, for previews and review
#   <out>/<name>_<tag>.brk                    the in-game "break kit": only the torn band |z-cut| < BAND of each piece
#                                             (torn edge, crumpled + burnt plating, inner walls, bulkhead, decks, bent plates).
# In game the rest of each piece is the ship's own mesh clipped exactly at z = cut +- BAND, so the seam matches.
# blender python: python3 break2.py -- in.obj mats.json outdir name tag:cut[,tag:cut...] [seed]
import bpy, bmesh, sys, math, random, mathutils, json, struct, gzip, os
from mathutils import Vector, noise
a=sys.argv[sys.argv.index('--')+1:]
src, matsfile, outdir, NAME, cutspec = a[0], a[1], a[2], a[3], a[4]
seed=int(a[5]) if len(a)>5 else 1
BAND=0.7
MATS=json.load(open(matsfile))
os.makedirs(outdir, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src, forward_axis='NEGATIVE_Z', up_axis='Y')
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
def gz(v): return -v.y      # game z of a Blender point (bow +)
def gx(v): return -v.x
# deck line from the hull object only (side shell top), sampled along the ship
hullObjs=[o for o in objs if o.name.split('.')[0] in ('Main_LOD0','Hull')]
hp=[o.matrix_world@v.co for o in hullObjs for v in o.data.vertices]
def deck_at(z):
    s=[p for p in hp if abs(gz(p)-z)<0.35]
    if not s: return None
    w=max(abs(p.x) for p in s)
    side=[p.z for p in s if abs(p.x)>0.85*w]
    return max(side) if side else max(p.z for p in s)
def mcls(m):
    if not m: return 'acc'
    k=m.name.split('.')[0]
    return MATS['mats'].get(k,{}).get('cls', k.split('_')[0])
# tag faces: which object, and whether it is a part the game moves (kept whole in game, left out of the kit)
MOV=set(MATS.get('moving',[]))
objc={}
for i,o in enumerate(objs):
    me=o.data
    a1=me.attributes.new('oid','INT','FACE'); a2=me.attributes.new('mov','INT','FACE')
    m=1 if o.name.split('.')[0] in MOV else 0
    for k in range(len(me.polygons)): a1.data[k].value=i; a2.data[k].value=m
    if me.vertices:
        zs=[gz(o.matrix_world@v.co) for v in me.vertices]; objc[i]=(min(zs)+max(zs))/2
# join everything, then drop rigging faces (thin wires look wrong torn)
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join()
base=bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
rig={i for i,m in enumerate(base.data.materials) if mcls(m)=='rigging'}
if rig:
    bm=bmesh.new(); bm.from_mesh(base.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in rig], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(base.data); bm.free()
burnt=bpy.data.materials.new('burnt'); burnt.use_nodes=True
base.data.materials.append(burnt); BURNT=len(base.data.materials)-1
hullIdx=[i for i,m in enumerate(base.data.materials) if mcls(m)=='hull']
ext=[max(gz(v.co) for v in base.data.vertices), min(gz(v.co) for v in base.data.vertices)]
L=ext[0]-ext[1]
ymin=min(v.co.z for v in base.data.vertices); ymax=max(v.co.z for v in base.data.vertices)
xw=max(abs(v.co.x) for v in base.data.vertices)
print("ship", NAME, "L", round(L,2), "z", [round(e,2) for e in ext], "verts", len(base.data.vertices))

def write_brk(path, cut, pieces):
    # BRK2, read by ModWreckArt.LoadKit (no compression: Unity's GZip can be missing in game builds).
    # Game coords: x=-bx, y=bz, z=-by. Winding reversed for Unity. Positions and UVs stored as 16-bit steps of each chunk's box.
    chunks_all=[]
    for side,o in pieces:
        me=o.data; me.calc_loop_triangles()
        cn=me.corner_normals
        uvl=me.uv_layers.active.data if me.uv_layers.active else None
        bymat={}
        for t in me.loop_triangles:
            bymat.setdefault(t.material_index,[]).append(t)
        chunks=[]
        for mi,ts in bymat.items():
            m=me.materials[mi]; key=m.name.split('.')[0] if m else 'none'
            if key=='burnt': mname,cls='burnt','burnt'
            else:
                inf=MATS['mats'].get(key,{'name':key,'cls':key.split('_')[0]}); mname,cls=inf['name'],inf['cls']
            verts={}; P=[];N=[];U=[];I=[]
            def flush():
                if I: chunks.append((mname,cls,P[:],N[:],U[:],I[:]))
            for t in ts:
                if len(P)>64000: flush(); verts.clear(); P.clear(); N.clear(); U.clear(); I.clear()
                tri=[]
                for li in t.loops:
                    vi=me.loops[li].vertex_index
                    co=me.vertices[vi].co; nn=cn[li].vector; uv=uvl[li].uv if uvl else (0,0)
                    k=(vi, round(uv[0],5), round(uv[1],5), round(nn.x,2), round(nn.y,2), round(nn.z,2))
                    j=verts.get(k)
                    if j is None:
                        j=len(P); verts[k]=j
                        P.append((-co.x, co.z, -co.y)); N.append((-nn.x, nn.z, -nn.y)); U.append((uv[0],uv[1]))
                    tri.append(j)
                I.extend((tri[2],tri[1],tri[0]))
            flush()
        chunks_all.append((side,chunks))
    def s(b, t): t=t.encode('utf-8'); b.append(struct.pack('<i',len(t))+t)
    b=[b'BRK2', struct.pack('<ff',cut,BAND)]
    mv=MATS.get('moving',[]); b.append(struct.pack('<i',len(mv)))
    for m in mv: s(b,m)
    b.append(struct.pack('<i',len(chunks_all)))
    def q16(vals, dims):
        lo=[min(v[d] for v in vals) for d in range(dims)]; hi=[max(v[d] for v in vals) for d in range(dims)]
        sc=[(hi[d]-lo[d]) or 1e-6 for d in range(dims)]
        qs=[max(0,min(65535,int(round((v[d]-lo[d])/sc[d]*65535)))) for v in vals for d in range(dims)]
        return lo, sc, qs
    for side,chunks in chunks_all:
        b.append(struct.pack('<bi',side,len(chunks)))
        for mname,cls,P,N,U,I in chunks:
            s(b,mname); s(b,cls)
            b.append(struct.pack('<i',len(P)))
            lo,sc,qs=q16(P,3); b.append(struct.pack('<6f',*lo,*sc)); b.append(struct.pack('<%dH'%len(qs),*qs))
            b.append(struct.pack('<%db'%(3*len(N)),*[max(-127,min(127,int(round(c*127)))) for n in N for c in n]))
            lo,sc,qs=q16(U,2); b.append(struct.pack('<4f',*lo,*sc)); b.append(struct.pack('<%dH'%len(qs),*qs))
            b.append(struct.pack('<i',len(I)))
            b.append(struct.pack('<%dH'%len(I),*I))
    open(path,'wb').write(b''.join(b))
    return os.path.getsize(path)

def do_cut(tag, cut, seed_):
    random.seed(seed_)
    ds=[d for d in (deck_at(cut-0.3),deck_at(cut),deck_at(cut+0.3)) if d is not None]
    DECK=min(ds) if ds else (ymin+(ymax-ymin)*0.35)
    ship=base.copy(); ship.data=base.data.copy(); bpy.context.scene.collection.objects.link(ship)
    off=Vector((random.random()*50,random.random()*50,random.random()*50))
    def tear(bx,by):
        p=Vector((bx*3.0,by*3.0,0))+off
        n=noise.fractal(p,0.6,2.2,4)*0.11 + noise.noise(Vector((bx*0.7,by*0.7,1))+off)*0.18
        return cut+max(-0.38,min(0.38,n))
    bm=bmesh.new(); bm.from_mesh(ship.data)
    ORIG=bm.faces.layers.int.new('orig')
    for f in bm.faces: f[ORIG]=1
    def allg(fs): return fs+list({e for f in fs for e in f.edges})+list({v for f in fs for v in f.verts})
    # 1) exact planes at the band edges, then refine inside the band only
    for zz in (cut-BAND, cut+BAND):
        fs=[f for f in bm.faces if min(gz(v.co) for v in f.verts)<zz<max(gz(v.co) for v in f.verts)]
        bmesh.ops.bisect_plane(bm, geom=allg(fs), plane_co=Vector((0,-zz,0)), plane_no=Vector((0,1,0)))
    def inband(f): return all(abs(gz(v.co)-cut)<=BAND+1e-4 for v in f.verts)
    step=0.07
    for k in range(-9,10):
        zz=cut+k*step
        fs=[f for f in bm.faces if inband(f)]
        bmesh.ops.bisect_plane(bm, geom=allg(fs), plane_co=Vector((0,-zz,0)), plane_no=Vector((0,1,0)))
    for ax,lo,hi,st in ((2,ymin,ymax,0.045),(0,-xw,xw,0.045)):
        t=lo
        while t<hi:
            fs=[f for f in bm.faces if inband(f) and any(abs(gz(v.co)-cut)<0.45 for v in f.verts) and f.calc_area()>st*st*0.5]
            if fs:
                co=Vector((0,0,0)); no=Vector((0,0,0)); co[ax]=t; no[ax]=1
                bmesh.ops.bisect_plane(bm, geom=allg(fs), plane_co=co, plane_no=no)
            t+=st
    bm.to_mesh(ship.data); bm.free()
    def make_piece(bow):
        o=ship.copy(); o.data=ship.data.copy(); bpy.context.scene.collection.objects.link(o)
        o.name=('bow' if bow else 'stern')
        bm=bmesh.new(); bm.from_mesh(o.data); ORIG=bm.faces.layers.int.get('orig')
        MV=bm.faces.layers.int.get('mov'); OI=bm.faces.layers.int.get('oid')
        sgn=1 if bow else -1
        kill=[]
        for f in bm.faces:
            c=f.calc_center_median()
            if f[MV]: side=objc.get(f[OI],0)>cut
            elif abs(gz(c)-cut)<BAND: side=gz(c)>tear(c.x,c.z)
            else: side=gz(c)>cut
            if side!=bow: kill.append(f)
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        bm.verts.ensure_lookup_table()
        # 2) crumple the plating along the tear and burn it (never at the band edge, so the seam stays exact)
        for v in bm.verts:
            dz=abs(gz(v.co)-cut)
            if dz>BAND-0.04 or all(f[MV] for f in v.link_faces): continue
            d=(gz(v.co)-tear(v.co.x,v.co.z))*sgn
            if d<0.22:
                w=(1-max(d,0)/0.22)*min(1,(BAND-0.04-dz)/0.1)
                n=noise.noise_vector(v.co*9+off)
                v.co+=Vector((n.x*0.035, n.y*0.05, n.z*0.03 - 0.025))*w
                v.co.x+= math.copysign(0.025*w*w, v.co.x)
        for f in bm.faces:
            c=f.calc_center_median(); d=(gz(c)-tear(c.x,c.z))*sgn
            if not f[MV] and abs(gz(c)-cut)<BAND and d<0.07+0.05*noise.noise(c*5+off): f.material_index=BURNT
        # 3) dark inner walls: hull faces near the break, copied, flipped and pulled inward
        inner=[f for f in bm.faces if (f.material_index in hullIdx or f.material_index==BURNT)]
        inner=[f for f in inner if (gz(f.calc_center_median())-cut)*sgn<1.3 and f.calc_center_median().z<DECK+0.03]
        ret=bmesh.ops.duplicate(bm, geom=inner)
        nf=[g for g in ret['geom'] if isinstance(g,bmesh.types.BMFace)]
        nv={g for g in ret['geom'] if isinstance(g,bmesh.types.BMVert)}
        for v in nv: v.co.x*=0.96; v.co.z=v.co.z*0.98+0.005
        for f in nf: f.material_index=BURNT; f[ORIG]=0
        bmesh.ops.reverse_faces(bm, faces=nf)
        # 4) a torn bulkhead a little way in, so you can't see down the empty hull
        zb=cut+sgn*0.75
        pts=[]
        for e in bm.edges:
            if not (e.link_faces and e.link_faces[0].material_index in hullIdx and e.link_faces[0][ORIG]==1): continue
            a1,b1=e.verts[0].co,e.verts[1].co
            za,zb2=gz(a1),gz(b1)
            if (za-zb)*(zb2-zb)<0:
                t=(zb-za)/(zb2-za); p=a1.lerp(b1,t)
                if p.z<=DECK+0.02: pts.append((p.x,p.z))
        newf=[]
        if len(pts)>=3:
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
                newf.append(bm.faces.new((cv,ring[i],ring[(i+1)%len(ring)]) if bow else (cv,ring[(i+1)%len(ring)],ring[i])))
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
                    newf.append(bm.faces.new(q if bow else tuple(reversed(q))))
                    q2=(rows2[i][0],rows2[i+1][0],rows2[i+1][1],rows2[i][1])
                    newf.append(bm.faces.new(tuple(reversed(q2)) if bow else q2))
        for f in newf: f.material_index=BURNT; f[ORIG]=0
        # bent plates: a few burnt hull panels at the tear folded outwards
        edge=[f for f in bm.faces if f.material_index==BURNT and f[ORIG]==1 and f.calc_area()>0.0004 and abs(f.normal.x)>0.6]
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
            g[ORIG]=0; gf[ORIG]=0
        uv=bm.loops.layers.uv.active
        for f in bm.faces:
            if f.material_index==BURNT and uv is not None:
                nrm=f.normal; axis=max(range(3),key=lambda i:abs(nrm[i]))
                for l in f.loops:
                    c=l.vert.co; u=[c.y,c.x,c.x][axis]; w_=[c.z,c.z,c.y][axis]
                    l[uv].uv=(u*1.5,w_*1.5)
        bm.normal_update(); bm.to_mesh(o.data); bm.free()
        return o
    bow=make_piece(True); stern=make_piece(False)
    bpy.data.objects.remove(ship)
    for o,nm in ((bow,'bow'),(stern,'stern')):
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True)
        bpy.ops.wm.obj_export(filepath=f"{outdir}/{NAME}_{tag}_{nm}.obj", export_selected_objects=True, forward_axis='NEGATIVE_Z', up_axis='Y', path_mode='STRIP', export_normals=True, export_uv=True, export_materials=True)
    # kit: keep only the band (original faces outside it come from the game's own mesh)
    for o in (bow,stern):
        bm=bmesh.new(); bm.from_mesh(o.data); ORIG=bm.faces.layers.int.get('orig')
        MV=bm.faces.layers.int.get('mov')
        kill=[f for f in bm.faces if f[MV] or (f[ORIG]==1 and not all(abs(gz(v.co)-cut)<=BAND+1e-4 for v in f.verts))]
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        bm.to_mesh(o.data); bm.free()
    sz=write_brk(f"{outdir}/{NAME}_{tag}.brk", cut, ((1,bow),(0,stern)))
    print("cut", tag, round(cut,3), "deck", round(DECK,3), "bow", len(bow.data.vertices), "stern", len(stern.data.vertices), "brk", sz)
    for o in (bow,stern): bpy.data.objects.remove(o)

# soot texture (same for every ship)
def make_soot():
    import numpy as np
    N=512; img=bpy.data.images.new('burnt',N,N)
    n1=np.zeros((N,N)); n2=np.zeros((N,N))
    for yy in range(N):
        for xx in range(N):
            q=Vector((xx/N*6,yy/N*6,0.5))
            n1[yy,xx]=noise.fractal(q,0.8,2.0,5, noise_basis='PERLIN_ORIGINAL')
            n2[yy,xx]=noise.noise(q*2.3+Vector((7,3,1)), noise_basis='VORONOI_F1')
    soot=np.clip(0.09+0.06*n1,0.02,0.3); streak=np.clip(n2,0,1)*0.10; rust=np.clip(n1*0.6-0.15,0,1)*0.35
    rgb=np.stack([soot+streak+rust*0.55, soot+streak*0.95+rust*0.25, soot+streak*0.9+rust*0.08],-1)
    px=np.concatenate([rgb,np.ones((N,N,1))],-1).astype(np.float32)
    img.pixels.foreach_set(px.ravel()); img.filepath_raw=outdir+'/burnt.png'; img.file_format='PNG'; img.save()
make_soot() if not os.path.exists(outdir+'/burnt.png') else None
bimg=bpy.data.images.load(outdir+'/burnt.png')
nt=burnt.node_tree; tn=nt.nodes.new('ShaderNodeTexImage'); tn.image=bimg
nt.links.new(tn.outputs[0], nt.nodes['Principled BSDF'].inputs['Base Color'])
nt.nodes['Principled BSDF'].inputs['Roughness'].default_value=0.95

mid=(ext[0]+ext[1])/2
for i,spec in enumerate(cutspec.split(',')):
    tag,f=spec.split(':')
    do_cut(tag, mid+float(f)*L, seed+i*7)
