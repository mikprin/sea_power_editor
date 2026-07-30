# 01C Rusted Spear — build notes

Mission file: [01C_rusted_spear.ini](../01C_rusted_spear.ini)
Script: [SCRIPT.md](SCRIPT.md)
Editor backbone it came from: `share/01C.ini`

**9 triggers, 4 objectives, 9 hostile patrol craft, 1 helicopter, 3 phases.**
For comparison: 01A is 8 triggers and 4 objectives, 01B is 13 and 5.

> Note: this folder is spelled `01C_ruested_spear`. The mission `.ini` uses the
> corrected `01C_rusted_spear`. Left the folder alone so nothing tracked moves —
> rename it if you want the two to match.

---

## Geography

Map centre unchanged from the backbone: `-6.08 / 39.04`, the Zanzibar Channel.

```
X = (lon - 39.04) * 60      Z = (lat + 6.08) * 60
```

The one fact that drove every placement decision: **Unguja (Zanzibar) island
occupies roughly X 8.4..30.6, Z -24..21.6.** That was derived by checking which
of the backbone's authored waypoints were valid water and which longitudes they
avoided at which latitudes. Consequences:

- `Z > 22` is north of the island — open water.
- `X < 8` is the channel, west of the island. Shallow, ~40 m, which is exactly
  what the script needs for "the submarine cannot dive".
- `X > 31` is the deep ocean east of the island.

Every position and waypoint in the mission sits inside water already proven by a
route you drew in the backbone. Nothing was placed on faith.

### The one change to your layout

**The deployment zone moved from NM (53, -8) to (54, 26).** Same 40 × 15 box,
same deep water east of Zanzibar, shifted 34 NM north.

Reason: at Z -15.5..-0.5 the box sat due east of the island *at the island's own
latitude*, so any westward course ran into Unguja. The player had to steam ~40 NM
around the north tip before the mission could begin. At Z 18.5..33.5 the box is
clear of the island in latitude and the run-in is a straight 20 NM to the channel
mouth.

Everything else of yours was kept and only renamed or re-scoped.

---

## Phase geometry

| Element | NM position | Notes |
|---|---|---|
| Player anchor | (38, 0, 26) hdg 270 | inside the deployment box, west edge |
| Picket line | (13.5, 25.5) (9.5, 25) (5.5, 24.5) (1.5, 24) | line abreast, 4 NM spacing, stationary |
| Nyoka holding position | (5.5, 0, 19.5) | surfaced, plant shut down |
| Nyoka transit route | (8, 24) → (11, 28) → (14, 31.5) | ~14.8 NM |
| NavPoint Zulu | (14, 31.5) r=4 | south end of the Pemba Channel — genuinely deep |
| Interceptor pair spawn | (-3, 14) (-3.6, 13.2) | mainland shore, 38 kt |
| Coastal squadron spawn | (24, 44) (25, 45) (23, 45) | ~15 NM to the shelf, ~24 min |
| Mi-14 spawn | (16, 1000, 58) | ~31 NM ingress, ~15 min |

Nyoka's crawl is ~14.8 NM and the win circle catches her 4 NM early, so the
escort leg is roughly **11 NM of effective transit — about 41 minutes at her
16 kt flank.** That number is the whole pacing budget of the mission and it is
why the sub sits at (5.5, 19.5) rather than deeper in the channel where you
originally marked her. Deeper in was a 2.5-hour crawl.

---

## Script → implementation decisions

### The submarine is a Foxtrot, not a Kilo

Your backbone had `wp_ss_kilo`. The script says "Project 641 Foxtrot or Project
877", and Foxtrot is the better pick on three counts:

- IDEA.md wants "шумная, но своя" — noisy but ours. Foxtrot is the noisy one.
- `wp_ss_kilo` is a 1980-88 boat. A defecting third-world crew running a
  hand-me-down fits the 1958-84 Foxtrot far better.
- Speed. `tools/units.py show wp_ss_foxtrot` gives T5 = **16 kt**, versus the
  script's assumed 12 kt. That saved ~15 minutes of crawl.

Briefing text says sixteen knots, not twelve, to match the actual data.

`VariantReference=Variant66` — one of the six Libyan-flagged variants
(Variant66-71).

### Nation: Libya

There is no Tanzania, Mozambique or Somalia in the game's nation vocabulary
(`tools/units.py nations`). Rather than fly a Sri Lankan flag off Zanzibar, the
regime is written as a Libyan-supplied client state and everything hostile flies
`Nation=libya`. That also makes the Foxtrot's Libyan variants correct rather than
a fudge, and gives SIREN a line with some texture in it: *"The regime buys its
hulls and its flags through Tripoli."*

### Enemy armament

`tools/units.py arsenal` on all three hostile hull types:

```
wp_pt_p6      25mm 2M-3    x1600
wp_pt_stenka  AK230 30mm   x10000  + noisemakers
wp_pt_p4      14.5mm 2M-5  x1200
```

Guns only. SIREN's briefing threatens the pressure hull with *massed autocannon
at close range* to match.

The useful consequence: **nothing hostile in this mission carries a missile.**
The threat is close-range gunfire and one CAS-fitted Mi-14, so a gun destroyer
can win the whole contract without opening a missile magazine — which is the
point, because the fee is a submarine, not cash.

### Handing over the submarine

`Trigger4` fires when the player gets within 3 NM and runs
`Action_UnitTransferToTaskforce=Taskforce1` on `NeutralSubmarine1`.

**This is the one inferred field in the file.** Vanilla Pacific Strike uses that
action with the values `Neutral` and `Taskforce2` only; `Taskforce1` is
documented in the community guide but never appears in a shipped mission. If the
engine rejects it, the player cannot steer her — every other trigger still
fires, so the mission does not break, it just stops being an escort. **Worth
testing first.**

The transit route is issued in the same trigger and telegraph is set three
redundant ways (`Action_UnitTelegraph`, `Action_UnitVelocityInKnots`, and a
`/SetTelegraph,5` inline command on the first waypoint) because docs/CLAUDE.md
§5 flags all of those as unverified. The player can override every one of them
by hand, which is the real safety net.

She is authored with **no `Waypoints=` and `Telegraph=0`** so she cannot wander
off her marked position before the player arrives.

### Making the enemy go for the sub, not the player

The script asks for AI targeting overrides. The mechanism used is scripted
attacks on the unit sections:

```ini
Attack=NeutralSubmarine1,15,wp_1
```

Target, seconds after reaching the named waypoint, waypoint number. Ammunition
and shot count are omitted so they just use their guns.

**Also unverified** — `Attack=` appears nowhere in Pacific Strike; it is
community-guide only. Fallback if it is ignored: both interceptor pairs run
authored routes that pass straight through the submarine's transit lane with
weapons free, so the phase still plays as an ordinary intercept. Degrades, does
not break.

### Phase gating is deliberately loose

`Trigger4` (rendezvous) is **not** gated on the blockade being destroyed. A
player who threads the picket line instead of clearing it still gets the
submarine — they just forfeit the `BreakBlockade` objective. Gating one on the
other would soft-lock the mission for anyone who slipped past a single boat.

`Trigger7` (win) is `Disabled=True` until the rendezvous, so reaching Zulu with
a still-neutral submarine cannot end the mission early.

### No despawn at Zulu

The script suggests despawning the sub or forcing a max-depth dive. Neither is
needed: the mission ends on the same frame the circle is entered, so the crash
dive is narrative only. `Action_DestroyUnits` on the player's own new submarine
would have shown up as a loss in the AAR.

---

## Structural notes

- **Objectives are the script's three, plus task force survival.** A first pass
  had six: `BreakBlockade` and a hidden `KillHelo` were cut, along with the
  trigger that awarded the second one. Clearing the picket is something the
  mission already forces, and shooting down the helicopter is optional flavour
  that does not need a scoreboard entry. Trigger count went 10 → 9.
- **The picket line is not in a formation, on purpose.** A formation would
  station-keep the three followers onto the leader's bearing and collapse the
  4 NM line the moment the player opened fire. `Telegraph=0` with no waypoints
  holds each boat independently.
- **`Trigger4` and `Trigger5` share one condition** and exist as two triggers
  only because `Action_Units` is per-trigger, not per-action (docs/CLAUDE.md §5).
  Trigger4 handles the submarine; Trigger5 spawns the interceptors. Trigger5 also
  carries `Action_EnableTriggers=Trigger7`, because Trigger4 already spends its
  one `Action_EnableTriggers` line on Trigger6 and a comma list on that action is
  not confirmed in vanilla.
- **Neutral fishing craft have no fail condition.** This is a stand-up gun fight
  with weapons free from second one; punishing a stray round would be miserable.
  They exist so the radar picture at the channel mouth is not four clean
  contacts.
- **Retreat anchor added.** Regime boats run Morale 2-3 and will break; without a
  `[GameplayAnchors]` `RetreatPoint_Red_1` they have nowhere to run to.
- **Map symbol New7 changed from Surface to Air** — the northern threat in this
  contract is the Mi-14, so the briefing icon should say so.
- **Date moved 26 Jun → 16 Jul 1985** so the optional contracts read in order
  behind Mission 01: 01A is 2 Jul, 01B is 9 Jul, 01C is 16 Jul.

---

## Campaign wiring

`campaign.ini` gained `[Mission4]`, `NumberOfMissions=3 → 4`.

- `Parents=1`, `IsUnlocked=False`, `RequiredResult=Victory` — same shape as 01A
  and 01B, a side contract hanging off Mission 01.
- Threat profile: ship 3, air 2.
- `TaskForceModeCompletionPoints=15` — thin on purpose. The pay is the boat.
- The fee is granted by
  `TaskForceModeCompletionRewardedUnits=wp_ss_foxtrot,Variant66,1` rather than by
  `JoinTaskForce=True` on the mission unit. `JoinTaskForce` is only documented for
  sections that are already `Taskforce1SubmarineN`, and this boat is
  `NeutralSubmarine1` until runtime. Losing her fails the mission anyway, so
  "reward regardless of survival" costs nothing.
- `player_task_force_roster.ini` gained `wp_ss_foxtrot=Variant66|110` under
  `[AllowedSubmarines]` **only so the awarded boat has a roster entry to live in**
  and can be repaired. It is deliberately absent from every
  `TaskForceModeAllowedRosterUnits` line, so it is never purchasable. If a later
  mission should let the player buy a second one, add it there.

---

## Validation run

```
python3 tools/units.py check campaigns/PhantomWake/missions/01C_rusted_spear.ini
-- 15 unit section(s) checked, 0 problem(s)
```

Also checked by hand, all clean:

- every `<Token>` in a `ConditionsCompleted` has a matching `Condition_<Token>_Type`,
  and no condition is defined but unused
- every `Action_*_Message` / `_Intel` / `_Forecast` / `_AreaLabel` / `LabelKey`
  resolves in `[Language_en]`
- every objective named in an `Action_Objectives*` exists in `[Taskforce1_Objectives]`
- every `Action_Units` and formation member names a real section
- every `Disabled=True` unit is enabled by exactly one trigger, and every
  `Action_SetEnabledStatus=True` target is actually authored `Disabled=True`
- every `Disabled=True` trigger is enabled by another trigger
- every `Action_VariableSet` name is declared in `[CampaignVariables]`
- all `NumberOf*` counts match the real section counts
- campaign `TaskForceModeAllowedRosterUnits` is a strict subset of the roster file

One bug was caught by that pass and fixed: `Trigger7`, the victory trigger, was
`Disabled=True` with nothing enabling it. The mission was unwinnable.

---

## Open items for playtest

Only two, and both are engine questions rather than design ones.

1. **`Action_UnitTransferToTaskforce=Taskforce1`.** The load-bearing unverified
   field. If the boat does not become steerable at the rendezvous, this is why.
2. **`Attack=` on vessel sections.** Not in vanilla at all. If the interceptors
   ignore the submarine and chase the player instead, this is why.

**No time limit**, matching Mission 01 and 01A. 01B is the only mission in the
campaign with one — a 7200 s sunrise hard fail plus an 80-minute warning — and it
has one because that contract is explicitly a before-dawn infiltration. Nothing
in this one expires.
