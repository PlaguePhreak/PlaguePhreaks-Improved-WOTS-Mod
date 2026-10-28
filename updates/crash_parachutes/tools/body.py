# New airman, step A: low-poly body (Skin modifier over a joint graph) + armature with automatic weights.
# Blender convention: Z up, figure faces -Y, figure's left = +X. Metres, 1.75 m tall, origin between the feet.
import bpy, sys, math, mathutils
out=sys.argv[sys.argv.index('--')+1]
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
# regions -> materials: flight suit, boots, gloves, skin (head/neck)
mats={}
def mat(n,c,rough=0.8):
    m=bpy.data.materials.new(n); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=rough; me.materials.append(m); mats[n]=len(me.materials)-1
mat('suit',(0.30,0.24,0.15)); mat('boots',(0.06,0.04,0.03),0.6); mat('gloves',(0.18,0.11,0.06),0.6); mat('skin',(0.75,0.55,0.42),0.6)
for p in me.polygons:
    c=p.center
    if c.z>1.475: p.material_index=mats['skin']
    elif c.z<0.20: p.material_index=mats['boots']
    elif abs(c.x)>0.52 and c.z<1.025: p.material_index=mats['gloves']
    else: p.material_index=mats['suit']
# armature
arm=bpy.data.armatures.new('airman_rig'); rig=bpy.data.objects.new('airman_rig',arm); bpy.context.scene.collection.objects.link(rig)
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
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
empty=[g.name for g in ob.vertex_groups if not any(g.index in [x.group for x in v.groups] for v in me.vertices)]
print('tris',sum(len(p.vertices)-2 for p in me.polygons),'verts',len(me.vertices),'groups without verts',empty)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=out, add_leaf_bones=False, path_mode='COPY', embed_textures=True)
