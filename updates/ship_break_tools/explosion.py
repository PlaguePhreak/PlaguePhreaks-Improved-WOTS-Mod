# Magazine explosion: Mantaflow fire + smoke sim, rendered to RGBA frames for a sprite sheet.
# blender python: python3 explosion.py -- outdir [res] [frames] [px]
import bpy, sys, os, math, random
a=sys.argv[sys.argv.index('--')+1:]
out=a[0]; RES=int(a[1]) if len(a)>1 else 96; FR=int(a[2]) if len(a)>2 else 64; PX=int(a[3]) if len(a)>3 else 256
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=FR
# domain: 8 x 8 x 12, ground at z=0 (sea level)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,5)); dom=bpy.context.active_object; dom.scale=(9,9,12)
bpy.ops.object.modifier_add(type='FLUID'); dm=dom.modifiers[-1]; dm.fluid_type='DOMAIN'
ds=dm.domain_settings; ds.domain_type='GAS'; ds.resolution_max=RES; ds.cache_frame_start=1; ds.cache_frame_end=FR
ds.cache_directory=os.path.join(out,'cache'); ds.cache_type='ALL'
ds.use_adaptive_domain=False
ds.alpha=1.0; ds.beta=2.4            # smoke rises strongly with heat
ds.vorticity=0.35
ds.burning_rate=0.55; ds.flame_smoke=1.4; ds.flame_vorticity=0.6; ds.flame_ignition=1.25; ds.flame_max_temp=3.0
ds.use_dissolve_smoke=True; ds.dissolve_speed=160
ds.use_noise=False
ds.time_scale=1.0
# flow: a burst sphere just above the water; on for the first frames only
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(0,0,0.9)); src=bpy.context.active_object
bpy.ops.object.modifier_add(type='FLUID'); fm=src.modifiers[-1]; fm.fluid_type='FLOW'
fs=fm.flow_settings; fs.flow_type='BOTH'; fs.flow_behavior='INFLOW'; fs.flow_source='MESH'
fs.fuel_amount=2.4; fs.temperature=3.0; fs.density=1.0; fs.smoke_color=(0.08,0.07,0.06)
fs.use_initial_velocity=True; fs.velocity_normal=9.0; fs.velocity_factor=0.0
fs.velocity_coord=(0,0,4.0)
fs.subframes=2
# keyframe the flow on 1..6, off afterwards
for f,on in ((1,True),(6,True),(7,False)):
    sc.frame_set(f); fs.use_inflow=on; fs.keyframe_insert('use_inflow')
src.hide_render=True
print("baking", RES, FR)
sc.frame_set(1)
with bpy.context.temp_override(object=dom, active_object=dom, selected_objects=[dom]):
    bpy.ops.fluid.bake_all()
print("baked")
# volume shader: smoke density + fire emission (blackbody)
mat=bpy.data.materials.new('vol'); mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear()
o=nt.nodes.new('ShaderNodeOutputMaterial'); pv=nt.nodes.new('ShaderNodeVolumePrincipled')
pv.inputs['Density'].default_value=6.0
pv.inputs['Color'].default_value=(0.07,0.065,0.06,1)
pv.inputs['Blackbody Intensity'].default_value=1.0
pv.inputs['Emission Strength'].default_value=0.0
atr=nt.nodes.new('ShaderNodeAttribute'); atr.attribute_name='flame'
mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.0; mr.inputs['From Max'].default_value=1.0
mr.inputs['To Min'].default_value=1100; mr.inputs['To Max'].default_value=2600
nt.links.new(atr.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], pv.inputs['Temperature'])
mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=14.0
nt.links.new(atr.outputs['Fac'], mul.inputs[0]); nt.links.new(mul.outputs[0], pv.inputs['Blackbody Intensity'])
nt.links.new(pv.outputs[0], o.inputs['Volume'])
dom.data.materials.append(mat)
# camera: orthographic side view, sea level near the bottom of the frame
cam=bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
cam.data.type='ORTHO'; cam.data.ortho_scale=12.0
cam.location=(0,-30,5.4); cam.rotation_euler=(math.radians(90),0,0); sc.camera=cam
sun=bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun)
sun.rotation_euler=(math.radians(50),0,math.radians(30)); sun.data.energy=3.5
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.5,0.55,0.62,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.7
sc.render.engine='CYCLES'; sc.cycles.samples=int(os.environ.get('SAMPLES','24')); sc.cycles.volume_bounces=1
sc.cycles.volume_step_rate=2.0
sc.render.film_transparent=True
sc.render.resolution_x=PX; sc.render.resolution_y=PX
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
sc.view_settings.view_transform='Standard'
for f in range(1,FR+1):
    sc.frame_set(f); sc.render.filepath=os.path.join(out,'f%03d.png'%f); bpy.ops.render.render(write_still=True)
print("rendered")
