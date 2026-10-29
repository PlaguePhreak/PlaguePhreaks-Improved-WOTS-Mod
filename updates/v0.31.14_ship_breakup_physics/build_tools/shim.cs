using System;
namespace UnityEngine {
public struct Vector3 { public float x,y,z; public Vector3(float a,float b,float c){x=a;y=b;z=c;}
 public static Vector3 zero{get{return new Vector3(0,0,0);}} public static Vector3 up{get{return new Vector3(0,1,0);}} public static Vector3 forward{get{return new Vector3(0,0,1);}} public static Vector3 right{get{return new Vector3(1,0,0);}}
 public static Vector3 operator+(Vector3 a,Vector3 b){return new Vector3(a.x+b.x,a.y+b.y,a.z+b.z);} public static Vector3 operator-(Vector3 a,Vector3 b){return new Vector3(a.x-b.x,a.y-b.y,a.z-b.z);} public static Vector3 operator-(Vector3 a){return new Vector3(-a.x,-a.y,-a.z);}
 public static Vector3 operator*(Vector3 a,float f){return new Vector3(a.x*f,a.y*f,a.z*f);} public static Vector3 operator*(float f,Vector3 a){return a*f;} public static Vector3 operator/(Vector3 a,float f){return new Vector3(a.x/f,a.y/f,a.z/f);}
 public float magnitude{get{return (float)Math.Sqrt(x*x+y*y+z*z);}} public Vector3 normalized{get{float m=magnitude;return m>1e-9f?this/m:zero;}}
 public static Vector3 Cross(Vector3 a,Vector3 b){return new Vector3(a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x);} public static float Dot(Vector3 a,Vector3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
 public override string ToString(){return string.Format("({0:F2},{1:F2},{2:F2})",x,y,z);} }
public struct Quaternion { public float x,y,z,w; public Quaternion(float a,float b,float c,float d){x=a;y=b;z=c;w=d;}
 public static Quaternion identity{get{return new Quaternion(0,0,0,1);}}
 public static Quaternion operator*(Quaternion a,Quaternion b){return new Quaternion(a.w*b.x+a.x*b.w+a.y*b.z-a.z*b.y,a.w*b.y+a.y*b.w+a.z*b.x-a.x*b.z,a.w*b.z+a.z*b.w+a.x*b.y-a.y*b.x,a.w*b.w-a.x*b.x-a.y*b.y-a.z*b.z);}
 public static Vector3 operator*(Quaternion q,Vector3 v){Vector3 u=new Vector3(q.x,q.y,q.z);Vector3 t=2f*Vector3.Cross(u,v);return v+q.w*t+Vector3.Cross(u,t);}
 public static Quaternion Inverse(Quaternion q){return new Quaternion(-q.x,-q.y,-q.z,q.w);}
 public static Quaternion AngleAxis(float deg,Vector3 a){a=a.normalized;float h=deg*Mathf.Deg2Rad/2;float s=(float)Math.Sin(h);return new Quaternion(a.x*s,a.y*s,a.z*s,(float)Math.Cos(h));}
 public static Quaternion Euler(float px,float py,float pz){return AngleAxis(py,Vector3.up)*AngleAxis(px,Vector3.right)*AngleAxis(pz,Vector3.forward);} }
public static class Mathf { public const float Deg2Rad=0.0174532924f, Rad2Deg=57.29578f;
 public static float Clamp(float v,float a,float b){return v<a?a:(v>b?b:v);} public static int Clamp(int v,int a,int b){return v<a?a:(v>b?b:v);} public static float Clamp01(float v){return Clamp(v,0,1);}
 public static float Min(float a,float b){return Math.Min(a,b);} public static float Max(float a,float b){return Math.Max(a,b);} public static float Abs(float a){return Math.Abs(a);} public static float Sqrt(float a){return (float)Math.Sqrt(a);} public static float Sin(float a){return (float)Math.Sin(a);}
 public static int RoundToInt(float a){return (int)Math.Round(a);} public static int CeilToInt(float a){return (int)Math.Ceiling(a);} public static int Max(int a,int b){return Math.Max(a,b);} }
public static class Random { static System.Random r=new System.Random(1); public static float value{get{return (float)r.NextDouble();}} public static float Range(float a,float b){return a+(b-a)*value;} }
public class Mesh{}
public class Transform { public Vector3 position; public Quaternion rotation=Quaternion.identity; public float s=1; public Vector3 TransformPoint(Vector3 p){return position+rotation*(p*s);} }
}
