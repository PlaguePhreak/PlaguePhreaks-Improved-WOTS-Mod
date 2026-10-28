import bpy, sys, mathutils
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.read_factory_settings(use_empty=True); sc=bpy.context.scene
for i,f in enumerate(a[1:]):
    bpy.ops.import_scene.fbx(filepath=f)
    for o in bpy.context.selected_objects:
        if o.type=='MESH':
            zs=[(o.matrix_world@v.co).z for v in o.data.vertices]; o.location.z-=(min(zs)+max(zs))/2
        o.location.x+=i*1.6
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.7,0.2,-0.6); l.data.energy=3.5
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.42,0.42,0.45)
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=1200; sc.render.resolution_y=500
c=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(c); ctr=mathutils.Vector((1.6,0,0))
c.location=ctr+mathutils.Vector((4,-6,1.5)); c.data.type='ORTHO'; c.data.ortho_scale=5.2
c.rotation_euler=(ctr-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
sc.render.filepath=a[0]; bpy.ops.render.render(write_still=True)
