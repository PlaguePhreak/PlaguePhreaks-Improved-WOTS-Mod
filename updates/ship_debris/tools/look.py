# Preview renders for the debris kit. python3 look.py -- <kit.blend> <tex_dir> <out_prefix>
#   <out_prefix>_kit.png   all pieces on a grey floor, labelled
#   <out_prefix>_sea.png   the pieces scattered on a sea with an oil slick, seen from about 60 m up
import bpy, sys, os, math, random
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; BLEND,TEX,OUTP=a
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=48; sc.cycles.device='CPU'
sc.render.resolution_x=1600; sc.render.resolution_y=900
sc.view_settings.view_transform='Standard'
pieces=[o for o in sc.objects if o.type=='MESH']
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Color'].default_value=(0.55,0.65,0.8,1); w.node_tree.nodes['Background'].inputs['Strength'].default_value=0.6
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun)
sun.data.energy=3.5; sun.rotation_euler=(math.radians(50),0,math.radians(30))
def cam(loc,look,lens=35):
    c=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(c); c.location=loc
    c.rotation_euler=(Vector(look)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); c.data.lens=lens; sc.camera=c; return c
# ---- kit sheet ----
fl=bpy.data.meshes.new('fl'); fl.from_pydata([(-40,-40,-0.6),(40,-40,-0.6),(40,40,-0.6),(-40,40,-0.6)],[],[(0,1,2,3)])
flo=bpy.data.objects.new('floor',fl); sc.collection.objects.link(flo)
fm=bpy.data.materials.new('fm'); fm.use_nodes=True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.35,0.37,0.4,1); fl.materials.append(fm)
labels=[]
for o in pieces:
    bpy.ops.object.text_add(location=o.location+Vector((0,-1.9,-0.55))); t=bpy.context.object; t.data.body=o.name.replace('_',' ')
    t.data.size=0.45; t.data.align_x='CENTER'; labels.append(t)
    lm=bpy.data.materials.new('lm'); lm.use_nodes=True; lm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.95,0.95,0.9,1); t.data.materials.append(lm)
cam((0,-17,15),(0,-1.5,0),30)
sc.render.filepath=OUTP+'_kit.png'
if not os.environ.get('NOKIT'): bpy.ops.render.render(write_still=True)
w.node_tree.nodes['Background'].inputs['Color'].default_value=(0.45,0.6,0.85,1)
for t in labels: bpy.data.objects.remove(t)
bpy.data.objects.remove(flo)
# ---- sea scene ----
bpy.ops.mesh.primitive_plane_add(size=400,location=(0,0,0)); sea=bpy.context.object
sm=bpy.data.materials.new('sea'); sm.use_nodes=True; p=sm.node_tree.nodes['Principled BSDF']
p.inputs['Base Color'].default_value=(0.03,0.09,0.13,1); p.inputs['Roughness'].default_value=0.12; sea.data.materials.append(sm)
nt=sm.node_tree; nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=0.6; nz.inputs['Detail'].default_value=8
tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1,2.5,1)
nt.links.new(tc.outputs['Object'],mp.inputs[0]); nt.links.new(mp.outputs[0],nz.inputs['Vector'])
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.35; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
def slick(name, tex, loc, size, rot, stretch=1.0, z=0.12):
    me=bpy.data.meshes.new(name); s=size/2
    me.from_pydata([(-s*stretch,-s,0),(s*stretch,-s,0),(s*stretch,s,0),(-s*stretch,s,0)],[],[(0,1,2,3)])
    me.uv_layers.new(); uv=me.uv_layers[0].data
    for i,c in enumerate([(0,0),(1,0),(1,1),(0,1)]): uv[i].uv=c
    o=bpy.data.objects.new(name,me); sc.collection.objects.link(o); o.location=(loc[0],loc[1],z); o.rotation_euler=(0,0,rot)
    mt=bpy.data.materials.new(name); mt.use_nodes=True; nt=mt.node_tree; pb=nt.nodes['Principled BSDF']
    im=nt.nodes.new('ShaderNodeTexImage'); im.image=bpy.data.images.load(os.path.join(TEX,tex))
    mix=nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type='MULTIPLY'; mix.inputs[0].default_value=1; mix.inputs[2].default_value=(0.06,0.05,0.04,1)
    nt.links.new(im.outputs['Color'],mix.inputs[1]); nt.links.new(mix.outputs[0],pb.inputs['Base Color'])
    al=nt.nodes.new('ShaderNodeMath'); al.operation='MULTIPLY'; al.inputs[1].default_value=0.7
    nt.links.new(im.outputs['Alpha'],al.inputs[0]); nt.links.new(al.outputs[0],pb.inputs['Alpha'])
    pb.inputs['Roughness'].default_value=0.05
    me.materials.append(mt); return o
slick('oilA','oil_slick_a.png',(0,0),70,0.3,z=0.02)
slick('oilB','oil_slick_c.png',(30,18),60,0.9,1.4,z=0.03)
slick('oilC','oil_slick_b.png',(-26,-12),45,2.0,z=0.04)
random.seed(4)
weights={'plank':6,'plank_short':5,'deck_section':2,'crate':3,'drum':3,'ammo_box':2,'carley_float':2,'life_ring':2,'hatch_cover':2,'steel_plate':2,'spar':2,'life_vest':3,'boat_capsized':1,'timber_burnt':4}
byname={o.name:o for o in pieces}; bag=[n for n,k in weights.items() for _ in range(k)]
for k in range(46):
    n=bag[k%len(bag)] if k<len(bag) else random.choice(bag); src=byname[n]
    o=src if k<len(pieces) and n not in [x.name for x in sc.objects if x.get('used')] else src.copy()
    if o is not src: sc.collection.objects.link(o)
    o['used']=1
    r=random.uniform(0,38)**1.0; ang=random.uniform(0,6.28)
    o.location=(r*math.cos(ang)*1.3, r*math.sin(ang), 0.0)
    o.rotation_euler=(math.radians(random.uniform(-6,6)),math.radians(random.uniform(-6,6)),random.uniform(0,6.28))
    if n=='drum' and random.random()<0.6: o.rotation_euler[0]=math.radians(90); o.location.z=0.15
    if n=='steel_plate': o.location.z=-0.2
for o in pieces:
    if not o.get('used'): o.hide_render=True
sun.rotation_euler=(math.radians(40),0,math.radians(140)); sun.data.energy=4
cam((0,-75,55),(0,0,0),40)
sc.render.filepath=OUTP+'_sea.png'; bpy.ops.render.render(write_still=True)
cam((6,-16,7),(2,2,0),35)
sc.render.filepath=OUTP+'_close.png'; bpy.ops.render.render(write_still=True)
