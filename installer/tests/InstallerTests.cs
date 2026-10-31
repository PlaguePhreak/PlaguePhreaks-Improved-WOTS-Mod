using System; using System.IO; using System.Linq; using System.Collections.Generic; using WotsInstaller;
class Ui : IUi { public Queue<bool> answers = new Queue<bool>(); public List<string> asked = new List<string>();
  public void Log(string l){ Console.WriteLine("   | "+l); }
  public bool Ask(string t,string q){ asked.Add(t); var a = answers.Count>0 ? answers.Dequeue() : true; Console.WriteLine("   ? ASK ["+t+"] -> "+(a?"Yes":"No")); return a; }
  public void Tell(string t,string x){ Console.WriteLine("   ! TELL ["+t+"] "+x.Split('\n')[0]); } }
class P {
  static string R="/home/claude/inst/ref", M="/home/claude/inst/managed", G="/tmp/wt/War on the Sea", MF="/tmp/wt/Mod Files";
  static string Dll => G+"/WarOnTheSea_Data/Managed/Assembly-CSharp.dll";
  static string Ov => G+"/WarOnTheSea_Data/StreamingAssets/override";
  static string TreeHash(string d){ if(!Directory.Exists(d)) return "none"; var s=string.Join("\n", Directory.GetFiles(d,"*",SearchOption.AllDirectories).OrderBy(x=>x).Select(f=>f.Substring(d.Length)+":"+StockFp.FileMd5(f))); s += "|dirs:"+string.Join(",",Directory.GetDirectories(d,"*",SearchOption.AllDirectories).OrderBy(x=>x).Select(x=>x.Substring(d.Length))); return Fp.Hash(s); }
  static void Fresh(string gameDll){
    if (Directory.Exists("/tmp/wt")) Directory.Delete("/tmp/wt", true);
    Directory.CreateDirectory(G+"/WarOnTheSea_Data/Managed"); foreach(var f in Directory.GetFiles(M)) File.Copy(f, G+"/WarOnTheSea_Data/Managed/"+Path.GetFileName(f));
    File.Copy(gameDll, Dll);
    Directory.CreateDirectory(Ov+"/campaign"); File.WriteAllText(Ov+"/campaign/campaigns.txt","stock campaigns"); File.WriteAllText(Ov+"/keep.txt","player file"); File.WriteAllText(Ov+"/same.txt","identical");
    Directory.CreateDirectory(MF+"/override/campaign"); Directory.CreateDirectory(MF+"/override/ModAssets/parachutes");
    File.WriteAllText(MF+"/override/campaign/campaigns.txt","MOD campaigns"); File.WriteAllText(MF+"/override/ModAssets/parachutes/chute.fbx","fbx"); File.WriteAllText(MF+"/override/same.txt","identical");
    File.Copy(R+"/hf3.dll", MF+"/Assembly-CSharp.dll"); File.WriteAllText(MF+"/mod_info.txt","name=PlaguePhreak's Improved WOTS Mod\nversion=0.30 Mega Patch 01 hotfix 3\n");
  }
  static int fails=0; static void Expect(bool c, string what){ Console.WriteLine((c?"  PASS ":"  FAIL ")+what); if(!c) fails++; }
  static void Main(){
    var hf3 = StockFp.FileMd5(R+"/hf3.dll");
    // 1
    Console.WriteLine("== 1. original game: install, reinstall, restore");
    Fresh(R+"/stock.dll"); var ov0=TreeHash(Ov); var ui=new Ui(); var I=new Installer(MF, ui);
    var st=I.Inspect(G); Console.WriteLine("  state: "+st.Describe);
    Expect(I.Install(st), "install ok"); Expect(StockFp.FileMd5(Dll)==hf3, "DLL == hotfix 3 exactly");
    Expect(File.ReadAllText(Ov+"/campaign/campaigns.txt")=="MOD campaigns" && File.Exists(Ov+"/ModAssets/parachutes/chute.fbx") && File.Exists(Ov+"/keep.txt"), "override copied, player file kept");
    st=I.Inspect(G); Expect(st.Installed, "shows installed: "+st.Describe);
    Expect(I.Install(st), "reinstall ok"); Expect(StockFp.FileMd5(Dll)==hf3, "still hotfix 3");
    st=I.Inspect(G); Expect(I.Restore(st), "restore ok"); Expect(StockFp.FileMd5(Dll)==StockFp.FileMd5(R+"/stock.dll"), "DLL back to original");
    Expect(TreeHash(Ov)==ov0, "Override folder exactly as before"); Expect(!Directory.Exists(G+"/WOTS Mod Backup"), "backup folder removed"); Expect(ui.asked.Count==0, "no questions asked");
    // 2
    Console.WriteLine("== 2. another DLL mod present: merge, update, restore");
    Fresh(R+"/other.dll"); ov0=TreeHash(Ov); ui=new Ui(); I=new Installer(MF, ui); st=I.Inspect(G); Console.WriteLine("  state: "+st.Describe);
    Expect(I.Install(st), "install ok"); Expect(ui.asked.Contains("Clash with another mod"), "clash question asked");
    var m1=StockFp.FileMd5(Dll); Expect(m1!=hf3, "merged DLL differs from plain hotfix 3");
    using (var mm = Mono.Cecil.ModuleDefinition.ReadModule(Dll)) Expect(mm.GetType("OtherModMarker")!=null && mm.GetType("ModVersion")!=null, "both mods' classes present");
    st=I.Inspect(G); Expect(I.Install(st), "update ok"); Expect(StockFp.FileMd5(Dll)==m1, "update gives the same DLL");
    st=I.Inspect(G); Expect(I.Restore(st), "restore ok"); Expect(StockFp.FileMd5(Dll)==StockFp.FileMd5(R+"/other.dll"), "DLL back to the other mod's DLL"); Expect(TreeHash(Ov)==ov0, "Override as before");
    // 3
    Console.WriteLine("== 3. clash, player says No");
    Fresh(R+"/other.dll"); ov0=TreeHash(Ov); ui=new Ui(); ui.answers.Enqueue(false); I=new Installer(MF, ui); st=I.Inspect(G);
    Expect(!I.Install(st), "install cancelled"); Expect(StockFp.FileMd5(Dll)==StockFp.FileMd5(R+"/other.dll"), "DLL untouched"); Expect(TreeHash(Ov)==ov0, "Override untouched"); Expect(!Directory.Exists(G+"/WOTS Mod Backup"), "no backup folder left");
    // 4
    Console.WriteLine("== 4. old hand-installed copy of the mod (0.32.19)");
    Fresh(R+"/g19.dll"); ui=new Ui(); I=new Installer(MF, ui); st=I.Inspect(G); Console.WriteLine("  state: "+st.Describe);
    Expect(I.Install(st), "install ok (after Yes)"); Expect(StockFp.FileMd5(Dll)==hf3, "DLL == hotfix 3");
    st=I.Inspect(G); Expect(I.Restore(st), "restore ok"); Expect(StockFp.FileMd5(Dll)==StockFp.FileMd5(R+"/g19.dll"), "back to the old copy");
    // 5
    Console.WriteLine("== 5. Steam put back the original DLL after install (game update / verify)");
    Fresh(R+"/other.dll"); ui=new Ui(); I=new Installer(MF, ui); st=I.Inspect(G); I.Install(st);
    File.Copy(R+"/stock.dll", Dll, true); st=I.Inspect(G); Expect(st.ManifestButChanged, "detected change: "+st.Describe);
    ui.asked.Clear(); Expect(I.Install(st), "install ok"); Expect(ui.asked.Contains("Game DLL changed"), "asked about the change"); Expect(StockFp.FileMd5(Dll)==hf3, "new base is original -> DLL == hotfix 3");
    st=I.Inspect(G); Expect(I.Restore(st), "restore ok"); Expect(StockFp.FileMd5(Dll)==StockFp.FileMd5(R+"/stock.dll"), "back to the new original");
    Console.WriteLine(fails==0 ? "ALL PASS" : fails+" FAILED");
  }
}
