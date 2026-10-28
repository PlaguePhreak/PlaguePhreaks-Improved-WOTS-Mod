import bpy,sys,mathutils
a=sys.argv[sys.argv.index('--')+1:]; can,pil,name,out=a
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=can); c=bpy.context.selected_objects[:]
bpy.ops.import_scene.fbx(filepath=pil); p=bpy.context.selected_objects[:]
root=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(root)
for o in c: o.name='canopy'
for o in p: o.name='pilot'
for o in c+p:
    if o.parent is None: o.parent=root
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=out, path_mode='COPY', embed_textures=True)
sc=bpy.context.scene
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.6,0.3,0.8); l.data.energy=3
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.35,0.45,0.6)
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=500; sc.render.resolution_y=600
ctr=mathutils.Vector((0,0,3.2))
for nm,loc in (('side',(20,0,0)),('three',(14,-14,-6)),('close',(4,-4,0.5))):
    cam=bpy.data.objects.new(nm,bpy.data.cameras.new(nm)); sc.collection.objects.link(cam)
    t=ctr if nm!='close' else mathutils.Vector((0,0,0.3))
    cam.location=t+mathutils.Vector(loc); cam.data.type='ORTHO'; cam.data.ortho_scale=10 if nm!='close' else 3
    cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
    sc.render.filepath=out.replace('.fbx','_'+nm+'.png'); bpy.ops.render.render(write_still=True)
