# Ship bundle -> OBJ for Blender (LOD0 only, every renderer, every submesh with its own material) + diffuse PNGs
# + <name>_mats.json (material key -> real material name, class, texture; and the reference object's matrix).
# Works for stock models (materials from _model.txt) and the modded ones (materials inside the bundle).
# python3 -I ship2mesh.py <sea folder> <name> <outdir>
# Coordinates: game/Unity space of the bundle root (1 = 10 m, +z = bow). OBJ x = -game x (winding reversed).
import UnityPy, sys, os, json, numpy as np
from UnityPy.helpers.MeshHelper import MeshHandler
sea, name, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
folder=os.path.join(sea,name)
os.makedirs(outdir, exist_ok=True)
env = UnityPy.load(os.path.join(folder, name))
def quat(q):
    x,y,z,w=q.x,q.y,q.z,q.w
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def local(tr):
    M=np.eye(4); M[:3,:3]=quat(tr.m_LocalRotation)@np.diag([tr.m_LocalScale.x,tr.m_LocalScale.y,tr.m_LocalScale.z])
    M[:3,3]=[tr.m_LocalPosition.x,tr.m_LocalPosition.y,tr.m_LocalPosition.z]; return M
def world(tr):
    # relative to the bundle's root object (the root's own transform is left out: the game puts the root at the unit)
    M=np.eye(4); t=tr
    while True:
        p=t.m_Father
        if not (p and p.path_id): break
        M=local(t)@M; t=p.read()
    return M
# stock material table
raw=open(os.path.join(folder,name+"_model.txt"),encoding="utf-8-sig").read()
dec=json.JSONDecoder(); model,i=dec.raw_decode(raw); mats,_=dec.raw_decode(raw[i:].lstrip())
stockMats={}
for k,mn in enumerate(model.get("meshNames",[])):
    if k<len(model.get("materialsOnMeshIndex",[])):
        stockMats[mn]=[mats["materialName"][j] for j in json.loads(model["materialsOnMeshIndex"][k])["mats"]]
# parts the game moves (turrets, guns, directors, props, rudder...): in game they stay whole, so the break kit leaves them out
MOVE=set()
def collect(o, key=''):
    if isinstance(o, dict):
        for k,v in o.items(): collect(v, k)
    elif isinstance(o, list):
        for v in o:
            if isinstance(v,str) and v.startswith('{'):
                try: collect(json.loads(v), key)
                except Exception: pass
            elif isinstance(v,str) and (key in ('baseTransformNames','propellerHubs','propellerBlades','propellerBlurs','rudder','directors','movingPart','divePlanes') or key.endswith('TransformNames')): MOVE.add(v)
            else: collect(v, key)
    elif isinstance(o,str) and o.startswith('{'):
        try: collect(json.loads(o), key)
        except Exception: pass
collect(model)
def moving(tr):
    t=tr
    while True:
        nm=t.m_GameObject.read().m_Name
        if nm in MOVE: return True
        p=t.m_Father
        if not (p and p.path_id): return False
        t=p.read()
def classify(nm, tex, onHull):
    import re
    s=(nm+" "+(tex or "")).lower()
    if 'rigging' in s or re.search(r'(^|[ _])(rope|net)(_|$| )', s): return 'rigging'
    if 'glass' in s or 'transparen' in s: return 'glass'
    if 'acc' in nm.lower(): return 'acc'
    return 'hull' if onHull else 'acc'
SKIP=('LOD1','LOD2','LOD3','Collider','Particles_','COL_')
keys={}   # (name) -> key
info={}
texs={}
out=[f"mtllib {name}.mtl"]; vo=to=0; parts=0; ref=None; movingObjs=set()
def texname(m):
    for k,v in m.m_SavedProperties.m_TexEnvs:
        if k=='_MainTex' and v.m_Texture.path_id: return v.m_Texture
    return None
for obj in env.objects:
    if obj.type.name!="MeshFilter": continue
    mf=obj.read()
    try: mesh=mf.m_Mesh.read(); go=mf.m_GameObject.read()
    except Exception as e: print("skip",e); continue
    if any(s in mesh.m_Name for s in SKIP) or any(s in go.m_Name for s in SKIP): continue
    rend=None; tr=None
    for c in go.m_Component:
        r=(c.component if hasattr(c,'component') else c).read(); tn=r.object_reader.type.name
        if tn=="Transform": tr=r
        if tn=="MeshRenderer": rend=r
    if rend is None or not getattr(rend,'m_Enabled',1): continue
    M=world(tr); R=M[:3,:3]; Rn=np.linalg.inv(R).T
    onHull=go.m_Name in ('Main_LOD0','Hull')
    if onHull and ref is None: ref=(go.m_Name, M.tolist())
    h=MeshHandler(mesh); h.process()
    V=np.array(h.m_Vertices,dtype=np.float64)[:, :3]
    N=np.array(h.m_Normals,dtype=np.float64)[:, :3] if h.m_Normals else np.zeros_like(V)
    UV=np.array(h.m_UV0,dtype=np.float64)[:, :2] if h.m_UV0 else np.zeros((len(V),2))
    Vw=(V@M[:3,:3].T)+M[:3,3]; Nw=N@Rn.T; Nw/=np.maximum(np.linalg.norm(Nw,axis=1,keepdims=True),1e-9)
    tris=h.get_triangles()
    # material names per submesh
    rmats=[m.read() if m.path_id else None for m in rend.m_Materials]
    snames=stockMats.get(go.m_Name) or stockMats.get(mesh.m_Name)
    if moving(tr): movingObjs.add(go.m_Name)
    out.append(f"o {go.m_Name}")
    for v in Vw: out.append(f"v {-v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
    for t in UV: out.append(f"vt {t[0]:.6f} {t[1]:.6f}")
    for n in Nw: out.append(f"vn {-n[0]:.5f} {n[1]:.5f} {n[2]:.5f}")
    for si,tl in enumerate(tris):
        if snames: mname=snames[min(si,len(snames)-1)]; tx=None
        else:
            m=rmats[min(si,len(rmats)-1)] if rmats else None
            mname=m.m_Name if m else 'none'; tx=texname(m) if m else None
        if mname not in keys:
            txn=tx.read().m_Name if tx else None
            cls=classify(mname, txn, onHull)
            key=f"{cls}_{len(keys)}"; keys[mname]=key; info[key]={'name':mname,'cls':cls,'tex':txn}
            if tx: texs[key]=tx
        if onHull and info[keys[mname]]['cls']=='acc' and classify(mname,info[keys[mname]]['tex'],True)=='hull':
            info[keys[mname]]['cls']='hull'      # also used on the hull: counts as hull plating
        out.append(f"usemtl {keys[mname]}")
        for a,b,c in tl:
            out.append(f"f {c+1+vo}/{c+1+to}/{c+1+vo} {b+1+vo}/{b+1+to}/{b+1+vo} {a+1+vo}/{a+1+to}/{a+1+vo}")
    vo+=len(V); to+=len(V); parts+=1
open(os.path.join(outdir,name+".obj"),"w").write("\n".join(out)+"\n")
# textures: modded = from the material; stock = the folder's _tex bundle (hull) or a bundle named like the acc material
def stock_tex(mname, cls):
    cands=[]
    for d in (folder, os.path.join(sea,'_common')):
        if not os.path.isdir(d): continue
        for f in os.listdir(d):
            fl=f.lower()
            if cls=='acc' and fl==mname.lower(): cands.insert(0,os.path.join(d,f))
            if cls!='acc' and fl.startswith(name+"_tex"): cands.append(os.path.join(d,f))
    if cls=='acc':
        own=mname.split('_')[0].lower()
        d=os.path.join(sea,own)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.lower()==mname.lower(): cands.append(os.path.join(d,f))
    for p in cands:
        try:
            for o in UnityPy.load(p).objects:
                if o.type.name=="Texture2D":
                    t=o.read()
                    if t.m_Name.endswith("_D") or '_D_' in t.m_Name or t.m_Name.lower().endswith('_d'): return t
        except Exception as e: print("tex fail",p,e)
    return None
mtl=""
done={}
for key,inf in info.items():
    fn=None
    t=texs[key].read() if key in texs else (stock_tex(inf['name'],'acc' if 'acc' in inf['name'].lower() else 'hull') if inf['cls'] in('hull','acc') else None)
    if t is not None:
        fn=f"{name}_{t.m_Name}.png"
        if fn not in done:
            try: t.image.save(os.path.join(outdir,fn)); done[fn]=1
            except Exception as e: print("img fail",e); fn=None
    inf['png']=fn
    col={'rigging':'0.1 0.1 0.1','glass':'0.3 0.4 0.5'}.get(inf['cls'],'0.6 0.6 0.6')
    mtl+=f"newmtl {key}\nKd {col}\n"+(f"map_Kd {fn}\n" if fn else "")
open(os.path.join(outdir,name+".mtl"),"w").write(mtl)
json.dump({'mats':info,'ref':ref,'parts':parts,'verts':vo,'moving':sorted(movingObjs)},open(os.path.join(outdir,name+"_mats.json"),"w"),indent=1)
print(name,"parts",parts,"verts",vo,"mats",len(info),"ref",ref[0] if ref else None,"moving",len(movingObjs))
