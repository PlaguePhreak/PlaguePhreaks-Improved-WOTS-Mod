# blender python: python3 seq.py -- poses.json unit.obj clone.obj outprefix camdist
import bpy, sys, json, math, mathutils
a=sys.argv[sys.argv.index('--')+1:]
poses=json.load(open(a[0])); files=[a[1],a[2]]; outp=a[3]; dist=float(a[4])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
objs=[]
for f in files:
    before=set(sc.objects)
    bpy.ops.wm.obj_import(filepath=f, forward_axis='NEGATIVE_Z', up_axis='Y')
    new=[o for o in sc.objects if o not in before and o.type=='MESH']
    objs.append(new)
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED': n.inputs['Roughness'].default_value=0.8
M=mathutils.Matrix(((-1,0,0),(0,0,-1),(0,1,0)))
D=mathutils.Matrix(((-1,0,0),(0,1,0),(0,0,1)))  # the imported mesh data is in OBJ axes (x = -game x)
# sea
bpy.ops.mesh.primitive_plane_add(size=400, location=(0,0,0)); sea=bpy.context.object
mat=bpy.data.materials.new('sea'); mat.use_nodes=True; b=mat.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.03,0.12,0.16,1); b.inputs['Roughness'].default_value=0.15
b.inputs['Alpha'].default_value=0.55
sea.data.materials.append(mat)
try: mat.blend_method='BLEND'
except: pass
c=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(c); sc.camera=c; c.data.lens=35
tgt=mathutils.Vector((0,0,-4.0)); c.location=tgt+mathutils.Vector((dist,-dist*0.35,dist*0.28)); c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler()
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.6,0.2,0.9); l.data.energy=4
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.62,0.7,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.render.resolution_x=640; sc.render.resolution_y=420
for i,f in enumerate(poses):
    for k,key in enumerate(['unit','clone']):
        p=f[key]; t=mathutils.Vector(p[0:3]); R=mathutils.Matrix(((p[3],p[6],p[9]),(p[4],p[7],p[10]),(p[5],p[8],p[11])))
        Rb=M@R@D; tb=M@t
        mw=Rb.to_4x4(); mw.translation=tb
        for o in objs[k]: o.matrix_world=mw
    sc.render.filepath='%s_%02d.png'%(outp,i); bpy.ops.render.render(write_still=True)
