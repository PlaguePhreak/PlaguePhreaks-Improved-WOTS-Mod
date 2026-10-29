# Python copy of ModWreckArt 0.29.4 (blast by load, water tower) with a crude splat renderer, for a preview.
import numpy as np, math, random, sys
from PIL import Image as I
mode=sys.argv[1]; T=float(sys.argv[2]); out=sys.argv[3]
R=float(sys.argv[4]) if len(sys.argv)>4 else 16; pops=int(sys.argv[5]) if len(sys.argv)>5 else 0; flares=int(sys.argv[6]) if len(sys.argv)>6 else 0
random.seed(5); np.random.seed(5)
PuffLife=9.0; BlastMin=2.5; Big=9
def rr(a,b): return random.uniform(a,b)
def lerp(a,b,t): return a+(b-a)*t
def onsphere():
    v=np.random.normal(size=3); return v/np.linalg.norm(v)
P=[]
def emit(s,t,p,v,size,life,col,g=0.0): P.append((s,t,np.array(p,float),np.array(v,float),size,life,np.array(col,float),g))
heads=[]
def head(az,el,reach,drag,g,RR,flare=False,wreck=False):
    az,el=math.radians(az),math.radians(el)
    d=np.array([math.cos(el)*math.sin(az), math.sin(el), math.cos(el)*math.cos(az)])
    return dict(p=d*RR*0.12, v=d*reach*drag*1.05, drag=drag,g=g,reach=reach,dist=0.,next=0.,age=0.,wreck=wreck,flare=flare)
if mode=='blast':
    pw=math.sqrt(max(0,min(1,(R-BlastMin)/(16-BlastMin)))); big=R>=Big
    cloudTime=6 if big else 6*0.35*pw; lifeK=lerp(0.3,1,pw)
    burstAt=lerp(0.15,0.5,pw); smokeAt=burstAt+lerp(0.8,2.0,pw); grow=0.8
    ns=3 if big else (1 if pw>0.8 else 0); nw=3 if big else 0
    for i in range(5):
        p=np.random.uniform(-1,1,3)*R*0.05; p[1]=abs(p[1])+R*0.02; emit('g',0,p,(0,R*0.04,0),R*rr(0.12,0.25),rr(0.3,0.6)+burstAt,(1,.9,.7,1))
    for i in range(8):
        d=onsphere(); d[1]=abs(d[1])*0.9+0.1; emit('b',0,d*R*0.03,d*R*rr(0.04,0.1),R*rr(0.06,0.1),rr(2,3),(1,.95,.9,1))
    for i in range(8):
        d=onsphere(); d[1]=abs(d[1])+0.3; emit('s',0,d*R*0.04,d*R*rr(0.05,0.12),R*rr(0.05,0.09),rr(1.5,2.5),(.95,.95,.95,.8))
    dark=0.16 if big else lerp(0.5,0.22,pw)
    t=0.; dt=1/30.; cloud=0.; fire=0.; gacc=0.; burst=False; smoked=False; ft=lerp(0.8,3.5,pw)
    while t<T:
        t+=dt; tb=t-burstAt
        if not burst and t>=burstAt:
            burst=True
            for i in range(round(lerp(4,16,pw))):
                p=np.random.uniform(-1,1,3)*R*0.15; p[1]=abs(p[1])+R*0.05; emit('g',t,p,(0,0,0),R*rr(0.5,0.9),rr(0.6,1.5)*lerp(0.4,1,pw),(1,.85,.6,1))
            for i in range(ns): heads.append(head(rr(0,360),lerp(15,80,random.random()**1.2),R*0.35*rr(0.7,1.3),rr(1.1,1.5),R*rr(0.08,0.15),R))
            for i in range(nw): heads.append(head(rr(0,360),rr(25,65),R*rr(1.1,1.7),rr(0.8,1.1),R*0.3,R,wreck=True))
            for i in range(round(50*lerp(0.1,1,pw))):
                d=onsphere(); d[1]=abs(d[1])*0.9+0.15; emit('c',t,d*R*0.08,d/np.linalg.norm(d)*R*rr(0.3,1),max(0.06,R*rr(0.008,0.03)),rr(3,6),(0.12,0.115,0.11,1),0.5*R)
            for i in range(round(100*lerp(0.15,1,pw))):
                d=onsphere(); d[1]=abs(d[1])*0.9+0.1; d/=np.linalg.norm(d); emit('k',t,d*R*0.03,d*R*rr(0.4,1.3),max(0.04,R*rr(0.006,0.012)),rr(1,2.6),(1,.9,.7,1),0.35*R)
            for i in range(round(40*pw)):
                d=onsphere(); d[1]=abs(d[1])*0.9+0.25; d/=np.linalg.norm(d); emit('k',t,d*R*0.1,d*R*rr(0.25,0.7),max(0.12,R*rr(0.018,0.03)),rr(2.5,4.5),(1,.95,.85,1),0.35*R)
        if burst and tb<grow:
            f=min(1,tb/grow); gacc+=dt/grow*140*lerp(0.12,1,pw)
            while gacc>=1:
                gacc-=1; d=onsphere(); d[1]=abs(d[1])*0.8+0.1; v=d*R*rr(0.2,0.42)*(1.2-0.6*f)+np.array([0,R*0.05,0]); w=rr(0.85,1)
                emit('b',t,d*R*lerp(0.04,0.22,f)*rr(0.6,1.1),v,R*lerp(0.28,0.45,f)*rr(0.8,1.1),PuffLife*lifeK*rr(1.2,1.8),(1,w,w,1))
        if not smoked and t>=smokeAt:
            smoked=True
            for i in range(round(lerp(6,40,pw))):
                d=onsphere(); d[1]=abs(d[1])*0.5+0.1; g=rr(0.45,0.65); emit('s',t,d*R*rr(0.2,0.32),d*R*rr(0.05,0.1),R*rr(0.2,0.32),PuffLife*lifeK*rr(1.2,1.7),(g,g*.97,g*.93,1))
            for i in range(round(lerp(8,30,pw))):
                a=rr(0,6.2832); d=np.array([math.cos(a),0,math.sin(a)]); g=rr(0.55,0.7); emit('s',t,d*R*0.2+np.array([0,R*0.03,0]),d*R*rr(0.06,0.12),R*rr(0.15,0.25),PuffLife*lifeK*rr(0.8,1.1),(g,g*.97,g*.95,1))
        if burst and grow*0.6<=tb<cloudTime+grow*0.6:
            cloud+=dt*24*lerp(0.3,1,pw)
            while cloud>=1:
                cloud-=1; p=onsphere()*R*0.2*random.random()**(1/3); p[0]*=1.8; p[2]*=1.8; p[1]=abs(p[1])*0.7+R*(0.08+0.05*tb)
                hot=max(0,min(1,1-tb/2.5)); k=lerp(0.55,1,hot)
                emit('b',t,p,(p[0]*0.25,R*rr(0.08,0.16),p[2]*0.25),R*rr(0.25,0.4),PuffLife*lifeK*rr(1.5,2.1),(k,k,k,1))
        if burst and tb<ft:
            fire+=dt*22*lerp(0.4,1,pw)
            while fire>=1:
                fire-=1; p=onsphere()*R*0.25*random.random()**(1/3); p[1]=abs(p[1])*0.8+R*0.03
                emit('g',t,p,(p[0]*0.4,R*0.06,p[2]*0.4),R*rr(0.15,0.35),rr(0.4,0.8),(1,0.78,0.4,1-tb/ft))
        for h in list(heads):
            left=dt; dead=False
            while left>0 and not dead:
                s_=min(left,0.04); left-=s_; h['age']+=s_; p0=h['p'].copy()
                h['v']=h['v']*math.exp(-h['drag']*s_); h['v'][1]-=h['g']*s_; h['p']=h['p']+h['v']*s_
                step=np.linalg.norm(h['p']-p0); sp=R*0.042
                while h['dist']+step>=h['next']:
                    k=(h['next']-h['dist'])/step if step>1e-4 else 1; at=p0+(h['p']-p0)*min(1,max(0,k))
                    f=min(1,h['dist']/max(0.01,h['reach'])); drift=h['v']*0.06+np.array([0,R*0.012,0])
                    if h['wreck']:
                        g=rr(0.38,0.5); emit('s',t,at,drift,R*rr(0.016,0.024),PuffLife*rr(0.6,0.9),(g,g*.96,g*.93,1))
                    else:
                        size=R*lerp(0.045,0.022,f)*rr(0.7,1.3); heat=max(0,min(1,1-h['age']/3))
                        c=lerp(np.array([0.28,0.27,0.26,1]),np.array([0.75,0.6,0.42,1]),heat*rr(0.6,1)); emit('s',t,at,drift,size,PuffLife*rr(0.7,1.15)*(1-0.35*f),c)
                        if heat>0.05: emit('g',t,at,h['v']*0.2,size*1.4,0.45,(1,0.78,0.4,heat))
                    h['next']+=sp
                h['dist']+=step
                if h['p'][1]<0 or h['dist']>=h['reach'] or h['age']>4 or np.linalg.norm(h['v'])<h['reach']*0.06: dead=True
            if dead: heads[:]=[x for x in heads if x is not h]
    balldark=dark
else:
    H=R; g=1.2; v0=math.sqrt(2*g*H); up=v0/g; balldark=0
    for k in range(220):
        th=math.radians(rr(0,35)); az=rr(0,6.283); d=np.array([math.sin(th)*math.cos(az),math.cos(th),math.sin(th)*math.sin(az)])
        vel=d*v0*rr(0.6,1.25); life=2*max(0.3,vel[1])/g*rr(0.85,1)
        emit('w',0,np.random.uniform(-1,1,3)*H*0.05,vel,H*rr(0.006,0.012),life,(1,1,1,0.9),g)
    for k in range(40):
        a=rr(0,6.283); d=np.array([math.cos(a),0,math.sin(a)]); emit('m',0,d*H*0.1+np.array([0,H*0.03,0]),d*H*rr(0.12,0.25),H*rr(0.1,0.16),rr(5,8),(1,1,1,1))
    t=0.; dt=1/30.; col=0.; mist=0.
    while t<T:
        t+=dt
        if t<0.4:
            col+=dt/0.4*170
            while col>=1:
                col-=1; a=rr(0,6.283); r=H*0.07*math.sqrt(random.random()); disc=np.array([r*math.cos(a),r*math.sin(a)])
                p=np.array([disc[0],rr(0,H*0.05),disc[1]]); vy=v0*lerp(0.45,1,math.sqrt(random.random()))
                vel=np.array([disc[0]*0.6+rr(-.08,.08)*v0,vy,disc[1]*0.6+rr(-.08,.08)*v0]); emit('W',t,p,vel,H*rr(0.08,0.13),2*vy/g*rr(0.9,1),(1,1,1,1),g)
        if up*0.7<t<up*1.8:
            mist+=dt*45
            while mist>=1:
                mist-=1; a=rr(0,6.283); r=H*0.22*math.sqrt(random.random())
                emit('m',t,(r*math.cos(a),H*rr(0.15,0.85),r*math.sin(a)),(H*0.03,-H*0.02,0),H*rr(0.18,0.3),rr(8,12),(1,1,1,1))
# render (same camera for every picture so sizes compare: a full destroyer magazine fills it)
W,Hh=960,600; img=np.zeros((Hh,W,3)); sky=np.linspace(0,1,Hh)[:,None,None]; img[:]=np.array([0.42,0.6,0.85])*(1-sky*0.3)
hor=int(Hh*0.66); img[hor:]=np.array([0.1,0.2,0.3])
cam=np.array([0,1.0,-48.0]); fpx=W/2/math.tan(math.radians(55/2))
items=[]
for s,tb,p,v,size,life,col,gr in P:
    age=t-tb
    if age<0 or age>life: continue
    a=age/life; pos=p+v*age+np.array([0,-0.5*gr*age*age,0])
    if s=='b':
        sz=size*np.interp(a,[0,0.15,1],[0.5,1,1.6]); d=balldark
        cm=np.array([np.interp(a,[0,.12,.26,1],[1,.95,d,.45]),np.interp(a,[0,.12,.26,1],[.85,.6,d*.97,.45]),np.interp(a,[0,.12,.26,1],[.5,.3,d*.94,.45])]); al=np.interp(a,[0,0.02,0.6,1],[0,1,0.9,0])
    elif s=='s': sz=size*np.interp(a,[0,0.12,1],[0.45,1,1.9]); cm=np.array([np.interp(a,[0,0.3,1],[1,.85,.75])]*3); al=np.interp(a,[0,0.03,0.5,1],[0,1,0.85,0])
    elif s=='W': sz=size*np.interp(a,[0,0.4,1],[0.6,1.2,2.2]); cm=np.ones(3)*np.interp(a,[0,1],[1,.9]); al=np.interp(a,[0,0.04,0.7,1],[0,1,0.85,0])
    elif s=='w': sz=size; cm=np.ones(3); al=np.interp(a,[0,0.7,1],[0.9,0.7,0])
    elif s=='m': sz=size*np.interp(a,[0,0.2,1],[0.5,1,2]); cm=np.ones(3)*0.95; al=np.interp(a,[0,0.1,0.6,1],[0,0.6,0.4,0])
    elif s=='c': sz=size; cm=np.ones(3); al=1
    else:
        sz=size*(np.interp(a,[0,1],[1,0.35]) if s=='g' else 1)
        cm=np.array([1,np.interp(a,[0,.4,1],[1,.6,.15]),np.interp(a,[0,.4,1],[1,.3,.05])]) if s=='g' else np.array([1,np.interp(a,[0,1],[1,.45]),np.interp(a,[0,1],[1,.15])])
        al=np.interp(a,[0,1],[1,0]) if s=='g' else np.interp(a,[0,.6,1],[1,1,0])
    q=pos-cam
    if q[2]<=0.1 or pos[1]<-0.3: continue
    items.append((np.linalg.norm(q),s,(W/2+q[0]/q[2]*fpx,hor-(pos[1])/q[2]*fpx,fpx/q[2]),sz,col[:3]*cm,col[3]*al))
items.sort(key=lambda x:-x[0])
pt=I.open('/tmp/claude-0/puff/puff.png'); yy,xx=np.mgrid[0:64,0:64]; glow=np.clip(1-np.hypot(xx-31.5,yy-31.5)/32,0,1)**2
for d,s,(x,y,sc),sz,c,al in items:
    rpx=max(1,int(sz*sc/2)) if s not in 'kw' else max(1,int(sz*sc*1.5))
    x0,y0=int(x-rpx),int(y-rpx); n=2*rpx
    if x0>=W or y0>=Hh or x0+n<0 or y0+n<0 or n>2000: continue
    if s in 'cw': rgb=np.ones((n,n,3))*c; a=np.ones((n,n))*al
    elif s in 'sbWm': tex=np.array(pt.resize((n,n)))/255.; rgb=tex[...,:3]*c; a=tex[...,3]*al
    else: gg=np.array(I.fromarray((glow*255).astype('uint8')).resize((n,n)))/255.; rgb=gg[...,None]*c; a=gg*al
    xa,ya=max(0,x0),max(0,y0); xb,yb=min(W,x0+n),min(Hh,y0+n); sub=(slice(ya-y0,yb-y0),slice(xa-x0,xb-x0)); dst=img[ya:yb,xa:xb]
    if s in 'sbcWmw': dst[:]=dst*(1-a[sub][...,None])+rgb[sub]*a[sub][...,None]
    else: dst[:]=np.minimum(1,dst+rgb[sub]*a[sub][...,None])
img[hor+2:]=np.array([0.1,0.2,0.3])
I.fromarray((np.clip(img,0,1)*255).astype('uint8')).save(out); print(out,len(P))
