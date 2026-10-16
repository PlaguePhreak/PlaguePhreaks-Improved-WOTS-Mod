# v0.21.3 Hit log tweaks [HITLOG]

## Edit 1 - bounces show in the hit log (Ammunition.OnTriggerEnter)
In the bounce block, find the line `UnityEngine.Debug.Log("[TORPHIT] " + base.name + " bounced off " ...`.
Paste this directly ABOVE it:
```csharp
int bounceSide;
string bounceFirer = ModHitLog.FirerName(firedByUnitID, out bounceSide);
string bounceTarget = ModHitLog.Paint(ModHitLog.ShipName(component3), (component3.faction == Faction.Player) ? "#80b8ff" : "#ff7070");
string bounceBy = (bounceFirer != string.Empty) ? (ModHitLog.Paint(ModHitLog.Capital(bounceFirer), (bounceSide == 0) ? "#80b8ff" : "#ff7070") + "'s ") : "A ";
ModHitLog.Add(bounceBy + ModHitLog.Paint("<b>torpedo</b>", "#ffffff") + " glanced off " + bounceTarget + " and ran on: " + ModHitLog.Paint("<b>bounced</b>", "#b0b0b0"));
```

## Edit 2 - no torpedo / bomb hit lines in General (MessageLog.SendMessageToLog)
Directly after the first `if (!LanguageManager.messageLogDictionary.ContainsKey(messageRef)) { ... return; }` block, add:
```csharp
if (messageRef == "TorpedoHit" || messageRef == "BombHit")
{
    if (this.audioReferences.ContainsKey(messageRef))
    {
        AudioManager.instance.PlayMessageAudio(AssetLoader.instance.ImportAudioClip(this.audioReferences[messageRef]));
    }
    return;
}
```
Hit sounds keep playing. Dud messages (TorpedoHitDud / BombHitDud) still show in General because the hit log does not cover duds.
Status: compiled and tested, works.
