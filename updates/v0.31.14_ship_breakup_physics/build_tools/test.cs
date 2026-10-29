using System; using System.Collections.Generic; using UnityEngine;
public class UnitData{public float baseLevel; public Vector3 dimensions;}
public class Unit{public UnitData unitData;}
public static class ModSinking {
 public static Transform root=new Transform();
 public static float HogAngle=4.5f, Gravity=0.981f, Porosity=0.85f, SeaLevel=0f, FSK=0.3f, GMk=0.08f, FreeboardK=1.4f, RunK=0.3f, SeedWater=0.6f, BlastKick=1f, PhysStep=0.05f, DampPitch=0.6f, DampYaw=0.4f, DampRoll=0.35f;
 public static int CellsAlong=12;
 public class Wreck{public Unit u; public float scale=1, L; public float floorY=-1000; public string name="t";}
 static float Rnd(float a){return UnityEngine.Random.Range(-a,a);}
 static void Fx(string a,Vector3 b,float c,float d){Console.WriteLine("  SPLASH at "+b);} static void Pooled(string a,Vector3 b){} static void Log(string s){Console.WriteLine("  LOG "+s);} static void DestroyPiece(Piece p){}
//BODY
 static void Report(string tag,Piece pc,float t){ Vector3 f=pc.rot*Vector3.forward, r=pc.rot*Vector3.right, upv=pc.rot*Vector3.up;
  float pitch=(float)(Math.Asin(-f.y)*57.3); float roll=(float)(Math.Atan2(-r.y,upv.y)*57.3); float W=0,cap=0; for(int i=0;i<pc.vol.Length;i++){W+=pc.water[i];cap+=pc.vol[i]*Porosity;}
  Console.WriteLine(string.Format("{0} t={1,5:F0} cgY={2,6:F2} pitch={3,6:F1} roll={4,6:F1} fill={5:F2} vel={6} done={7}",tag,t,(root.position+pc.rel).y,pitch,roll,W/cap,pc.vel,pc.done)); }
 public static void Main(string[] a){
  // destroyer: 110 m (11 units), beam 1.1, draft 0.4, height 1.0
  float L=11f; var ud=new UnitData{baseLevel=-0.4f,dimensions=new Vector3(1.1f,1f,L)};
  foreach(string mode in new[]{"break","magsplit"}) foreach(float sig in new[]{1f,-1f}){
   var w=new Wreck{u=new Unit{unitData=ud},L=L};
   var pc=new Piece(); pc.tr=new Transform(); pc.isUnit=sig<0;
   MakeSplitPiece(w,pc,0.5f,sig,L,90f,mode,sig>0);
   Console.WriteLine("== "+mode+" sigma "+sig+" mass "+pc.mass+" cg "+pc.cg+" vel "+pc.vel+" spin "+pc.spin);
   float t=0,nx=0; while(t<400&&!pc.done){TickPiece(w,pc,0.1f);t+=0.1f; if(t>=nx){Report(mode,pc,t);nx+= t<10?1:20;}} Report("end",pc,t);
  }
  // whole ship with one side holed (capsize-like), and one end holed (plunge-like), and shallow seabed
  foreach(string kind in new[]{"side","end","even","shallow"}){
   var w=new Wreck{u=new Unit{unitData=ud},L=L}; if(kind=="shallow") w.floorY=-4f;
   var pc=new Piece(); pc.tr=new Transform(); pc.isUnit=true; pc.sigma=0; pc.lenFrac=1;
   BuildCells(w,pc,-L/2,L/2,L); float S=300; pc.dur=S; pc.tauOpen=0.25f*S; pc.tauSeep=1.2f*S; pc.tauLeak=0.3f*S; pc.tauAcross=0.05f*S; pc.tauDown=0.02f*S;
   for(int i=0;i<pc.vol.Length;i++){int k=i/8; bool port=((i%8)/2)<2; float zf=(k+0.5f)/pc.n; float op=0.15f;
    if(kind=="side"&&port) op=1f; if((kind=="end"||kind=="shallow")&&zf>0.6f) op=1f; if(kind=="even") op=0.45f; pc.open[i]=op;}
   Console.WriteLine("== whole "+kind+" mass "+pc.mass+" cg "+pc.cg+" I "+pc.inertia);
   float t=0,nx=0; while(t<2000&&!pc.done){TickPiece(w,pc,0.25f);t+=0.25f; if(t>=nx){Report(kind,pc,t);nx+=60;}} Report("end",pc,t);
  }
 }
}
