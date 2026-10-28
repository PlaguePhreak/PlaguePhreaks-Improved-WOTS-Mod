# Textures for ship debris and oil slicks (Claude, 28 Oct 2026). python3 tex.py <out_dir>
# debris_atlas.png: 1024x1024, 4x4 tiles of 256 (tile index = row*4+col, row 0 at the TOP of the image)
# oil_slick_a/b/c.png: 512 RGBA, white-ish RGB (tinted in game), alpha = thickness; oil_sheen_*.png: rainbow edges
import sys, os, numpy as np
from PIL import Image
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
rng=np.random.default_rng(7)

def vnoise(n, cells, seed):
    r=np.random.default_rng(seed); g=r.random((cells+1,cells+1))
    g[-1,:]=g[0,:]; g[:,-1]=g[:,0]                # tiles
    x=np.linspace(0,cells,n,endpoint=False); i=x.astype(int); f=x-i; f=f*f*(3-2*f)
    a=g[i][:,i]; b=g[i][:,i+1]; c=g[i+1][:,i]; d=g[i+1][:,i+1]
    fx=f[None,:]; fy=f[:,None]
    return (a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy
def fbm(n, base, oct, seed, gain=0.5):
    s=np.zeros((n,n)); amp=1; tot=0
    for o in range(oct):
        s+=amp*vnoise(n, base*2**o, seed+o); tot+=amp; amp*=gain
    return s/tot
def col(c): return np.array(c,float)/255.

T=256
def wood(base, dark, seed, grain=40, burnt=0.):
    n=fbm(T,4,4,seed); y=np.arange(T)[:,None]*np.ones((1,T))
    rings=np.sin((y/T*grain+n*6)*np.pi)**8
    streak=fbm(T,32,2,seed+9)
    k=np.clip(0.55*rings+0.45*streak,0,1)[...,None]
    img=base*(1-k)+dark*k
    # plank seams every 64 px
    seam=((np.arange(T)%64)<2)[:,None]*np.ones((1,T)); img*=1-0.5*seam[...,None]
    if burnt:
        b=np.clip((fbm(T,3,4,seed+20)-0.5+burnt)*3,0,1)[...,None]
        img=img*(1-b)+col((22,18,15))*b
    return img
def paint(base, seed, wear=0.15, rust=0.1, soot=0.):
    n=fbm(T,6,5,seed); img=np.ones((T,T,3))*base*(0.9+0.2*n[...,None])
    w=np.clip((fbm(T,8,4,seed+3)-(1-wear))*6,0,1)[...,None]
    img=img*(1-w)+col((70,64,58))*w
    r=np.clip((fbm(T,5,5,seed+5)-(1-rust))*4,0,1)[...,None]
    img=img*(1-r)+col((105,52,28))*(0.7+0.5*fbm(T,40,2,seed+6))[...,None]*r
    if soot:
        s=np.clip((fbm(T,3,4,seed+8)-0.5+soot)*2.5,0,1)[...,None]
        img=img*(1-s)+col((25,23,22))*s
    return img
tiles=[None]*16
tiles[0]=wood(col((150,112,72)),col((96,66,40)),1)                  # deck plank wood (teak-ish, weathered)
tiles[1]=wood(col((120,88,58)),col((60,40,25)),2,burnt=0.05)        # burnt wood
tiles[2]=wood(col((176,146,100)),col((128,98,62)),3,grain=25)       # crate pine
tiles[3]=paint(col((112,118,124)),4)                                # navy grey (5-N)
tiles[4]=paint(col((96,100,104)),5,wear=0.25,rust=0.3,soot=0.0)     # scorched/rusty plate
tiles[5]=paint(col((60,66,52)),6,wear=0.2,rust=0.25)                # drum: dark olive
tiles[6]=paint(col((84,88,60)),7,wear=0.1,rust=0.05)                # ammo box olive drab
tiles[7]=paint(col((150,150,140)),8,wear=0.1,rust=0.02)             # carley float grey canvas
lr=np.ones((T,T,3))*col((225,222,210))*(0.9+0.1*fbm(T,6,4,9))[...,None]
band=(((np.arange(T)%64)>=40))[None,:]*np.ones((T,1)); lr=lr*(1-band[...,None])+col((190,40,30))*band[...,None]
tiles[8]=lr                                                         # life ring white/red (u = around)
tiles[9]=paint(col((150,128,88)),10,wear=0.05,rust=0)               # kapok canvas
tiles[10]=paint(col((78,82,86)),11,wear=0.2,rust=0.15)              # IJN dark grey
tiles[11]=np.ones((T,T,3))*col((22,20,18))*(0.7+0.6*fbm(T,10,4,12))[...,None]  # charred
tiles[12]=paint(col((110,62,36)),13,wear=0.3,rust=0.6)              # raw rust
tiles[13]=paint(col((120,40,32)),14,wear=0.15,rust=0.1)             # anti-fouling red
tiles[14]=paint(col((200,200,192)),15,wear=0.2,rust=0.1)            # boat white
tiles[15]=wood(col((170,150,110)),col((120,100,70)),16,grain=60)    # rope / light tan
atlas=np.zeros((1024,1024,3))
for i,t in enumerate(tiles):
    r,c=divmod(i,4); atlas[r*T:(r+1)*T,c*T:(c+1)*T]=t
Image.fromarray((np.clip(atlas,0,1)*255).astype(np.uint8)).save(os.path.join(out,'debris_atlas.png'))

# ---------- oil ----------
N=512
yy,xx=np.mgrid[0:N,0:N]; cx=(xx-N/2)/(N/2); cy=(yy-N/2)/(N/2)
def stretched(seed, base, oct, sx):
    f=fbm(N,base,oct,seed); w=max(8,int(N/sx))
    return np.array(Image.fromarray((f*255).astype(np.uint8)).crop((0,0,w,N)).resize((N,N),Image.BICUBIC))/255.
def smooth(e0,e1,x):
    t=np.clip((x-e0)/(e1-e0),0,1); return t*t*(3-2*t)
def slick(seed, stretch=1.0):
    # domain-warped distance: one main patch, ragged edge, long windrows along x (the drift)
    qx=fbm(N,2,4,seed)-0.5; qy=fbm(N,2,4,seed+1)-0.5
    d=np.sqrt(((cx+0.5*qx)/stretch)**2+(cy+0.5*qy)**2)
    edge=fbm(N,5,4,seed+2)-0.5
    dd=d+0.22*edge
    wind=stretched(seed+3,3,4,3.0)                        # streaks along x
    core=smooth(0.78,0.30,dd)                              # 1 inside, 0 outside
    rows=smooth(0.42,0.70,wind)*smooth(1.0,0.55,dd)       # windrows reaching out past the core
    holes=smooth(0.30,0.55,fbm(N,4,4,seed+4))              # patchy: open water inside the slick
    a=np.maximum(core*(0.35+0.65*holes), rows*0.55)
    a=np.clip(a,0,1)
    # RGB: white-ish (tinted in game); thick parts slightly browner (mousse), thin parts lighter
    thick=smooth(0.5,0.95,a)[...,None]
    rgb=np.ones((N,N,3))*(1-thick)+np.array([0.85,0.7,0.55])*thick
    rgb*=(0.85+0.15*fbm(N,16,3,seed+5))[...,None]
    # sheen only on the thin fringe, soft and low-frequency colours
    fr=smooth(0.04,0.18,a)*smooth(0.45,0.2,a)
    ph=fbm(N,3,3,seed+6)*2.2+a*1.5
    rb=np.stack([0.5+0.5*np.cos(2*np.pi*(ph+0.0)),0.5+0.5*np.cos(2*np.pi*(ph+0.33)),0.5+0.5*np.cos(2*np.pi*(ph+0.67))],-1)
    border=np.clip((1.0-np.maximum(abs(cx),abs(cy)))/0.1,0,1)
    rgba=np.dstack([rgb, a*border]); sh=np.dstack([rb, fr*0.45*border])
    return rgba, sh
for k,(s,st) in enumerate([(31,1.0),(47,1.3),(63,1.45)]):
    a,sh=slick(s,st); n='abc'[k]
    Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8),'RGBA').save(os.path.join(out,f'oil_slick_{n}.png'))
    Image.fromarray((np.clip(sh,0,1)*255).astype(np.uint8),'RGBA').save(os.path.join(out,f'oil_sheen_{n}.png'))
print('ok')
