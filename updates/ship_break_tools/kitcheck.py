# Does what the game will do with a .brk kit, to check it: clip the ship's own mesh at cut +- band, add the kit,
# write the two pieces as OBJ (game coords -> OBJ x negated, winding reversed).
# python3 -I kitcheck.py ship.obj kit.brk outprefix
import sys, struct, gzip, numpy as np
def read_kit(p):
    d=open(p,'rb').read()
    if d[:2]==b'\x1f\x8b': d=gzip.decompress(d)
    o=0
    def rd(fmt):
        nonlocal o; r=struct.unpack_from('<'+fmt,d,o); o+=struct.calcsize('<'+fmt); return r
    def rs():
        n=rd('i')[0]; nonlocal o; s=d[o:o+n].decode(); o+=n; return s
    v=d[:4]; o=4
    cut,band=rd('ff')
    if v==b'BRK1': rs(); rd('16f')
    mv=[rs() for _ in range(rd('i')[0])]; n=rd('i')[0]; pieces=[]
    for _ in range(n):
        side,nc=rd('bi'); ch=[]
        for _ in range(nc):
            mn=rs(); cls=rs(); nv=rd('i')[0]
            if v==b'BRK1':
                P=np.array(rd('%df'%(3*nv))).reshape(-1,3); N=np.array(rd('%db'%(3*nv))).reshape(-1,3)/127.0
                U=np.array(rd('%df'%(2*nv))).reshape(-1,2)
            else:
                lo=np.array(rd('3f')); sc=np.array(rd('3f')); P=lo+np.array(rd('%dH'%(3*nv))).reshape(-1,3)/65535.0*sc
                N=np.array(rd('%db'%(3*nv))).reshape(-1,3)/127.0
                lo=np.array(rd('2f')); sc=np.array(rd('2f')); U=lo+np.array(rd('%dH'%(2*nv))).reshape(-1,2)/65535.0*sc
            ni=rd('i')[0]; I=np.array(rd('%dH'%ni)).reshape(-1,3)
            ch.append((mn,cls,P,N,U,I))
        pieces.append((side,ch))
    return cut,band,mv,None,pieces
if __name__!='__main__': raise SystemExit
shipobj, kit, outp = sys.argv[1], sys.argv[2], sys.argv[3]
cut,band,ref,M,pieces=read_kit(kit)
# ship obj (OBJ coords) -> per material triangles in game coords
V=[];T=[];Nn=[];F={};cur=None
for l in open(shipobj):
    p=l.split()
    if not p: continue
    if p[0]=='v': V.append((-float(p[1]),float(p[2]),float(p[3])))
    elif p[0]=='vt': T.append((float(p[1]),float(p[2])))
    elif p[0]=='vn': Nn.append((-float(p[1]),float(p[2]),float(p[3])))
    elif p[0]=='usemtl': cur=p[1]
    elif p[0]=='f':
        ids=[tuple(int(x)-1 for x in q.split('/')) for q in p[1:]]
        F.setdefault(cur,[]).append(ids[::-1])
V=np.array(V);T=np.array(T)
def clip(keep_bow):
    # keep z >= cut+band (bow) or z <= cut-band (stern); split straddling triangles exactly
    zc=cut+band if keep_bow else cut-band; s=1 if keep_bow else -1
    out={}
    for m,tris in F.items():
        lst=out.setdefault(m,[])
        for tri in tris:
            pts=[(V[a[0]],T[a[1]]) for a in tri]
            dd=[(p[0][2]-zc)*s for p in pts]
            if min(dd)>=0: lst.append(pts); continue
            if max(dd)<=0: continue
            poly=[]
            for i in range(3):
                j=(i+1)%3; pi,pj=pts[i],pts[j]; di,dj=dd[i],dd[j]
                if di>=0: poly.append(pi)
                if (di>=0)!=(dj>=0):
                    t=di/(di-dj); poly.append((pi[0]+(pj[0]-pi[0])*t, pi[1]+(pj[1]-pi[1])*t))
            for k in range(1,len(poly)-1): lst.append([poly[0],poly[k],poly[k+1]])
    return out
for side,ch in pieces:
    body=clip(side==1)
    lines=["mtllib kit.mtl"]; vn=0
    for m,tl in body.items():
        lines.append(f"usemtl {m}")
        for t in tl:
            for p,uv in t: lines.append(f"v {-p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"); lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
            lines.append(f"f {vn+3}/{vn+3} {vn+2}/{vn+2} {vn+1}/{vn+1}"); vn+=3
    for mn,cls,P,N,U,I in ch:
        key='burnt' if cls=='burnt' else None
        lines.append(f"usemtl {key or 'K_'+mn}")
        base=vn
        for p,u in zip(P,U): lines.append(f"v {-p[0]:.6f} {p[1]:.6f} {p[2]:.6f}"); lines.append(f"vt {u[0]:.6f} {u[1]:.6f}")
        for a,b,c in I: lines.append(f"f {base+c+1}/{base+c+1} {base+b+1}/{base+b+1} {base+a+1}/{base+a+1}")
        vn+=len(P)
    open(f"{outp}_{'bow' if side==1 else 'stern'}.obj","w").write("\n".join(lines)+"\n")
    print(side, sum(len(v) for v in body.values()), "clipped tris +", sum(len(c[5]) for c in ch), "kit tris")
