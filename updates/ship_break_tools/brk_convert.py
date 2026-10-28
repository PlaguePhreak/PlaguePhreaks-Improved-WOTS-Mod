# BRK1 (gzip, float) -> BRK2 (raw, 16-bit quantized). python3 -I brk_convert.py file.brk [...]
import sys, struct, os
sys.argv_saved=sys.argv; sys.argv=[sys.argv[0],'x','x','x']
here=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(here,'kitcheck.py')).read().split("if __name__!='__main__'")[0]
exec(src)
for p in sys.argv_saved[1:]:
    if open(p,'rb').read(2)!=b'\x1f\x8b': print(p,'already BRK2'); continue
    cut,band,mv,_,pieces=read_kit(p)
    def s(b,t): t=t.encode(); b.append(struct.pack('<i',len(t))+t)
    b=[b'BRK2', struct.pack('<ff',cut,band), struct.pack('<i',len(mv))]
    for m in mv: s(b,m)
    b.append(struct.pack('<i',len(pieces)))
    def q16(A):
        lo=A.min(0); sc=A.max(0)-lo; sc[sc==0]=1e-6
        return lo, sc, np.clip(np.round((A-lo)/sc*65535),0,65535).astype('<u2')
    for side,ch in pieces:
        b.append(struct.pack('<bi',side,len(ch)))
        for mn,cls,P,N,U,I in ch:
            s(b,mn); s(b,cls); b.append(struct.pack('<i',len(P)))
            lo,sc,q=q16(P); b.append(struct.pack('<6f',*lo,*sc)); b.append(q.tobytes())
            b.append(np.clip(np.round(N*127),-127,127).astype('i1').tobytes())
            lo,sc,q=q16(U); b.append(struct.pack('<4f',*lo,*sc)); b.append(q.tobytes())
            b.append(struct.pack('<i',I.size)); b.append(I.astype('<u2').tobytes())
    open(p,'wb').write(b''.join(b)); print(p,'->BRK2',os.path.getsize(p))
