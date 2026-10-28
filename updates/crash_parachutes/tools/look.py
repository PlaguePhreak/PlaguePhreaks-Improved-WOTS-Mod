# Renders an airman FBX: front, side, three-quarter, and a posing test (arms up, one knee bent) to check the weights.
import bpy, sys, math, mathutils
a=sys.argv[sys.argv.index('--')+1:]; f,out=a[0],a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=f, automatic_bone_orientation=False)
sc=bpy.context.scene
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.7,0.2,-0.6); l.data.energy=3.5
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.42,0.42,0.45)
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=360; sc.render.resolution_y=520
rig=[o for o in sc.objects if o.type=='ARMATURE']
for o in sc.objects:
    if o.type=='ARMATURE': o.hide_render=True
ctr=mathutils.Vector((0,0,0.9))
def shot(nm,loc,scale=2.0,c=ctr):
    cam=bpy.data.objects.new(nm,bpy.data.cameras.new(nm)); sc.collection.objects.link(cam)
    cam.location=c+mathutils.Vector(loc); cam.data.type='ORTHO'; cam.data.ortho_scale=scale
    cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
    sc.render.filepath=out+'_'+nm+'.png'; bpy.ops.render.render(write_still=True)
shot('front',(0,-6,0)); shot('side',(6,0,0)); shot('three',(4,-4,1.2)); shot('head',(1.5,-3,0.6),0.75,mathutils.Vector((0,0,1.45)))
if rig and len(a)<3:
    pb=rig[0].pose.bones
    def r(n,ax,deg):
        b=pb.get(n)
        if b: b.rotation_mode='XYZ'; e=list(b.rotation_euler); e['XYZ'.index(ax)]=math.radians(deg); b.rotation_euler=e
    for s,sg in (('L',1),('R',-1)):
        r('upperarm.'+s,'Z',0); r('upperarm.'+s,'X',0)
    # pose in world terms is easier: rotate bones about their local axes; test values
    r('upperarm.L','Y',0); 
    for n in ('upperarm.L','upperarm.R'):
        b=pb.get(n); b.rotation_mode='QUATERNION'
        bone=rig[0].data.bones[n]; cur=(bone.tail_local-bone.head_local).normalized()
        tgt=mathutils.Vector((0.25*(1 if n.endswith('L') else -1),0,1)).normalized()
        q=cur.rotation_difference(tgt); M=bone.matrix_local.to_quaternion()
        b.rotation_quaternion=M.inverted()@q@M
    for n,tgt in (('thigh.L',(0.05,-1,-0.3)),('shin.L',(0,0.3,-1))):
        b=pb.get(n); b.rotation_mode='QUATERNION'; bone=rig[0].data.bones[n]
        bpy.context.view_layer.update()
        par=b.parent.matrix.to_quaternion() if b.parent else mathutils.Quaternion()
        parrest=bone.parent.matrix_local.to_quaternion() if bone.parent else mathutils.Quaternion()
        cur=(par@parrest.inverted())@(bone.tail_local-bone.head_local).normalized()
        q=cur.rotation_difference(mathutils.Vector(tgt).normalized()); M=(par@parrest.inverted()@bone.matrix_local.to_quaternion())
        b.rotation_quaternion=M.inverted()@q@M
    bpy.context.view_layer.update()
    shot('posetest',(4,-4,1.2),2.4,mathutils.Vector((0,0,1.0)))
