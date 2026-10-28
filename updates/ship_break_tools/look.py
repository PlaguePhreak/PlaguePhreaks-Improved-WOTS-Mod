# Textured render of OBJ files: blender python: python3 look.py -- out.png cam(side|q1|q2|top) file1.obj [file2.obj ...]
import bpy, sys, math, mathutils
a=sys.argv[sys.argv.index('--')+1:]
out, view, files = a[0], a[1], [f for f in a[2:] if not f.isdigit()]
bpy.ops.wm.read_factory_settings(use_empty=True)
for f in files:
    bpy.ops.wm.obj_import(filepath=f, forward_axis='NEGATIVE_Z', up_axis='Y')
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Roughness'].default_value=0.8
            if 'Specular IOR Level' in n.inputs: n.inputs['Specular IOR Level'].default_value=0.2
            if m.name.startswith('glass'): n.inputs['Base Color'].default_value=(0.2,0.25,0.3,1)
sc=bpy.context.scene
mn=mathutils.Vector((1e9,)*3); mx=-mn
for o in sc.objects:
    if o.type!='MESH': continue
    for v in o.bound_box:
        w=o.matrix_world@mathutils.Vector(v); mn=mathutils.Vector(map(min,mn,w)); mx=mathutils.Vector(map(max,mx,w))
ctr=(mn+mx)/2; r=(mx-mn).length
V={'side':(1,0,0.12),'q1':(0.75,-0.75,0.45),'q2':(-0.6,0.7,0.4),'top':(0.05,-0.02,1),'q3':(0.8,0.6,0.35),'low':(0.9,-0.3,0.08)}
c=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(c)
if view.startswith('tear'):
    # tearB<cut> looks at the bow piece's broken end from astern, tearS<cut> at the stern piece from ahead
    cz=float(view[5:]); s_=-1 if view[4]=='B' else 1
    tgt=mathutils.Vector((0,-cz,0.45)); c.location=tgt+mathutils.Vector((2.2,-s_*3.2,1.6)); c.data.lens=35
    c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
else:
    c.location=ctr+mathutils.Vector(V.get(view,V['q1'])).normalized()*r*0.95; c.data.lens=40
    c.rotation_euler=(ctr-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.7,0.2,0.9); l.data.energy=4
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.62,0.7,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.8
sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.render.resolution_x=int(a[-1]) if a[-1].isdigit() else 900; sc.render.resolution_y=int(sc.render.resolution_x*0.55)
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
