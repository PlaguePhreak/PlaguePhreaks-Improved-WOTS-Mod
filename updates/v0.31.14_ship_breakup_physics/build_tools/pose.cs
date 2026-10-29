using System; using System.Collections.Generic; using UnityEngine; using System.Text;
public class UnitData{public float baseLevel; public Vector3 dimensions;}
public class Unit{public UnitData unitData;}
public static class ModSinking {
 public static Transform root=new Transform();
 public static float HogAngle=4.5f, Gravity=0.981f, Porosity=0.85f, SeaLevel=0f, FSK=0.3f, GMk=0.08f, FreeboardK=1.4f, RunK=0.3f, SeedWater=0.6f, BlastKick=1f, PhysStep=0.05f, DampPitch=0.6f, DampYaw=0.4f, DampRoll=0.35f;
 public static int CellsAlong=12;
 public class Wreck{public Unit u; public float scale=1, L; public float floorY=-1000; public string name="t";}
 static float Rnd(float a){return UnityEngine.Random.Range(-a,a);}
 static void Fx(string a,Vector3 b,float c,float d){} static void Pooled(string a,Vector3 b){} static void Log(string s){} static void DestroyPiece(Piece p){}
//BODY
 static string Pose(Piece pc){ Vector3 o=root.position+pc.rel-pc.rot*(pc.cg); Vector3 ax=pc.rot*Vector3.right, ay=pc.rot*Vector3.up, az=pc.rot*Vector3.forward;
  return string.Format(System.Globalization.CultureInfo.InvariantCulture,"[{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}]",o.x,o.y,o.z,ax.x,ax.y,ax.z,ay.x,ay.y,ay.z,az.x,az.y,az.z); }
 public static void Main(string[] a){
  // a: L beam draft cut baseTime mode floor times...
  var ci=System.Globalization.CultureInfo.InvariantCulture;
  float L=float.Parse(a[0],ci), B=float.Parse(a[1],ci), T=float.Parse(a[2],ci), cut=float.Parse(a[3],ci), bt=float.Parse(a[4],ci); string mode=a[5]; float floor=float.Parse(a[6],ci);
  var times=new List<float>(); for(int i=7;i<a.Length;i++) times.Add(float.Parse(a[i],ci));
  var ud=new UnitData{baseLevel=-T,dimensions=new Vector3(B,1f,L)};
  var w=new Wreck{u=new Unit{unitData=ud},L=L,floorY=floor};
  float half=L/2; bool detachFore=(half-cut)<=(cut+half);
  var pu=new Piece(); pu.tr=new Transform(); pu.isUnit=true; MakeSplitPiece(w,pu,cut,detachFore?-1f:1f,L,bt,mode,false);
  var pcl=new Piece(); pcl.tr=new Transform(); MakeSplitPiece(w,pcl,cut,detachFore?1f:-1f,L,bt,mode,true);
  var sb=new StringBuilder("["); float t=0; int ti=0; float dt=0.1f;
  while(ti<times.Count){ if(t>=times[ti]-1e-4){ sb.Append((ti>0?",":"")+"{\"t\":"+t.ToString("F1",ci)+",\"unit\":"+Pose(pu)+",\"clone\":"+Pose(pcl)+",\"ud\":"+(pu.done?1:0)+",\"cd\":"+(pcl.done?1:0)+",\"sigU\":"+pu.sigma.ToString(ci)+"}"); ti++; continue;}
   if(!pu.done) TickPiece(w,pu,dt); if(!pcl.done) TickPiece(w,pcl,dt); t+=dt; }
  Console.WriteLine(sb.Append("]").ToString());
 }
}
