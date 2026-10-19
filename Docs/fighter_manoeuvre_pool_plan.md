# Fighter manoeuvre pool and team tactics (plan for 0.26.4.2 onward; requested by Aaron, 18 Oct)

Goal: each pilot picks from a large pool of moves for the situation, rarely, and pilots work as pairs and flights, so fights differ every time.

## How picking will work
1. **Situation read** (every 1 s per pilot): range, angle off the enemy's tail, who has the height and speed advantage, whether the enemy is turning, whether a friend is in trouble, my ammo-less state is not tracked (no ammo model), and my own speed (energy).
2. **Each move has a fitness score** for the situation (0 to 1), a minimum pilot rank, and a cooldown. The pilot rolls among the moves that are legal and fit, weighted by score, so the same situation does not always give the same move.
3. **Rarity (done in 0.26.4.1):** a pilot makes at most one special move (yo-yo, barrel roll, split-S, roll-over and the new ones) every 25 to 50 seconds, and each move also has its own low chance. Plain gun runs, breaks and cover are not limited.
4. **Teams:** pairs (leader and wingman) and flights of 3 to 4. Team moves are started by the flight leader and given to the others as roles (attacker, support, decoy), so they work together and not separately.
5. **Stay in the area (done in 0.26.4.1):** the game removes any plane that is more than 5000 units (50 km) from the middle. Fighters now turn back at 4300.

## The pool
Rank: G Green, T Trained, V Veteran, E Elite. "Steer" means moves built from the game's turn, height and speed wishes. "Acro" means flown by `ModFlight.Acro` (the plane turned directly, like the roll-over attack).
| Move | What it does | Built from | Rank | When it fits |
|---|---|---|---|---|
| Break | Hard turn into the attacker (exists) | Steer | G | enemy on my tail |
| Pursuit curves | Chooses lead, pure or lag pursuit by range and angle: lead pursuit when far and well placed, pure when close, lag when too fast or too close | Steer | T | every gun run |
| High yo-yo | Pull up out of the turn plane to cut the angle without overshooting (exists, now rare) | Steer | V | closing fast from behind |
| Low yo-yo | Dip below the enemy's turn plane to gain speed and close from behind when too far back | Steer | V | enemy turning away, I am slow |
| Lag displacement roll | Lag behind and roll off to the outside of the enemy's turn to stop an overshoot | Steer | V | overshoot, enemy hard turning |
| Out-of-plane manoeuvre | Break out of the enemy's turn plane (up or down and away) to dodge a tailing shot and set up a reversal | Steer | T | enemy on tail inside 400 m |
| Hit-and-run | One fast firing pass then straight away at full speed, no turning (the US pass, made a named move with its own trigger) | Steer | T | I am faster or higher |
| Unloaded extension | Push the nose to level or slightly down, unload the turn, accelerate straight away, then turn back in | Steer | V | slow, outnumbered, or enemy turns better |
| The Scissors | A series of reversing turns with the enemy, both fighters slowing, aimed at forcing it to overshoot | Steer, pairs with the enemy's side | V | a turning fighter on my tail at close range, I turn well |
| Defensive spiral | A tight diving spiral turn with the throttle back, losing height to keep speed | Steer + barrel | T | enemy on tail, no wingman help |
| High-g barrel roll | A wide barrel roll with a climb to force an attacker to overshoot (a bigger version of the barrel roll now in) | Acro | V | enemy close behind, above stall speed |
| Barrel roll attack | A roll round the target's line to stay out of its turn and fire from the side | Acro | V | attacking a bomber or a straight-flying fighter |
| High-side guns pass | Attack from high and to the side, firing through the deflection, then pull away over the target | Steer | T | target below and ahead, I have height |
| Immelmann | Half loop up then roll upright, reversing heading with a gain in height | Acro | V | after a pass, enemy low on my tail, I am fast |
| Split-S | Half roll and pull through (exists, now rare, US Elite only) | Acro | E | enemy on tail, plenty of height |
| Pitchback | Pull up steeply and reverse back toward the target as it passes underneath | Steer + Acro | V | enemy overshoots below and ahead |
| Wingover | Climbing turn through about 180 degrees, trading speed for a heading change | Steer | T | slow, fighting at low speed |
| Zoom climb | Exists | Steer | T | after a pass |
| Team: Combat spread | Flight spreads out 500 to 1000 m abreast so each covers the others' tails | Steer | T | flight leader, no contact yet |
| Team: Defensive split | When bounced the two aircraft break in opposite directions, forcing the attacker to choose one | Steer | T | two or more under attack |
| Team: Sandwich | Two fighters attack one enemy from opposite sides, so it can only turn into one | Steer | T | 2 or more of us near one enemy |
| Team: Thach Weave | Exists, only 50% and Veteran or better | Steer | V | one wingman bounced |
| Team: Wingman cover | Exists (goes after the enemy on a friend's tail) | Steer | T | friend in trouble |
| Team: Decoy | A fighter flies as bait while the others set up above | Steer | E | outnumbered |

## Honest limits
- There is no ammo, fuel-for-the-fight or real aerodynamics model; scores use speed, height, range and angles only.
- The Scissors and Sandwich need two pilots to agree. The flight leader starts them and the others get a role; it will take a couple of test rounds to look right.
- Some moves look alike on screen (low yo-yo, lag displacement roll and the out-of-plane break are all curved paths). They will differ in the numbers (height change, turn rate, speed), not in the code path.

## Build order (each a test round)
- **0.26.4.1 (written):** rare special moves, stay in the battle area.
- **0.26.4.2:** the pool and the picking system, plus the Steer moves that replace what is there: pursuit curves, low yo-yo, lag displacement roll, out-of-plane, hit-and-run, unloaded extension, defensive spiral, high-side guns pass, wingover.
- **0.26.4.3:** Acro moves: Immelmann, pitchback, high-g barrel roll, barrel roll attack.
- **0.26.4.4:** team moves: combat spread, defensive split, sandwich, scissors, decoy.
