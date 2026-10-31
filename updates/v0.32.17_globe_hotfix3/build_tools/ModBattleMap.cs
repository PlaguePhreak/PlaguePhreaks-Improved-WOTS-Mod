using System;
using UnityEngine;
using UnityEngine.UI;

// 0.32.9 Globe phase 6: the battle minimap shows the campaign map's own picture of the battle square.
// A campaign battle's terrain is a 512 x 512 pixel cut of the DEM at 240 pixels per degree, centred on the attacked force
// (TerrainTiles.GetMapImage). This cuts the same square out of the campaign map textures (the four quads the campaign map
// is drawn with) and puts it on the minimap's image instead of the height-map shading. Called at the end of
// TerrainTiles.InitialiseTerrain (both returns). Skirmishes and non-campaign battles are left alone.
public static class ModBattleMap
{
    public static bool On = true;            // false = stock minimap picture
    public static int Size = 512;            // pixels of the cut (the DEM cut is 512)
    private static Texture2D last;
    private static bool reported;

    public static void Apply()
    {
        try
        {
            if (!On) return;
            CampaignManager cm = CampaignManager.instance;
            Map map = Map.instance;
            if (cm == null || cm.campaignData == null || map == null || map.mapImage == null) { Debug.Log("[BMAP] no campaign or no minimap image, stock minimap kept"); return; }
            if (EngagementManager.instance == null || EngagementManager.instance.engagementData == null || !EngagementManager.instance.engagementData.isCampaignEngagement) { Debug.Log("[BMAP] not a campaign battle, stock minimap kept"); return; }
            CampaignData d = cm.campaignData;
            int[] c = d.lastEncounterPixelCoords;
            if (c == null || c.Length < 2 || d.mapOriginXY == null || d.mapOriginXY.Length < 2 || d.mapPixelWidth <= 0) { Debug.Log("[BMAP] no encounter pixel coords, stock minimap kept"); return; }
            if (cm.mapMaterial == null) { Debug.Log("[BMAP] no campaign map material, stock minimap kept"); return; }
            Texture2D[] q = new Texture2D[4];
            string[] names = cm.mapSharderQuads != null && cm.mapSharderQuads.Length == 4 ? cm.mapSharderQuads : new string[] { "_TexTL", "_TexTR", "_TexBL", "_TexBR" };
            for (int i = 0; i < 4; i++) { q[i] = cm.mapMaterial.GetTexture(names[i]) as Texture2D; if (q[i] == null) { Debug.Log("[BMAP] campaign map quad " + names[i] + " missing, stock minimap kept"); return; } }
            float w = d.mapPixelWidth, h = d.mapPixelWidth * 0.5f;
            int n = Mathf.Clamp(Size, 64, 1024);
            Texture2D tex = new Texture2D(n, n, TextureFormat.RGBA32, false);
            tex.wrapMode = TextureWrapMode.Clamp;
            Color[] px = new Color[n * n];
            // the DEM cut covers 512 DEM pixels (1/240 degree each) centred on the encounter pixel, bottom-left = centre - 256
            float x0 = c[0] - 256, y0 = c[1] - 256;
            for (int y = 0; y < n; y++)
            {
                float py = y0 + (y + 0.5f) * 512f / n;
                float v = (py - d.mapOriginXY[1]) / h;
                for (int x = 0; x < n; x++)
                {
                    float pxl = x0 + (x + 0.5f) * 512f / n;
                    float u = pxl - d.mapOriginXY[0];
                    u = ((u % 86400f) + 86400f) % 86400f;            // the pixel x can be wrapped round the world
                    u /= w;
                    Color col;
                    if (u < 0f || u > 1f || v < 0f || v > 1f) col = new Color(0.1f, 0.15f, 0.25f, 1f);
                    else
                    {
                        int qi = (u < 0.5f ? 0 : 1) + (v >= 0.5f ? 0 : 2);   // TL, TR, BL, BR
                        float lu = (u < 0.5f ? u : u - 0.5f) * 2f, lv = (v >= 0.5f ? v - 0.5f : v) * 2f;
                        col = q[qi].GetPixelBilinear(lu, lv);
                        col.a = 1f;
                    }
                    px[y * n + x] = col;
                }
            }
            tex.SetPixels(px); tex.Apply(false, false);
            Image img = map.mapImage.GetComponent<Image>();
            if (img == null) { Debug.Log("[BMAP] minimap has no Image component"); return; }
            img.material = null;
            img.sprite = Sprite.Create(tex, new Rect(0f, 0f, n, n), new Vector2(0.5f, 0.5f));
            img.preserveAspect = false;
            if (last != null) UnityEngine.Object.Destroy(last);
            last = tex;
            Debug.Log("[BMAP] minimap shows the campaign map at pixel " + c[0] + "," + c[1]);
        }
        catch (Exception ex)
        {
            if (!reported) { reported = true; Debug.LogError("[BMAP] failed: " + ex.ToString()); }
        }
    }
}
