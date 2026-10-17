# New win conditions and objectives text (draft, untested)

Status: written, not tested in game.

## How the game decides
`CampaignManager.CheckWinCondition` uses `mustControl` and `maxAirAt` from each campaign's `setup.txt`. The player wins when they hold ALL `mustControl` locations at once (and the `maxAirAt` / `maxPortAt` levels are met). The player loses when the ENEMY holds all of them at once. One list therefore works for both sides.

## Change
`mustControl` is now `["rabaul","cooktown","newhebrides"]` in both campaigns, and `maxAirAt` is now `[]` (the Guadalcanal rank 5 airfield is no longer needed).
- Allies win by capturing Rabaul while keeping Cooktown and New Hebrides. Japan wins by capturing Cooktown and New Hebrides while keeping Rabaul.
- In campaign002 (player Japan) the same list applies the other way round.
- The AI also uses `mustControl` as its list of secondary targets, so it will now go for these three locations.

## Objectives screen
New `objectives.txt` for both campaigns in `Override/language/english/campaign/campaign00X/`. Gold location names use the same `<color=#E0B030>` tag as the logbook.

## Final version (written straight into the override folder)

- `mustControl`: rabaul, lae, guadalcanal, cooktown, newhebrides, rennell. `maxAirAt`: guadalcanal (rank 5 airfield).
- The engine has one list, so the "secondary" objectives (Lae for the Allies, Rennell for Japan) must also be held to win. The objectives text says all items must be held at once.
- Cooktown: port level 1, `createShips` true (Allied home port, weekly supply). Rennell now starts Allied with a 300 man garrison and 300 supplies.
- objectives.txt, victory.txt and defeat.txt rewritten for both campaigns; campaigns.txt descriptions updated.
