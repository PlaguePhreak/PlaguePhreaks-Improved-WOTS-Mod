# Step C: poses the new airman (seated / hanging / floating) with the skeleton and exports a static posed mesh.
# Run: python3 pose2.py -- <airman.fbx> <pose> <out.fbx>   Blender: Z up, figure faces -Y, his left = +X.
# Origins: seated = seat point under the hips; hanging = midpoint of the harness D-rings (where the risers clip);
# floating = chest at the waterline.
import bpy, sys, math, mathutils
from mathutils import Vector, Matrix
a=sys.argv[sys.argv.index('--')+1:]; src,POSE,out=a[:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src, automatic_bone_orientation=False)
rig=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'][0]
ob=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
vl=bpy.context.view_layer; pb=rig.pose.bones
W=rig.matrix_world   # FBX import may scale the rig; work in world space
def head(n): vl.update(); return W@pb[n].head
def tail(n): vl.update(); return W@pb[n].tail
def aim(n,d):
    """turn bone n (keeping its head) so it points along world direction d"""
    vl.update(); p=pb[n]
    M=W@p.matrix; cur=(M.to_3x3()@Vector((0,1,0))).normalized()
    q=cur.rotation_difference(Vector(d).normalized())
    R=q.to_matrix()@M.to_3x3()
    NM=Matrix.Translation(M.translation)@R.to_4x4()
    p.matrix=W.inverted()@NM; vl.update()
def length(n): return (rig.data.bones[n].tail_local-rig.data.bones[n].head_local).length*W.to_scale()[0]
def reach(side,wrist,bend):
    """two-bone arm: put the wrist at a world point, elbow bending toward 'bend'"""
    S=head('upperarm.'+side); A=length('upperarm.'+side); B=length('forearm.'+side)
    D=Vector(wrist)-S; d=min(D.length,A+B-1e-4); u=D.normalized()
    x=(A*A-B*B+d*d)/(2*d); h=math.sqrt(max(0,A*A-x*x))
    bn=Vector(bend); bn=(bn-u*bn.dot(u)).normalized()
    E=S+u*x+bn*h
    aim('upperarm.'+side,E-S); aim('forearm.'+side,Vector(wrist)-E)
# rest-pose D-ring points (front of each shoulder strap) in world space
mw=ob.matrix_world
def dring_rest(sx):
    c=[mw@v.co for v in ob.data.vertices]
    c=[p for p in c if abs(p.x-sx*0.085)<0.02 and abs(p.z-1.385)<0.02]
    return min(c,key=lambda p:p.y)
DR={s:dring_rest(1 if s=='L' else -1) for s in ('L','R')}
chest_rest=(W@rig.data.bones['chest'].matrix_local).copy()
if POSE=='hanging':
    aim('spine',(0,0.04,1)); aim('chest',(0,0.02,1)); aim('neck',(0,-0.05,1)); aim('head',(0,-0.12,1))
    for s,sx in (('L',1),('R',-1)):
        aim('thigh.'+s,(sx*0.06,-0.14,-1)); aim('shin.'+s,(0,0.16,-1)); aim('foot.'+s,(0,-1,-0.55))
    # hands grip the risers: risers run from the D-rings up to (+-0.22, 0, +1.1) above them
    vl.update(); CP=W@pb['chest'].matrix@(rig.data.bones['chest'].matrix_local.inverted())
    dr={s:(W@pb['chest'].matrix)@((chest_rest.inverted())@DR[s]) for s in DR}
    for s,sx in (('L',1),('R',-1)):
        top=dr[s]+Vector((sx*0.22-dr[s].x+ (dr['L'].x+dr['R'].x)/2*0,0,1.1)); top=Vector((sx*0.30+(dr['L'].x+dr['R'].x)/2,(dr['L'].y+dr['R'].y)/2,dr[s].z+1.1))
        w=dr[s].lerp(top,0.42)   # wrist a little below the grip
        reach(s,w,(sx*1,0.4,-0.2))
        aim('hand.'+s,top-w)
    vl.update(); dr={s:(W@pb['chest'].matrix)@((chest_rest.inverted())@DR[s]) for s in DR}
    ORIGIN=(dr['L']+dr['R'])/2
elif POSE=='seated':
    aim('spine',(0,0.08,1)); aim('chest',(0,0.04,1)); aim('neck',(0,-0.02,1)); aim('head',(0,-0.05,1))
    for s,sx in (('L',1),('R',-1)):
        aim('thigh.'+s,(sx*0.10,-1,0.04)); aim('shin.'+s,(sx*0.02,-0.30,-1)); aim('foot.'+s,(0,-1,0.15))
    # right hand on the stick between the knees, left hand on the throttle at his left side
    hip=head('hips'); 
    reach('R',hip+Vector((-0.02,-0.40,0.12)),(-1,0.3,-0.5)); aim('hand.R',(0,-0.25,1))
    reach('L',hip+Vector((0.25,-0.22,0.18)),(1,0.4,-0.6)); aim('hand.L',(0.1,-1,0.3))
    vl.update()
    ORIGIN=head('hips')-Vector((0,0,0.13))
elif POSE=='floating':
    # treading water in the life vest: arms out on the surface, legs hanging, leaning back
    aim('spine',(0,0.05,1)); aim('chest',(0,0.03,1)); aim('neck',(0,-0.15,1)); aim('head',(0,-0.3,1))
    for s,sx in (('L',1),('R',-1)):
        aim('shoulder.'+s,(sx*1,0.05,0.12)); aim('upperarm.'+s,(sx*1,-0.15,-0.25)); aim('forearm.'+s,(sx*0.8,-0.6,-0.1)); aim('hand.'+s,(sx*0.6,-0.8,0))
        aim('thigh.'+s,(sx*0.10,-0.35,-1)); aim('shin.'+s,(sx*0.02,0.25,-1)); aim('foot.'+s,(0,-0.6,-1))
    vl.update(); ORIGIN=head('chest')
# bake the pose into the mesh and drop the skeleton
bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); vl.objects.active=ob
for m in ob.modifiers:
    if m.type=='ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
ob.parent=None; ob.matrix_world=mw
bpy.data.objects.remove(rig)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
for v in ob.data.vertices: v.co-=ORIGIN
if POSE=='floating':   # lean back 35 degrees about the chest
    R=Matrix.Rotation(math.radians(-35),4,'X')
    for v in ob.data.vertices: v.co=R@v.co
for g in list(ob.vertex_groups): ob.vertex_groups.remove(g)
ob.name=ob.name.split('.')[0]+'_'+POSE
bpy.ops.export_scene.fbx(filepath=out, path_mode='COPY', embed_textures=True, object_types={'MESH'})
import numpy as np
V=np.array([v.co[:] for v in ob.data.vertices]); print('bounds',V.min(0).round(2),V.max(0).round(2))
if POSE=='hanging':
    print('DRINGS', tuple(round(x,3) for x in (dr['L']-ORIGIN)), tuple(round(x,3) for x in (dr['R']-ORIGIN)))
