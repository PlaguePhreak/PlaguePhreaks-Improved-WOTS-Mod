# Preview: the two pieces sinking in a V on a sea plane. python3 scene.py -- out.png cut bow.obj stern.obj [view]
import bpy, sys, math, mathutils
from mathutils import Vector, Matrix
a=sys.argv[sys.argv.index('--')+1:]
out=a[0]; cut=float(a[1]); view=a[4] if len(a)>4 else 'a'
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def load(f,pitch,dz,dy,roll):
    before=set(sc.objects); bpy.ops.wm.obj_import(filepath=f, forward_axis='NEGATIVE_Z', up_axis='Y')
    for o in set(sc.objects)-before:
        piv=Vector((0,-cut,0))
        M=Matrix.Translation(piv+Vector((0,-dz,dy)))@Matrix.Rotation(math.radians(roll),4,'Y')@Matrix.Rotation(math.radians(pitch),4,'X')@Matrix.Translation(-piv)
        o.matrix_world=M@o.matrix_world
load(a[2], -28, 0.35, -0.55, 6)     # bow piece, bow up
load(a[3], 22, -0.35, -0.55, -8)    # stern piece, stern up
for m in bpy.data.materials:
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED': n.inputs['Roughness'].default_value=0.8
bpy.ops.mesh.primitive_plane_add(size=80, location=(0,0,0))
sea=sc.objects[-1] if False else bpy.context.active_object
sm=bpy.data.materials.new('sea'); sm.use_nodes=True; b=sm.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.02,0.07,0.1,1); b.inputs['Roughness'].default_value=0.15
if 'Transmission Weight' in b.inputs: b.inputs['Transmission Weight'].default_value=0.0
sea.data.materials.append(sm)
c=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(c)
tgt=Vector((0,-cut,0.6))
loc={'a':(9,-4,4.5),'b':(-8,6,3.5),'c':(7,1,2.0)}[view]
c.location=tgt+Vector(loc); c.data.lens=38; c.rotation_euler=(tgt-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.8,0.2,0.9); l.data.energy=4
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.65,0.75,1)
sc.render.engine='CYCLES'; sc.cycles.samples=24; sc.render.resolution_x=1000; sc.render.resolution_y=560
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
