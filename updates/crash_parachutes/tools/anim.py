# Bail-out animation for review: pilot falls clear, chute streams out, blossoms, sways down, lands in the sea and collapses.
# Hierarchy: <name>_bailout (falls) > sway (pivot at canopy centre) > pilot, chute (pivot at riser top) > canopy, lines
import bpy, sys, math, mathutils
a=sys.argv[sys.argv.index('--')+1:]; can_fbx,pil_fbx,name,out=a[:4]; gif=len(a)>4 and a[4]=='gif'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; FPS=30; sc.render.fps=FPS
def imp(f):
    bpy.ops.import_scene.fbx(filepath=f); return [o for o in bpy.context.selected_objects]
co=imp(can_fbx); po=imp(pil_fbx)
canopy=[o for o in co if o.type=='MESH' and 'canopy' in o.name][0]; lines=[o for o in co if o.type=='MESH' and 'lines' in o.name][0]
pilot=[o for o in po if o.type=='MESH'][0]
for o in co+po:
    if o.type!='MESH': bpy.data.objects.remove(o)
def empty(n,parent=None,loc=(0,0,0)):
    e=bpy.data.objects.new(n,None); sc.collection.objects.link(e); e.parent=parent; e.location=loc; return e
SWAY=6.5; RISER=1.1
root=empty(name+'_bailout'); sway=empty('sway',root,(0,0,SWAY)); chute=empty('chute',sway,(0,0,RISER-SWAY))
for o in (canopy,lines):
    mw=o.matrix_world.copy(); o.parent=chute; o.matrix_world=mw; o.location=(0,0,-RISER); o.rotation_euler=(0,0,0); o.scale=(1,1,1)
canopy.name='canopy'; lines.name='lines'
mw=pilot.matrix_world.copy(); pilot.parent=sway; pilot.matrix_world=mw; pilot.location=(0,0,-SWAY); pilot.rotation_euler=(0,0,0); pilot.scale=(1,1,1); pilot.name='pilot'
def key(o,f,loc=None,rot=None,scl=None):
    if loc is not None: o.location=loc; o.keyframe_insert('location',frame=f)
    if rot is not None: o.rotation_euler=[math.radians(r) for r in rot]; o.keyframe_insert('rotation_euler',frame=f)
    if scl is not None: o.scale=scl; o.keyframe_insert('scale',frame=f)
F=lambda t: round(t*FPS)+1
# --- fall path of the harness (root), z up, metres. Start 60 m above the sea, 1 m/s wind drift along +x.
T_STRETCH=1.5; T_OPEN=2.6; V0=6.0; Z0=60.0
z=Z0; v=0.0; t=0.0; dt=1/FPS; path=[]; t_touch=None
while True:
    if t<T_STRETCH: v+=9.8*dt
    elif t<T_OPEN: v+= (V0-v)*min(1,dt*4.5)
    else: v+=(V0-v)*min(1,dt*2)
    if t_touch is None and z<=1.4: t_touch=t          # feet reach the water
    if t_touch is not None:
        s=t-t_touch; v=max(0.0,v-dt*9); z=max(z-v*dt,-0.05*math.sin(s*2.5)-0.1) if s<1.2 else -0.1-0.05*math.sin(s*2.5)
    else: z-=v*dt
    path.append((t,z)); t+=dt
    if t_touch is not None and t>t_touch+4.0: break
END=len(path); sc.frame_start=1; sc.frame_end=END
for i,(tt,zz) in enumerate(path):
    if i%2==0 or i==END-1:
        drift=min(tt,t_touch)*1.0
        key(root,i+1,loc=(drift,0,zz))
# --- pilot pitches forward in free fall (never past ~50 deg, stays head-up),, jerked upright at line stretch
for tt,r in ((0,(0,0,0)),(0.5,(-25,10,0)),(1.0,(-45,18,8)),(T_STRETCH,(-50,12,12)),(T_STRETCH+0.35,(-15,4,4)),(T_STRETCH+0.7,(14,-4,0)),(T_STRETCH+1.1,(-5,0,0)),(T_OPEN+0.5,(0,0,0))):
    key(pilot,F(tt),rot=r)
key(pilot,F(t_touch),rot=(0,0,0)); key(pilot,F(t_touch+1.2),rot=(-35,0,0)); key(pilot,F(t_touch+4),rot=(-30,0,0))   # leans back in the water
# --- canopy: packed (tiny, at the pilot) > streamer > blossom > breathing > collapse
key(chute,1,loc=(0,0.15,-SWAY),rot=(0,0,0),scl=(0.01,0.01,0.01))
key(chute,F(1.0),loc=(0,0.15,-SWAY),scl=(0.01,0.01,0.01))
key(chute,F(1.2),loc=(0,0.3,-SWAY+0.4),scl=(0.03,0.03,0.25))
key(chute,F(T_STRETCH),loc=(0,0,RISER-SWAY),scl=(0.06,0.06,1.05))
key(chute,F(T_STRETCH+0.4),scl=(0.18,0.18,1.08))
key(chute,F(T_STRETCH+0.75),scl=(0.7,0.7,1.02))
key(chute,F(T_OPEN),scl=(1.15,1.15,0.88))
key(chute,F(T_OPEN+0.35),scl=(0.95,0.95,1.03))
key(chute,F(T_OPEN+0.7),scl=(1,1,1))
tt=T_OPEN+0.7; k=0
while tt<t_touch-0.4:
    tt+=0.75; k+=1; s=1.02 if k%2 else 1.0; key(chute,F(tt),scl=(s,s,2-s))
key(chute,F(t_touch),loc=(0,0,RISER-SWAY),rot=(0,0,0),scl=(1,1,1))
key(chute,F(t_touch+0.8),loc=(0,0.8,RISER-SWAY-0.4),rot=(25,0,0),scl=(1.05,1.05,0.7))
key(chute,F(t_touch+2.2),loc=(0,2.5,-SWAY-0.05),rot=(35,0,0),scl=(1.2,1.2,0.25))
key(chute,F(t_touch+4),loc=(0,4.0,-SWAY-0.12),rot=(0,0,0),scl=(1.3,1.3,0.03))   # lies flat on the sea, drifted downwind
# --- pendulum sway under the canopy after opening, dying down, stopped at splashdown
key(sway,1,rot=(0,0,0)); key(sway,F(T_OPEN-0.3),rot=(0,0,0))
tt=T_OPEN-0.3
while tt<t_touch-0.3:
    tt+=0.25; A=5+11*math.exp(-(tt-T_OPEN)/4)
    key(sway,F(tt),rot=(A*math.sin(2*math.pi*(tt-T_OPEN+0.3)/3.4),0.45*A*math.sin(2*math.pi*(tt-T_OPEN)/4.7),0))
key(sway,F(t_touch),rot=(0,0,0))
for o in (root,sway,chute,pilot):
    if o.animation_data:
        for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action,'fcurves') else []: pass
# --- sea reference plane (delete it in the game version)
bpy.ops.mesh.primitive_plane_add(size=60,location=(0,0,0)); sea=bpy.context.active_object; sea.name='sea_reference_delete_me'
m=bpy.data.materials.new('sea'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.05,0.15,0.25,1); sea.data.materials.append(m)
print('frames',END,'touchdown s',round(t_touch,2))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=out, path_mode='COPY', embed_textures=True, bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False, bake_anim_simplify_factor=0.0, add_leaf_bones=False)
if gif:
    sea.scale=(8,8,1)
    l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.6,0.3,0.8); l.data.energy=3
    w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.45,0.6,0.8)
    sc.render.engine='CYCLES'; sc.cycles.samples=6; sc.render.resolution_x=320; sc.render.resolution_y=400
    cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=35
    import os; d=os.path.dirname(out)+'/frames_'+name; os.makedirs(d,exist_ok=True)
    for f in range(1,END+1,3):
        sc.frame_set(f); p=root.matrix_world.translation; tgt=p+mathutils.Vector((0,0,2.8))
        cam.location=tgt+mathutils.Vector((15,-17,3)); cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=f'{d}/{f:04d}.png'; bpy.ops.render.render(write_still=True)
