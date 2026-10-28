# New airman, step B: body from step A + flying kit (helmet, goggles, life vest, harness) for US or Japan,
# one material with a 256 px colour-swatch texture. Run: python3 airman.py -- <out.fbx> us|jp
# Blender convention: Z up, figure faces -Y, figure's left = +X. Metres, 1.75 m tall, origin between the feet.
import bpy, sys, math, mathutils, os
a=sys.argv[sys.argv.index('--')+1:]; out=a[0]; NAT=a[1] if len(a)>1 else 'us'
bpy.ops.wm.read_factory_settings(use_empty=True)
J={ # name: (pos, (radius x, radius y), parent). Baggy flight suit proportions.
 'pelvis':((0,0,0.97),(0.17,0.135),None),
 'waist':((0,0.005,1.11),(0.165,0.14),'pelvis'),
 'chest':((0,0,1.27),(0.19,0.15),'waist'),
 'chestTop':((0,0.01,1.40),(0.175,0.135),'chest'),
 'neck':((0,0.015,1.49),(0.065,0.065),'chestTop'),
 'neckTop':((0,0.01,1.56),(0.058,0.06),'neck'),
 'shoulder.L':((0.195,0.01,1.415),(0.075,0.075),'chestTop'),
 'bicep.L':((0.28,0.02,1.315),(0.066,0.066),'shoulder.L'),
 'elbow.L':((0.37,0.03,1.20),(0.056,0.056),'bicep.L'),
 'cuff.L':((0.505,0.005,1.035),(0.05,0.047),'elbow.L'),
 'wrist.L':((0.535,0.0,1.0),(0.036,0.03),'cuff.L'),
 'hand.L':((0.58,-0.01,0.94),(0.045,0.024),'wrist.L'),
 'fingers.L':((0.612,-0.018,0.875),(0.034,0.018),'hand.L'),
 'thumb.L':((0.56,-0.05,0.93),(0.016,0.016),'hand.L'),
 'hip.L':((0.10,0,0.92),(0.10,0.10),'pelvis'),
 'thighmid.L':((0.105,-0.005,0.73),(0.088,0.088),'hip.L'),
 'knee.L':((0.105,-0.01,0.52),(0.07,0.072),'thighmid.L'),
 'calf.L':((0.105,0.01,0.33),(0.064,0.07),'knee.L'),
 'ankle.L':((0.105,0.015,0.12),(0.058,0.062),'calf.L'),
 'heel.L':((0.105,0.045,0.045),(0.05,0.045),'ankle.L'),
 'toe.L':((0.105,-0.15,0.04),(0.05,0.042),'ankle.L'),
}
for k in list(J):
    if k.endswith('.L'):
        p,r,par=J[k]; J[k[:-2]+'.R']=((-p[0],p[1],p[2]),r,(par[:-2]+'.R') if par and par.endswith('.L') else par)
names=list(J); idx={n:i for i,n in enumerate(names)}
me=bpy.data.meshes.new('airman'); me.from_pydata([J[n][0] for n in names],[(idx[J[n][2]],i) for i,n in enumerate(names) if J[n][2]],[])
ob=bpy.data.objects.new('airman',me); bpy.context.scene.collection.objects.link(ob)
bpy.context.view_layer.objects.active=ob; ob.select_set(True)
sk=ob.modifiers.new('skin','SKIN'); sk.branch_smoothing=0.6; sk.use_smooth_shade=True
for i,n in enumerate(names):
    sv=me.skin_vertices[0].data[i]; sv.radius=J[n][1]
    sv.use_root=(n=='pelvis')
ss=ob.modifiers.new('sub','SUBSURF'); ss.levels=1; ss.render_levels=1
bpy.ops.object.modifier_apply(modifier='skin'); bpy.ops.object.modifier_apply(modifier='sub')
# head: shaped sphere (skull + jaw), joined to the body (no nose or ears, Aaron 28 Oct)
import bmesh
def prim(kind,loc,scale,**kw):
    if kind=='sphere': bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=loc,**kw)
    else: bpy.ops.mesh.primitive_cube_add(location=loc,**kw)
    o=bpy.context.active_object; o.scale=scale; bpy.ops.object.transform_apply(scale=True); return o
hd=prim('sphere',(0,0.0,1.655),(0.093,0.108,0.118))
for v in hd.data.vertices:
    c=v.co   # local to (0,0,1.655)
    if c.z<0:   # narrow the jaw and chin
        t=min(1,-c.z/0.118); c.x*=1-0.32*t; c.y*=1-0.12*t
        if c.y<0: c.y-=0.012*t
    if c.y<-0.06 and c.z>0.02: c.y+=0.012   # flatter brow/forehead
for o in [hd]:
    for p in o.data.polygons: p.use_smooth=True
bpy.ops.object.select_all(action='DESELECT')
for o in [hd]: o.select_set(True)
ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.join(); me=ob.data
# colours per nation: US khaki summer suit, tan cloth helmet, yellow Mae West, olive webbing;
# Japan brown flying suit, brown leather helmet, kapok vest, light tan webbing
PAL={'us':dict(suit=(0.40,0.34,0.21),boots=(0.10,0.06,0.04),gloves=(0.22,0.13,0.07),skin=(0.75,0.55,0.42),
               helmet=(0.50,0.40,0.26),vest=(0.85,0.62,0.08),harness=(0.27,0.27,0.16),metal=(0.22,0.22,0.22),lens=(0.06,0.14,0.14),buckle=(0.55,0.55,0.52)),
     'jp':dict(suit=(0.30,0.21,0.12),boots=(0.09,0.06,0.04),gloves=(0.20,0.12,0.06),skin=(0.75,0.55,0.42),
               helmet=(0.26,0.15,0.08),vest=(0.52,0.46,0.30),harness=(0.62,0.56,0.42),metal=(0.22,0.22,0.22),lens=(0.06,0.14,0.14),buckle=(0.55,0.55,0.52))}[NAT]
ORDER=list(PAL)
MI={n:i for i,n in enumerate(ORDER)}
for n in ORDER: me.materials.append(bpy.data.materials.new(n))
for p in me.polygons:
    c=p.center
    if c.z>1.475: p.material_index=MI['skin']
    elif c.z<0.30: p.material_index=MI['boots']
    elif abs(c.x)>0.52 and c.z<1.025: p.material_index=MI['gloves']
    else: p.material_index=MI['suit']
# ---- kit pieces
me.update(); bm0=bmesh.new(); bm0.from_mesh(me); bm0.normal_update()
def shell(pred,off,matn,name,thick=0.0):
    """copy body faces matching pred(face centre, face normal) and push them out along vertex normals"""
    bm=bmesh.new(); vm={}
    for f in bm0.faces:
        if not pred(f.calc_center_median(),f.normal): continue
        vs=[]
        for v in f.verts:
            if v.index not in vm: vm[v.index]=bm.verts.new(v.co+v.normal*off)
            vs.append(vm[v.index])
        bm.faces.new(vs)
    m=bpy.data.meshes.new(name); bm.to_mesh(m); o=bpy.data.objects.new(name,m); bpy.context.scene.collection.objects.link(o)
    for q in m.polygons: q.use_smooth=True
    if thick:
        sd=o.modifiers.new('s','SOLIDIFY'); sd.thickness=thick; sd.offset=1
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='s')
    setmat(o,matn); return o
def setmat(o,matn):
    for n in ORDER: o.data.materials.append(bpy.data.materials[n])
    for q in o.data.polygons: q.material_index=MI[matn]
kit=[]
# life vest: puffy shell over the torso, plus a horse-collar round the neck
def torso(c,nrm): return 1.0<c.z<1.45 and abs(c.x)<(0.165 if c.z>1.33 else 0.21)
kit.append(shell(torso,0.03,'vest','vest',0.012))
for v in kit[0].data.vertices:   # inflated lobes on the chest
    if v.co.y<-0.05 and 1.15<v.co.z<1.40: v.co.y-=0.025*math.sin((v.co.z-1.15)/0.25*math.pi)
bpy.ops.mesh.primitive_torus_add(major_radius=0.105,minor_radius=0.04,major_segments=16,minor_segments=8,location=(0,0.02,1.46))
col=bpy.context.active_object; col.scale=(1.0,0.95,0.8); col.rotation_euler=(math.radians(-12),0,0)
bpy.ops.object.transform_apply(scale=True,rotation=True); setmat(col,'vest'); kit.append(col)
# harness webbing: ribbons projected onto the vest (shoulder straps front and back, chest strap, belly band)
# and onto the suit (leg loops). Each guide point is pushed in from outside until it meets the surface.
from mathutils.bvhtree import BVHTree
vest=kit[0]; dg=bpy.context.evaluated_depsgraph_get()
bv_vest=BVHTree.FromObject(vest,dg); bv_body=BVHTree.FromObject(ob,dg)
def snap(bvh,p,d,lift):
    p=mathutils.Vector(p); d=mathutils.Vector(d).normalized()
    hit,nrm,_,_=bvh.ray_cast(p+d*0.6,-d)
    if hit is None: return p,d
    return hit+nrm*lift,nrm
def ribbon(bvh,pts,width,lift,closed=False):
    P=[snap(bvh,p,d,lift) for p,d in pts]; bm=bmesh.new(); L=[]
    n=len(P)
    for i,(p,nrm) in enumerate(P):
        q0=P[(i-1)%n][0] if (closed or i>0) else p; q1=P[(i+1)%n][0] if (closed or i<n-1) else p
        t=(q1-q0).normalized(); side=t.cross(nrm).normalized()*width/2
        L.append((bm.verts.new(p-side),bm.verts.new(p+side)))
    for i in range(n if closed else n-1):
        a_,b_=L[i],L[(i+1)%n]; bm.faces.new((a_[0],a_[1],b_[1],b_[0]))
    m=bpy.data.meshes.new('strap'); bm.to_mesh(m); o=bpy.data.objects.new('strap',m); bpy.context.scene.collection.objects.link(o)
    sd=o.modifiers.new('s','SOLIDIFY'); sd.thickness=0.007; sd.offset=0
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='s'); setmat(o,'harness'); kit.append(o)
for sx in (1,-1):
    x=0.085*sx; pts=[]
    for z in (1.00,1.07,1.14,1.21,1.28,1.35,1.41): pts.append(((x,0,z),(0,-1,0)))          # front, waist up
    for y in (-0.06,0.0,0.06): pts.append(((x,y,1.45),(0,0.0,1)))                          # over the shoulder
    for z in (1.41,1.33,1.24,1.15,1.06): pts.append(((x,0,z),(0,1,0)))                     # down the back
    ribbon(bv_vest,pts,0.045,0.006)
ribbon(bv_vest,[((x,0,1.215),(0,-1,0)) for x in (-0.15,-0.1,-0.05,0,0.05,0.1,0.15)],0.04,0.012)   # chest strap
ribbon(bv_vest,[((0.2*math.sin(a_),-0.0,1.03),(math.sin(a_),-math.cos(a_),0)) for a_ in [i*2*math.pi/16 for i in range(16)]],0.045,0.006,True)   # belly band
for sx in (1,-1):   # leg loops round the top of each thigh
    cx=0.103*sx
    ribbon(bv_body,[((cx+0.1*math.sin(a_),-0.005-0.1*math.cos(a_),0.80),(math.sin(a_),-math.cos(a_),0)) for a_ in [i*2*math.pi/12 for i in range(12)]],0.04,0.006,True)
for z in (1.21,):   # chest buckle
    hit=snap(bv_vest,(0,0,z),(0,-1,0),0.02)[0]
    bpy.ops.mesh.primitive_cube_add(location=hit); b=bpy.context.active_object; b.scale=(0.032,0.008,0.028)
    bpy.ops.object.transform_apply(scale=True); setmat(b,'buckle'); kit.append(b)
# helmet: shell over the skull with a face opening; the sides come down as ear flaps
hc=mathutils.Vector((0,0,1.655))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=10,location=hc)
h=bpy.context.active_object; h.scale=(0.102,0.117,0.127); bpy.ops.object.transform_apply(scale=True)
bmh=bmesh.new(); bmh.from_mesh(h.data)
def lc(f): return f.calc_center_median()-hc      # sphere coords are world (transform_apply moved them)
dead=[f for f in bmh.faces if lc(f).z<-0.07 or (lc(f).y<-0.02 and lc(f).z<0.04 and abs(lc(f).x)<0.08)]
bmesh.ops.delete(bmh,geom=dead,context='FACES'); bmh.to_mesh(h.data); bmh.free()
sd=h.modifiers.new('s','SOLIDIFY'); sd.thickness=0.008; sd.offset=1
bpy.context.view_layer.objects.active=h; bpy.ops.object.modifier_apply(modifier='s')
for q in h.data.polygons: q.use_smooth=True
setmat(h,'helmet'); kit.append(h)
# goggles pushed up on the helmet: two lenses and a strap
for sx in (1,-1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=0.027,depth=0.02,location=(sx*0.043,-0.112,1.722),rotation=(math.radians(58),0,math.radians(sx*-14)))
    g=bpy.context.active_object; bpy.ops.object.transform_apply(location=False,rotation=True)
    setmat(g,'metal')
    ax=mathutils.Vector((0,-1,0)); ax.rotate(mathutils.Euler((math.radians(58-90),0,math.radians(sx*-14))))
    for q in g.data.polygons:
        if q.normal.dot(mathutils.Vector((0,-math.sin(math.radians(58)),math.cos(math.radians(58)))))<-0.8 or q.normal.y<-0.7: q.material_index=MI['lens']
    kit.append(g)
bpy.ops.mesh.primitive_torus_add(major_radius=0.112,minor_radius=0.008,major_segments=20,minor_segments=6,location=(0,0.004,1.712))
st=bpy.context.active_object; st.scale=(0.95,1.1,1); st.rotation_euler=(math.radians(-14),0,0)
bpy.ops.object.transform_apply(scale=True,rotation=True); setmat(st,'metal'); kit.append(st)
bm0.free()
bpy.ops.object.select_all(action='DESELECT')
for o in kit: o.select_set(True)
ob.select_set(True); bpy.context.view_layer.objects.active=ob; bpy.ops.object.join(); me=ob.data
# ---- one texture: 4x4 swatches of 64 px with light cloth noise; every face maps into its swatch
import numpy as np
rng=np.random.default_rng(3); S=64; img=np.zeros((256,256,4),np.float32)
for i,n in enumerate(ORDER):
    r,c=divmod(i,4); col=np.array(PAL[n])
    noise=1+0.06*rng.standard_normal((S,S,1))+0.04*np.sin(np.arange(S)[None,:,None]*1.7)
    img[r*S:(r+1)*S,c*S:(c+1)*S,:3]=np.clip(col*noise,0,1); img[r*S:(r+1)*S,c*S:(c+1)*S,3]=1
tex=bpy.data.images.new(f'airman_{NAT}_tex',256,256); tex.pixels=img.ravel().tolist()
tex.filepath_raw=os.path.join(os.path.dirname(out),f'airman_{NAT}_tex.png'); tex.file_format='PNG'; tex.save()
while me.uv_layers: me.uv_layers.remove(me.uv_layers[0])   # drop the primitives' own UV maps
uv=me.uv_layers.new(name='UVMap')
for p in me.polygons:
    r,c=divmod(p.material_index,4)
    # spread each face's corners a little inside its swatch so the noise shows
    for k,li in enumerate(p.loop_indices):
        ang=k*2.1; uv.data[li].uv=((c*S+S/2+18*math.cos(ang+p.index))/256, (r*S+S/2+18*math.sin(ang+p.index))/256)   # Blender image rows start at the bottom
m=bpy.data.materials.new(f'airman_{NAT}'); m.use_nodes=True; nt=m.node_tree
t=nt.nodes.new('ShaderNodeTexImage'); t.image=tex; t.interpolation='Closest'
bs=nt.nodes['Principled BSDF']; nt.links.new(t.outputs['Color'],bs.inputs['Base Color']); bs.inputs['Roughness'].default_value=0.75
me.materials.clear(); me.materials.append(m)
for p in me.polygons: p.material_index=0
ob.name=f'airman_{NAT}'
# armature
arm=bpy.data.armatures.new(f'airman_{NAT}_rig'); rig=bpy.data.objects.new(f'airman_{NAT}_rig',arm); bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig; bpy.ops.object.mode_set(mode='EDIT')
P=lambda n: mathutils.Vector(J[n][0])
B={}
def bone(n,h,t,par=None,conn=False):
    b=arm.edit_bones.new(n); b.head=h; b.tail=t
    if par: b.parent=B[par]; b.use_connect=conn
    B[n]=b
bone('hips',P('pelvis'),P('waist'))
bone('spine',P('waist'),P('chest'),'hips',True)
bone('chest',P('chest'),P('chestTop'),'spine',True)
bone('neck',P('chestTop'),P('neckTop'),'chest',True)
bone('head',P('neckTop'),mathutils.Vector((0,0.0,1.78)),'neck',True)
for s in ('L','R'):
    bone('shoulder.'+s,P('chestTop')+mathutils.Vector((0,0,-0.01)),P('shoulder.'+s),'chest')
    bone('upperarm.'+s,P('shoulder.'+s),P('elbow.'+s),'shoulder.'+s,True)
    bone('forearm.'+s,P('elbow.'+s),P('wrist.'+s),'upperarm.'+s,True)
    bone('hand.'+s,P('wrist.'+s),P('fingers.'+s),'forearm.'+s,True)
    bone('thigh.'+s,P('hip.'+s),P('knee.'+s),'hips')
    bone('shin.'+s,P('knee.'+s),P('ankle.'+s),'thigh.'+s,True)
    bone('foot.'+s,P('ankle.'+s),P('toe.'+s),'shin.'+s,True)
for b in arm.edit_bones:
    b.roll=0
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); rig.select_set(True); bpy.context.view_layer.objects.active=rig
bpy.ops.object.parent_set(type='ARMATURE_NAME')
# weights by distance to each bone (heat weighting fails on the layered kit). A vertex never follows the
# other side's limbs, and only the nearest bones (falloff 2 cm) share it.
import numpy as np
V=np.array([v.co[:] for v in me.vertices]); bones=list(arm.bones)
def segd(h,t):
    h=np.array(h); t=np.array(t); d=t-h; u=np.clip(((V-h)@d)/(d@d),0,1); return np.linalg.norm(V-(h+u[:,None]*d),axis=1)
D=np.stack([segd(b.head_local[:],b.tail_local[:]) for b in bones],1)
for j,b in enumerate(bones):
    if b.name.endswith('.L'): D[V[:,0]<-0.02,j]=9
    if b.name.endswith('.R'): D[V[:,0]>0.02,j]=9
    if b.name.split('.')[0] in ('upperarm','forearm','hand'): D[(np.abs(V[:,0])<0.215)&(V[:,2]>0.95)&(V[:,2]<1.52),j]=9   # vest and torso stay off the arms
W=np.exp(-(D-D.min(1,keepdims=True))/0.02); W[W<0.08]=0
top=np.argsort(-W,1)[:,3:]; np.put_along_axis(W,top,0,1); W/=W.sum(1,keepdims=True)
for j,b in enumerate(bones):
    g=ob.vertex_groups[b.name]
    for i in np.nonzero(W[:,j])[0]: g.add([int(i)],float(W[i,j]),'REPLACE')
empty=[g.name for g in ob.vertex_groups if not any(g.index in [x.group for x in v.groups] for v in me.vertices)]
print('tris',sum(len(p.vertices)-2 for p in me.polygons),'verts',len(me.vertices),'groups without verts',empty)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=out, add_leaf_bones=False, path_mode='COPY', embed_textures=True)
