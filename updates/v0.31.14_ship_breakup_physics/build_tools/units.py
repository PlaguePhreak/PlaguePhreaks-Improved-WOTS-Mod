import os
old=[l.split() for l in open('/mnt/project-files/v0.29_mega/mod_wreck/units.txt') if len(l.split())>=2]
m={a:b for a,b,*_ in old}
B='/tmp/claude-0/kits/brk'
done=[n for n in sorted(os.listdir(B)) if all(os.path.exists(f'{B}/{n}/{n}_{t}.brk') for t in ('fore','mid','aft'))]
for n in done: m.setdefault(n,n)
for a,b in [('kamikawa_maru','kamogawa_maru'),('kuma','nagara'),('taiyo','zuiho')]:
    if b in done: m[a]=b
    else: print('MISSING model',b)
open('/tmp/claude-0/kits/units.txt','w').write(''.join(f'{a} {b}\n' for a,b in sorted(m.items())))
print(len(old),'old',len(done),'new kits',len(m),'units')
