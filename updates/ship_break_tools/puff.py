import bpy, sys, math
out=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
bpy.ops.mesh.primitive_cube_add(size=2.2); box=bpy.context.active_object
mat=bpy.data.materials.new('p'); mat.use_nodes=True; nt=mat.node_tree; N=nt.nodes; N.clear(); L=nt.links.new
geo=N.new('ShaderNodeNewGeometry'); P=geo.outputs['Position']
ln=N.new('ShaderNodeVectorMath'); ln.operation='LENGTH'; L(P, ln.inputs[0])
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=2.2; nz.inputs['Detail'].default_value=6; nz.inputs['Roughness'].default_value=0.6; L(P,nz.inputs['Vector'])
m1=N.new('ShaderNodeMath'); m1.operation='MULTIPLY'; L(nz.outputs['Fac'],m1.inputs[0]); m1.inputs[1].default_value=0.9
a1=N.new('ShaderNodeMath'); a1.operation='ADD'; L(m1.outputs[0],a1.inputs[0]); a1.inputs[1].default_value=0.42
s1=N.new('ShaderNodeMath'); s1.operation='SUBTRACT'; L(a1.outputs[0],s1.inputs[0]); L(ln.outputs['Value'],s1.inputs[1])
d=N.new('ShaderNodeMath'); d.operation='MULTIPLY'; d.use_clamp=False; L(s1.outputs[0],d.inputs[0]); d.inputs[1].default_value=6.0
mx=N.new('ShaderNodeMath'); mx.operation='MAXIMUM'; L(d.outputs[0],mx.inputs[0]); mx.inputs[1].default_value=0
pv=N.new('ShaderNodeVolumePrincipled'); pv.inputs['Color'].default_value=(0.85,0.85,0.85,1); L(mx.outputs[0],pv.inputs['Density'])
o=N.new('ShaderNodeOutputMaterial'); L(pv.outputs[0],o.inputs['Volume'])
box.data.materials.append(mat)
cam=bpy.data.objects.new('c',bpy.data.cameras.new('c')); sc.collection.objects.link(cam)
cam.data.type='ORTHO'; cam.data.ortho_scale=2.3; cam.location=(0,-6,0); cam.rotation_euler=(math.radians(90),0,0); sc.camera=cam
sun=bpy.data.objects.new('s',bpy.data.lights.new('s','SUN')); sc.collection.objects.link(sun); sun.data.energy=4.5
sun.rotation_euler=(math.radians(35),math.radians(20),0)
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']; bg.inputs[0].default_value=(0.5,0.52,0.55,1); bg.inputs[1].default_value=0.8
sc.render.engine='CYCLES'; sc.cycles.samples=64; sc.cycles.volume_bounces=2; sc.cycles.use_denoising=True
sc.render.film_transparent=True; sc.render.resolution_x=sc.render.resolution_y=256
sc.render.image_settings.color_mode='RGBA'; sc.view_settings.view_transform='Standard'
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
