# Ship bundle -> OBJ (LOD0 only, parts placed with their transforms, game units: 1 = 10 m) + diffuse PNG.
# python3 -I ship2obj.py <unit folder> <name> <outdir>
import UnityPy, sys, os, numpy as np
folder, name, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(outdir, exist_ok=True)
env = UnityPy.load(os.path.join(folder, name))
def quat(q):
    x,y,z,w=q.x,q.y,q.z,q.w
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def local(tr):
    M=np.eye(4); M[:3,:3]=quat(tr.m_LocalRotation)@np.diag([tr.m_LocalScale.x,tr.m_LocalScale.y,tr.m_LocalScale.z])
    M[:3,3]=[tr.m_LocalPosition.x,tr.m_LocalPosition.y,tr.m_LocalPosition.z]; return M
def world(tr):
    M=local(tr); p=tr.m_Father
    while p and p.path_id:
        pt=p.read(); M=local(pt)@M; p=pt.m_Father
    return M
import json
mt=json.loads(open(os.path.join(folder,name+"_model.txt"),encoding="utf-8-sig").read().split("\n")[0].strip()) if False else None
raw=open(os.path.join(folder,name+"_model.txt"),encoding="utf-8-sig").read()
dec=json.JSONDecoder(); model,i=dec.raw_decode(raw); mats,_=dec.raw_decode(raw[i:].lstrip())
matOf={}
for k,mn in enumerate(model["meshNames"]):
    idx=json.loads(model["materialsOnMeshIndex"][k])["mats"][0]
    nm=mats["materialName"][idx]
    matOf[mn]='acc' if 'acc' in nm.lower() else ('rigging' if 'rigging' in nm.lower() else ('glass' if 'transparen' in nm.lower() else 'hull'))
SKIP=('LOD1','LOD2','Collider','Particles_')
out=[f"mtllib {name}.mtl"]; vo=to=no=0; n=0
for obj in env.objects:
    if obj.type.name!="MeshFilter": continue
    mf=obj.read()
    try: mesh=mf.m_Mesh.read(); go=mf.m_GameObject.read()
    except Exception as e: print("skip",e); continue
    if any(s in mesh.m_Name for s in SKIP) or any(s in go.m_Name for s in SKIP): continue
    has_r=False; tr=None
    for c in go.m_Component:
        cc=c.component if hasattr(c,'component') else c
        r=cc.read(); tn=r.object_reader.type.name
        if tn=="Transform": tr=r
        if tn=="MeshRenderer": has_r=True
    if not has_r: continue
    M=world(tr); R=M[:3,:3]
    mat=matOf.get(go.m_Name,'acc')
    txt=mesh.export().splitlines(); vs=ts=ns=0
    out.append(f"o {go.m_Name}"); out.append(f"usemtl {mat}")
    for l in txt:
        p=l.split()
        if not p: continue
        if p[0]=='v':
            v=np.array([-float(p[1]),float(p[2]),float(p[3]),1]); w=M@v
            out.append(f"v {-w[0]:.6f} {w[1]:.6f} {w[2]:.6f}"); vs+=1
        elif p[0]=='vn':
            v=R@np.array([-float(p[1]),float(p[2]),float(p[3])]); v/=np.linalg.norm(v) or 1
            out.append(f"vn {-v[0]:.6f} {v[1]:.6f} {v[2]:.6f}"); ns+=1
        elif p[0]=='vt': out.append(l); ts+=1
        elif p[0]=='f':
            fs=[]
            for q in p[1:]:
                a=q.split('/'); a=[str(int(a[0])+vo), (str(int(a[1])+to) if len(a)>1 and a[1] else ''), (str(int(a[2])+no) if len(a)>2 and a[2] else '')]
                fs.append('/'.join(a))
            out.append("f "+" ".join(fs))
    vo+=vs; to+=ts; no+=ns; n+=1; print(go.m_Name, mesh.m_Name, vs)
open(os.path.join(outdir,name+".obj"),"w").write("\n".join(out)+"\n")
# diffuse
tex={}
for f in os.listdir(folder):
    kind='acc' if f.startswith(name+"_acc") else ('hull' if f.startswith(name+"_tex") else None)
    if not kind: continue
    for o in UnityPy.load(os.path.join(folder,f)).objects:
        if o.type.name=="Texture2D":
            d=o.read()
            if d.m_Name.endswith("_D"): fn=f"{name}_{kind}_D.png"; d.image.save(os.path.join(outdir,fn)); tex[kind]=fn
mtl=""
for k in ('hull','acc'):
    mtl+=f"newmtl {k}\nKd 1 1 1\n"+(f"map_Kd {tex[k]}\n" if k in tex else "")
mtl+="newmtl rigging\nKd 0.1 0.1 0.1\nnewmtl glass\nKd 0.3 0.4 0.5\n"
open(os.path.join(outdir,name+".mtl"),"w").write(mtl)
print("parts",n,"verts",vo,"tex",tex)
