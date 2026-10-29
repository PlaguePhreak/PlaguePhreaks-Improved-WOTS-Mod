# 0.32.10 merge notes

- **Base:** 0.32.9 globe test 9 (md5 831b6169dc1979fc175105e8199bdd0d).
- **Output:** md5 89192094a7a60b704430cb2073af189a.
- **Changed:** CampaignManager.Check5Min only (the fuel hotfix), version strings 0.32.9 -> 0.32.10 and a changelog entry.

## Hook (dnSpy)
CampaignManager.Check5Min: the `if (campaignData.revealAllContacts)` test that wrapped the whole fuel loop is moved down so
it only wraps the first loop over otherMobile (the enemy-icon refresh). Exactly the steps in the fuel hotfix README.

Verified: CampaignManager decompile equals the fuel hotfix DLL (2add2a95) plus the known 0.32 hooks (ModGlobe.Ensure,
ModGeo.Battle x2, JoinRadiusMetres, WrapPixel, Metres); all other classes identical to 0.32.9; ilverify list identical.
