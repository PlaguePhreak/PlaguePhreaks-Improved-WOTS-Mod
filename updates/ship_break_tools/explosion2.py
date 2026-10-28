# Magazine explosion, procedural volume (no fluid sim): a fireball that bursts out of the water, rises on a stem of
# smoke and rolls into a dark mushroom cloud, the fire dying to embers. Rendered as RGBA frames for a sprite sheet.
# blender python: python3 explosion2.py -- outdir [frames] [px] [samples]
import bpy, sys, os, math
a=sys.argv[sys.argv.index('--')+1:]
out=a[0]; FR=int(a[1]) if len(a)>1 else 64; PX=int(a[2]) if len(a)>2 else 256; SM=int(a[3]) if len(a)>3 else 32
ONLY=[int(x) for x in a[4].split(',')] if len(a)>4 else None
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
# volume box in world units, object coords = world coords
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0)); box=bpy.context.active_object
box.scale=(14,14,16); box.location=(0,0,7.6); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
mat=bpy.data.materials.new('boom'); mat.use_nodes=True; nt=mat.node_tree; nt.nodes.clear(); N=nt.nodes; Lk=nt.links.new
def node(t, **kw):
    n=N.new(t)
    for k,v in kw.items(): setattr(n,k,v)
    return n
def val(v): n=node('ShaderNodeValue'); n.outputs[0].default_value=v; return n
def math_(op, a_, b_=None, clamp=False):
    n=node('ShaderNodeMath', operation=op); n.use_clamp=clamp
    for i,x in enumerate((a_,b_)):
        if x is None: continue
        if isinstance(x,(int,float)): n.inputs[i].default_value=x
        else: Lk(x, n.inputs[i])
    return n.outputs[0]
def vmath(op, a_, b_=None):
    n=node('ShaderNodeVectorMath', operation=op)
    for i,x in enumerate((a_,b_)):
        if x is None: continue
        if isinstance(x,tuple): n.inputs[i].default_value=x
        else: Lk(x, n.inputs[i])
    return n.outputs['Value'] if op in('LENGTH','DOT_PRODUCT','DISTANCE') else n.outputs['Vector']
P=node('ShaderNodeNewGeometry').outputs['Position']
# per-frame parameters (set from python before each render)
V={k:val(0.0) for k in ('cz','R','dens','fire','stemR','stemTop','w','core','flat')}
def comb(x,y,z):
    n=node('ShaderNodeCombineXYZ')
    for i,c in enumerate((x,y,z)):
        if isinstance(c,(int,float)): n.inputs[i].default_value=c
        else: Lk(c, n.inputs[i])
    return n.outputs[0]
# noise (4D, evolves with w)
def noise(scale, detail, rough, vec):
    n=node('ShaderNodeTexNoise', noise_dimensions='4D'); n.inputs['Scale'].default_value=scale; n.inputs['Detail'].default_value=detail
    n.inputs['Roughness'].default_value=rough; Lk(vec, n.inputs['Vector']); Lk(V['w'].outputs[0], n.inputs['W'])
    return n.outputs['Fac']
# --- cap / fireball: flattened sphere around (0,0,cz)
c=comb(0,0,V['cz'].outputs[0])
q=vmath('SUBTRACT', P, c)
sep=node('ShaderNodeSeparateXYZ'); Lk(q, sep.inputs[0])
qz=math_('MULTIPLY', sep.outputs[2], V['flat'].outputs[0])
qq=comb(sep.outputs[0], sep.outputs[1], qz)
dist=vmath('LENGTH', qq)
n1=noise(0.6, 8.0, 0.66, P)
n1c=math_('SUBTRACT', n1, 0.5)
# billow: radius modulated by noise
Rn=math_('ADD', V['R'].outputs[0], math_('MULTIPLY', n1c, math_('MULTIPLY', V['R'].outputs[0], 1.1)))
edge=math_('SUBTRACT', Rn, dist)                      # >0 inside
capd=math_('DIVIDE', edge, math_('MULTIPLY', V['R'].outputs[0], 0.18))
capd=math_('MINIMUM', math_('MAXIMUM', capd, 0.0), 1.0)
# --- stem: column from the sea up to the cap
sx=node('ShaderNodeSeparateXYZ'); Lk(P, sx.inputs[0])
rr=vmath('LENGTH', comb(sx.outputs[0], sx.outputs[1], 0))
n2=noise(0.9, 5.0, 0.6, P)
stemR=math_('MULTIPLY', V['stemR'].outputs[0], math_('ADD', 0.55, math_('MULTIPLY', n2, 0.9)))
# wider at the bottom (spray/base surge)
widen=math_('ADD', 1.0, math_('MULTIPLY', math_('MAXIMUM', math_('SUBTRACT', 0.8, sx.outputs[2]), 0.0), 0.7))
stemR=math_('MULTIPLY', stemR, widen)
sd=math_('DIVIDE', math_('SUBTRACT', stemR, rr), math_('MAXIMUM', V['stemR'].outputs[0], 0.05))
sd=math_('MINIMUM', math_('MAXIMUM', sd, 0.0), 1.0)
below=math_('LESS_THAN', sx.outputs[2], V['stemTop'].outputs[0])
above0=math_('GREATER_THAN', sx.outputs[2], -0.05)
sd=math_('MULTIPLY', math_('MULTIPLY', sd, below), above0)
sd=math_('MULTIPLY', sd, 0.75)
dens=math_('MAXIMUM', capd, sd)
# fine detail
n3=noise(2.4, 4.0, 0.55, P)
dens=math_('MULTIPLY', dens, math_('ADD', 0.45, math_('MULTIPLY', n3, 1.1)))
dens=math_('MULTIPLY', dens, V['dens'].outputs[0])
# fire: hot inner part of the cap (and the stem base early), patchy
inner=math_('ADD', math_('DIVIDE', edge, math_('MULTIPLY', V['R'].outputs[0], 0.75)), V['core'].outputs[0])
fire=math_('MULTIPLY', math_('MINIMUM', math_('MAXIMUM', inner, 0.0), 1.0), V['fire'].outputs[0])
n4=noise(1.3, 5.0, 0.6, P)
mask=math_('POWER', math_('MAXIMUM', math_('SUBTRACT', math_('MULTIPLY', n4, 3.0), 1.4), 0.0), 1.5)
fire=math_('MULTIPLY', fire, math_('MAXIMUM', mask, math_('MULTIPLY', V['core'].outputs[0], 0.8)))
fire=math_('ADD', fire, math_('MULTIPLY', math_('MULTIPLY', sd, V['core'].outputs[0]), 0.6))
fire=math_('MINIMUM', fire, 1.5)
pv=node('ShaderNodeVolumePrincipled')
pv.inputs['Color'].default_value=(0.13,0.128,0.125,1)
pv.inputs['Absorption Color'].default_value=(0.0,0.0,0.0,1)
Lk(math_('MULTIPLY', dens, 3.2), pv.inputs['Density'])
Lk(math_('MULTIPLY', fire, 30.0), pv.inputs['Blackbody Intensity'])
temp=math_('ADD', math_('ADD', 1400.0, math_('MULTIPLY', fire, 1300.0)), math_('MULTIPLY', V['core'].outputs[0], 500.0))
Lk(temp, pv.inputs['Temperature'])
o=node('ShaderNodeOutputMaterial'); Lk(pv.outputs[0], o.inputs['Volume'])
box.data.materials.append(mat)
# camera: orthographic, side on, sea level at 8% from the bottom
cam=bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
cam.data.type='ORTHO'; cam.data.ortho_scale=15.0
cam.location=(0,-40,-0.3+7.5); cam.rotation_euler=(math.radians(90),0,0); sc.camera=cam
sun=bpy.data.objects.new('sun', bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun)
sun.rotation_euler=(math.radians(55),0,math.radians(35)); sun.data.energy=3.0
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.55,0.6,0.66,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.9
sc.render.engine='CYCLES'; sc.cycles.samples=SM; sc.cycles.volume_bounces=1; sc.cycles.volume_step_rate=1.0
sc.cycles.use_denoising=True
sc.render.film_transparent=True
sc.render.resolution_x=PX; sc.render.resolution_y=PX
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGBA'
sc.view_settings.view_transform='Standard'
def ease(x): return 1-math.exp(-x)
for f in range(FR):
    if ONLY and f not in ONLY: continue
    t=f/(FR-1)               # 0..1 over the sheet (game plays it over ~8-10 s)
    V['R'].outputs[0].default_value=0.9+3.3*ease(t*11.0)+0.9*t
    V['cz'].outputs[0].default_value=0.9+1.2*ease(t*8)+6.8*t
    V['flat'].outputs[0].default_value=1.0+0.9*min(1,t*2.5)
    V['dens'].outputs[0].default_value=min(1,0.4+t*12)*(1.0-0.75*max(0,(t-0.55)/0.45)**1.6)
    V['fire'].outputs[0].default_value=(1.0 if t<0.08 else math.exp(-(t-0.08)*4.5))
    V['core'].outputs[0].default_value=max(0,1-t*10)*1.2
    V['stemR'].outputs[0].default_value=(0.3+1.1*ease(t*6))*(1.0 if t>0.04 else 0.4)
    V['stemTop'].outputs[0].default_value=V['cz'].outputs[0].default_value
    V['w'].outputs[0].default_value=t*2.2
    sc.render.filepath=os.path.join(out,'f%03d.png'%f); bpy.ops.render.render(write_still=True)
print("rendered")
