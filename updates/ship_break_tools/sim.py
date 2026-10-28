# Python copy of ModWreckArt's 3D blast (Tick/Puff/Bang) with a crude splat renderer, for a preview.
import numpy as np, math, random, sys
from PIL import Image
random.seed(3); np.random.seed(3)
R=16.5; PuffLife=9.0; Streamers=48; Wreck=14; Sparks=90; light=1.0
puff=np.array(Image.open('/tmp/claude-0/puff/puff.png')).astype(float)/255
def rr(a,b): return random.uniform(a,b)
def onsphere():
    v=np.random.normal(size=3); return v/np.linalg.norm(v)
P=[]  # particles: sys, born, pos, vel, size, life, col
def emit(s,t,p,v,size,life,col): P.append((s,t,np.array(p,float),np.array(v,float),size,life,np.array(col,float)))
def head(az,el,reach,drag,g):
    az,el=math.radians(az),math.radians(el)
    d=np.array([math.cos(el)*math.sin(az), math.sin(el), math.cos(el)*math.cos(az)])
    return dict(p=d*R*0.04, v=d*reach*drag*1.05, drag=drag,g=g,reach=reach,dist=0.,next=0.,age=0.,wreck=False)
heads=[]
for i in range(Streamers):
    heads.append(head(rr(0,360), 3+77*random.random()**1.4, R*rr(0.6,1.2), rr(1.1,1.5), R*rr(0.08,0.15)))
for i in range(Wreck):
    h=head(rr(0,360), rr(10,60), R*rr(1.1,1.7), rr(0.8,1.1), R*0.3); h['wreck']=True; heads.append(h)
def lerp(a,b,t): return a+(b-a)*t
def Puff(h,at,t):
    f=min(1,h['dist']/max(0.01,h['reach'])); drift=h['v']*0.06+np.array([0,R*0.012,0])
    if h['wreck']:
        g=rr(0.38,0.5); emit('s',t,at,drift,R*rr(0.016,0.024),PuffLife*rr(0.6,0.9),(g,g*.96,g*.93,1)); return
    size=R*lerp(0.06,0.03,f)*rr(0.7,1.3); heat=max(0,min(1,1-h['age']/3))
    c=lerp(np.array([0.38,0.27,0.22,1])*np.array([light,light,light,1]), np.array([0.85,0.38,0.2,1]), heat*rr(0.75,1))
    emit('s',t,at,drift,size,PuffLife*rr(0.7,1.15)*(1-0.35*f),c)
    if heat>0.05: emit('g',t,at,h['v']*0.2,size*0.9,0.45,(1,0.62,0.3,heat))
# bang
for i in range(10):
    p=np.random.uniform(-1,1,3)*R*0.08; p[1]=abs(p[1]); emit('g',0,p,(0,0,0),R*rr(0.25,0.4),rr(0.5,1.1),(1,.85,.6,1))
for i in range(45):
    d=onsphere(); d[1]=abs(d[1])*0.8+0.1; emit('s',0,d*R*rr(0.02,0.12),d*R*rr(0.03,0.08),R*rr(0.12,0.2),PuffLife*rr(0.8,1.2),(1,rr(0.55,0.7),0.3,1))
for i in range(Sparks):
    d=onsphere(); d[1]=abs(d[1])*0.9+0.1; d/=np.linalg.norm(d); emit('k',0,d*R*0.03,d*R*rr(0.4,1.3),R*rr(0.006,0.012),rr(1,2.6),(1,.9,.7,1))
T=float(sys.argv[1]) if len(sys.argv)>1 else 2.0
t=0.; dt=1/30.; cloud=0.
while t<T:
    t+=dt
    if t<4:
        cloud+=dt*14
        while cloud>=1:
            cloud-=1; p=np.random.uniform(-1,1,3)*R*0.12; p[1]=abs(p[1])+R*0.05
            col=(1,0.55,0.28,1) if t<1.2 else (0.42,0.33,0.28,1)
            emit('s',t,p,(p[0]*0.3,R*rr(0.05,0.11),p[2]*0.3),R*rr(0.14,0.22),PuffLife*rr(1,1.4),col)
    for h in list(heads):
        hid=id(h)
        left=dt; dead=False
        while left>0 and not dead:
            s=min(left,0.04); left-=s; h['age']+=s; p0=h['p'].copy()
            h['v']=h['v']*math.exp(-h['drag']*s); h['v'][1]-=h['g']*s; h['p']=h['p']+h['v']*s
            step=np.linalg.norm(h['p']-p0); sp=R*(0.045 if h['wreck'] else 0.042)
            while h['dist']+step>=h['next']:
                k=(h['next']-h['dist'])/step if step>1e-4 else 1
                Puff(h,p0+(h['p']-p0)*min(1,max(0,k)),t); h['next']+=sp
            h['dist']+=step
            if h['p'][1]<0 or h['dist']>=h['reach'] or h['age']>4 or np.linalg.norm(h['v'])<h['reach']*0.06: dead=True
        if dead: heads[:]=[x for x in heads if id(x)!=hid]
# render: camera at distance D, height H, looking at (0, R*0.3, 0), perspective
W,Hh=1280,720; img=np.zeros((Hh,W,3)); 
sky=np.linspace(0,1,Hh)[:,None,None]; img[:]=np.array([0.42,0.6,0.85])*(1-sky*0.3)+0
hor=int(Hh*0.62); img[hor:]=np.array([0.1,0.2,0.3])
cam=np.array([0,R*0.06,-R*2.3]); fov=55; fpx=W/2/math.tan(math.radians(fov/2))
def proj(p):
    q=p-cam; 
    if q[2]<=0.1: return None
    return W/2+q[0]/q[2]*fpx, hor-q[1]/q[2]*fpx+ (cam[1]/q[2]*fpx)*0, fpx/q[2]
items=[]
for s,tb,p,v,size,life,col in P:
    age=t-tb
    if age<0 or age>life: continue
    a=age/life; pos=p+v*age
    if s=='k': pos=pos+np.array([0,-0.5*0.35*R*age*age,0])
    if s=='s':
        sz=size*np.interp(a,[0,0.12,1],[0.45,1,1.9])
        cm=np.array([np.interp(a,[0,0.25,1],[1,0.62,0.42]),np.interp(a,[0,0.25,1],[1,0.5,0.38]),np.interp(a,[0,0.25,1],[1,0.45,0.36])])
        al=np.interp(a,[0,0.03,0.5,1],[0,1,0.85,0])
    else:
        sz=size*(np.interp(a,[0,1],[1,0.35]) if s=='g' else 1)
        cm=np.array([1,np.interp(a,[0,.4,1],[1,.6,.15]),np.interp(a,[0,.4,1],[1,.3,.05])]) if s=='g' else np.array([1,np.interp(a,[0,1],[1,.45]),np.interp(a,[0,1],[1,.15])])
        al=np.interp(a,[0,1],[1,0]) if s=='g' else np.interp(a,[0,.6,1],[1,1,0])
    pr=proj(pos)
    if pr is None or pos[1]<-0.5: continue
    items.append((np.linalg.norm(pos-cam),s,pr,sz,col[:3]*cm,col[3]*al))
items.sort(key=lambda x:-x[0])
from PIL import Image as I
pt=I.open('/tmp/claude-0/puff/puff.png')
glow=np.zeros((64,64)); yy,xx=np.mgrid[0:64,0:64]; glow=np.clip(1-np.hypot(xx-31.5,yy-31.5)/32,0,1)**2
for d,s,(x,y,sc),sz,c,al in items:
    rpx=max(1,int(sz*sc/2)) if s!='k' else max(1,int(sz*sc*1.5))
    x0,y0=int(x-rpx),int(y-rpx); n=2*rpx
    if x0>=W or y0>=Hh or x0+n<0 or y0+n<0 or n>2000: continue
    if s=='s': tex=np.array(pt.resize((n,n)))/255.; rgb=tex[...,:3]*c; a=tex[...,3]*al
    else: g=np.array(I.fromarray((glow*255).astype('uint8')).resize((n,n)))/255.; rgb=g[...,None]*c; a=g*al
    xa,ya=max(0,x0),max(0,y0); xb,yb=min(W,x0+n),min(Hh,y0+n)
    sub=(slice(ya-y0,yb-y0),slice(xa-x0,xb-x0)); dst=img[ya:yb,xa:xb]
    if s=='s': dst[:]=dst*(1-a[sub][...,None])+rgb[sub]*a[sub][...,None]
    else: dst[:]=np.minimum(1,dst+rgb[sub]*a[sub][...,None])
img[hor:]=np.where(img[hor:]>0, img[hor:], img[hor:]); img[hor+2:]=np.array([0.1,0.2,0.3])*1.0  # sea hides below
I.fromarray((np.clip(img,0,1)*255).astype('uint8')).save('/tmp/claude-0/puff/sim_%.1f.png'%T)
print(len(P),'particles')
