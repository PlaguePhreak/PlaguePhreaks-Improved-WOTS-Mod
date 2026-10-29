cd /tmp/claude-0/simcs
python3 - <<'P'
s=open('/tmp/claude-0/b9/MS4.cs').read()
def grab(sig):
    a=s.index(sig); a=s.rindex('\n',0,a)+1
    i=s.index('{',a); d=0
    while True:
        if s[i]=='{': d+=1
        elif s[i]=='}':
            d-=1
            if d==0: break
        i+=1
    return s[a:i+1]
parts=[grab('private class Piece'),grab('private static void MakeSplitPiece'),grab('private static void BuildCells'),grab('private static void Fracs'),grab('private static void Flow'),grab('private static bool Step('),grab('private static void TickPiece')]
body='\n\n'.join(parts).replace('private class','public class').replace('private static','public static')
for n in ['test','pose']:
    t=open(n+'.cs').read().replace('//BODY',body); open(n+'_full.cs','w').write(t)
P
D=$(ls -d /usr/lib/dotnet/shared/Microsoft.NETCore.App/8.*|head -1); refs=""; for f in System.Runtime System.Console System.Private.CoreLib System.Collections netstandard System.Runtime.Extensions; do [ -f $D/$f.dll ] && refs="$refs -r:$D/$f.dll"; done
for n in t:test pose:pose; do dotnet /usr/lib/dotnet/sdk/8.0.132/Roslyn/bincore/csc.dll -nologo -nostdlib -noconfig -langversion:7.3 -t:exe -out:${n%%:*}.dll $refs shim.cs ${n##*:}_full.cs 2>&1 | grep error; done
