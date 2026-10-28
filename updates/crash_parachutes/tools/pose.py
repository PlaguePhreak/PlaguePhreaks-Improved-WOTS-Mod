# Re-poses the seated game crew figure into a parachute hanging pose (linear blend skinning in numpy).
# Blender coords after import + x10: X = figure's left, -Y = facing direction, Z = up. Metres.
import bpy, sys, math, numpy as np, mathutils
a=sys.argv[sys.argv.index('--')+1:]
src,out=a[0],a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src, forward_axis='NEGATIVE_Z', up_axis='Y')
o=[x for x in bpy.context.scene.objects if x.type=='MESH'][0]
o.scale=(10,10,10); bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
V=np.array([v.co[:] for v in o.data.vertices])
B={
 'spine':(None,(0,0.20,-0.13),(0,0.21,0.42)),
 'head':('spine',(0,0.21,0.42),(0,0.22,0.72)),
 'thigh.L':('spine',(0.10,0.18,-0.13),(0.12,-0.25,-0.15)),
 'shin.L':('thigh.L',(0.12,-0.25,-0.15),(0.12,-0.22,-0.57)),
 'foot.L':('shin.L',(0.12,-0.22,-0.57),(0.12,-0.42,-0.63)),
 'upperarm.L':('spine',(0.19,0.20,0.36),(0.25,-0.07,0.26)),
 'forearm.L':('upperarm.L',(0.25,-0.07,0.26),(0.15,-0.33,0.22)),
}
for k in list(B):
    if k.endswith('.L'):
        p,h,t=B[k]; B[k[:-2]+'.R']=((p[:-2]+'.R') if p and p.endswith('.L') else p,(-h[0],h[1],h[2]),(-t[0],t[1],t[2]))
def n(v): v=np.array(v,float); return v/np.linalg.norm(v)
T={'spine':n((0,0.05,1)),'head':n((0,-0.05,1)),
   'thigh.L':n((0.06,-0.12,-1)),'shin.L':n((0.0,0.18,-1)),'foot.L':n((0,-1,-0.6)),
   'upperarm.L':n((0.14,-0.02,0.26)),'forearm.L':n((-0.13,-0.02,0.25))}
for k in list(T):
    if k.endswith('.L'): d=T[k]; T[k[:-2]+'.R']=np.array((-d[0],d[1],d[2]))
def rot(a_,b_):
    a_=n(a_); b_=n(b_); v=np.cross(a_,b_); c=np.dot(a_,b_)
    if np.linalg.norm(v)<1e-8: return np.eye(3)
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]); return np.eye(3)+K+K@K*(1/(1+c))
G={}
order=['spine','head','thigh.L','thigh.R','shin.L','shin.R','foot.L','foot.R','upperarm.L','upperarm.R','forearm.L','forearm.R']
for k in order:
    p,h,t=B[k]; h=np.array(h); t=np.array(t)
    nh=h if p is None else G[p][0]@h+G[p][1]
    R=rot(t-h,T[k]); G[k]=(R, nh-R@h)
def segd(P,h,t):
    h=np.array(h); t=np.array(t); d=t-h; u=np.clip(((P-h)@d)/(d@d),0,1); return np.linalg.norm(P-(h+u[:,None]*d),axis=1)
D=np.stack([segd(V,B[k][1],B[k][2]) for k in order],1)
W=np.exp(-(D-D.min(1,keepdims=True))/0.025); W[W<0.05]=0; W/=W.sum(1,keepdims=True)
NV=np.zeros_like(V)
for i,k in enumerate(order):
    R,off=G[k]; NV+=W[:,i:i+1]*((V@R.T)+off)
R,off=G['spine']; chest=R@np.array((0,0.12,0.32))+off
NV-=chest
for v,p in zip(o.data.vertices,NV): v.co=p
o.data.update()
o.name=a[3] if len(a)>3 else 'pilot'
bpy.ops.export_scene.fbx(filepath=out, path_mode='COPY', embed_textures=True)
mn=NV.min(0); mx=NV.max(0); print('posed bounds',mn.round(2),mx.round(2))
sc=bpy.context.scene
l=bpy.data.objects.new("l",bpy.data.lights.new("l","SUN")); sc.collection.objects.link(l); l.rotation_euler=(0.6,0.3,0.8); l.data.energy=3
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.5,0.5,0.5)
sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.render.resolution_x=400; sc.render.resolution_y=500
ctr=mathutils.Vector(((mn+mx)/2).tolist())
for nm,loc in (('side',(5,0,0)),('front',(0,-5,0)),('three',(3,-3,1))):
    c=bpy.data.objects.new(nm,bpy.data.cameras.new(nm)); sc.collection.objects.link(c); c.location=ctr+mathutils.Vector(loc)
    c.data.type='ORTHO'; c.data.ortho_scale=2.4
    c.rotation_euler=(ctr-c.location).to_track_quat('-Z','Y').to_euler(); sc.camera=c
    sc.render.filepath=out.replace('.fbx','_'+nm+'.png'); bpy.ops.render.render(write_still=True)
