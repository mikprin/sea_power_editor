# Sea Power mission authoring — field notes

Things learned by reading vanilla campaigns that are **missing from, or contradict**,
`Mission_Creation_Community_Guide.md` and `Task_Force_Campaign_Guide.md`. Everything
below was verified against real files under `campaigns/pacific-strike-task-force/`
and `share/OriginalMissions/{Linear1,Molina}` (the full original 11-mission vanilla
set — checked later, so referenced only in the sections that cite it by path); where
something is inferred rather than confirmed it says so.

Read this before writing a mission `.ini`. It is cheaper than re-deriving it.

---

## 1. Geo ↔ NM conversion (the single most useful fact)

`RelativePositionInNM=X,alt,Z` and `Condition_*_PositionNM=X,alt,Z` are offsets
from `MapCenterLatitude` / `MapCenterLongitude`:

```
X = (lon - MapCenterLongitude) * 60     ; +X = East
Z = (lat - MapCenterLatitude)  * 60     ; +Z = North
```

**There is no cosine-of-latitude correction.** One degree of longitude is treated
as 60 NM at every latitude.

Proof, `01 Raid on Okinawa.ini`: map center `26.53 / 127.47`; the Kume trigger
circle is at geo `26.37616 / 126.748406` and `PositionNM=-43.33733,0,-9.341428`.
`(126.748406 - 127.47) * 60 = -43.30` ✓. With a cosine term it would be `-38.75` ✗.
Latitude: `(26.37616 - 26.53) * 60 = -9.23` ✓.

Consequence: at high latitude your NM offsets stretch east-west relative to real
distance. Lay out missions in NM first, then only use geo for map symbols and zones.

The middle value is **altitude in feet** for air units, `0` for surface, and for
submarines a keyword: `low`, `periscope`, `shallow` (also valid in waypoints, e.g.
`Waypoints=23.0933,Shallow,-7.4392`).

---

## 2. There is no relative timer. Plan around it.

`Condition_*_Type=Time` is **always absolute seconds from mission start**. There is
no "start a 90-second countdown when X happens" condition. `Disabled=True` +
`Action_EnableTriggers` does *not* rebase the clock — an enabled trigger whose
`Time` has already passed fires immediately.

Three workarounds. **C, the stopwatch unit (§16), is the only true relative delay** —
prefer it when the delay must start on an event. A and B are the cheap options.

**A. Area + absolute deadline, ANDed.** The loss only lands if the threat is still
present at the deadline, so killing it cancels the trigger:

```ini
[Trigger10]
Condition_StillThere_Type=UnitsInTheArea
Condition_StillThere_PositionNM=-1.51,0,-4.12
Condition_StillThere_AreaRadiusNM=4
Condition_StillThere_Units=Taskforce2Helicopter1
Condition_Deadline_Type=Time
Condition_Deadline_Time=3050
ConditionsCompleted=<StillThere> AND <Deadline>
```

For this to feel like a timer the threat's **arrival must be deterministic** — spawn
it with a fixed `Time` trigger, not an event-driven one, so you can compute
`deadline = spawn + transit + grace`.

**B. A trigger with no conditions at all fires the moment it is enabled.** See
`09 Shadows off Palawan.ini` Trigger5: `Disabled=True` and nothing but actions.
Useful as a "do this later, when I say so" hook.

`Action_DisableTriggers=TriggerN` cancels a pending deadline (e.g. threat destroyed).
`Action_ReactivateTriggers` re-arms an already-fired trigger so it can fire again.

**C. The stopwatch unit.** Spawn a unit that travels a known distance at a known
speed and gate on its arrival. See §16 — this is the real answer.

Also seen in vanilla and unexplained: `Condition_Condition1_Time=-27900`
(`02 Action in the Taiwan Strait.ini`, Trigger5). Negative times are undocumented and
did not correspond to any obvious clock offset. Do not copy it.

---

## 3. Area conditions are static circles, never "distance to unit"

`UnitsInTheArea` takes a fixed `PositionNM` + `AreaRadiusNM`. You cannot anchor an
area to a moving ship. To gate on "escort reaches the convoy" you place the circle
where the convoy *will be* and widen the radius to absorb drift.

Fields:

```ini
Condition_X_Type=UnitsInTheArea
Condition_X_PositionNM=16.5,0,-6.9
Condition_X_AreaRadiusNM=10
Condition_X_AreaLabel=Trigger5Condition_XAreaLabel   ; key in [Language_en]
Condition_X_AreaDisplaySide=Blue                     ; Blue | Both | None
Condition_X_Units=Taskforce1Submarine1
Condition_X_MinimumUnits=2                           ; optional
```

`Type=Generic` with a `PositionNM` + `AreaRadiusNM` + `AreaLabel` and no `Units` is
how vanilla draws a **labelled circle on the tactical map without any trigger logic**
(`08A Pathfinders.ini` Trigger6, `07 Action in the Java Sea.ini` "Datum A01"). Cheap
way to mark a search box.

### Barrier lines: there is no rectangular trigger area

`Kind=Rectangle` and `Shape=Rectangle` exist for **map symbols and zones only**.
Trigger conditions accept `AreaRadiusNM` and nothing else, so a "line the player
cannot sail around" has to be built as a **chain of overlapping circles ORed inside
one trigger**:

```ini
Condition_Gate1_Type=UnitsInTheArea
Condition_Gate1_PositionNM=-7.267,0,-6.836
Condition_Gate1_AreaRadiusNM=3
Condition_Gate1_AreaDisplaySide=None
Condition_Gate1_Units=NeutralVessel1
; ...Gate2..Gate7 spaced 5 NM apart along the barrier bearing...
ConditionsCompleted=<Gate1> OR <Gate2> OR <Gate3> OR <Gate4> OR <Gate5> OR <Gate6> OR <Gate7>
```

Radius 3 with 5 NM spacing gives a continuous 6 NM wide corridor with 1 NM of
overlap — no gaps for a unit to thread. Set every gate to `AreaDisplaySide=None` and
draw one `Kind=Rectangle` map symbol over the same line so the player sees a clean
barrier instead of a string of blobs.

Check the geometry before shipping: compute the minimum distance from each gate
centre to every leg of the target's route. Exactly one gate should be under the
radius; the neighbours sitting ~4–5 NM off are what catch a player who steers wide.

---

## 4. Condition names are free-form, not `Condition1`

The editor always writes `Condition_Condition1_*`, which makes multi-condition
triggers unreadable. The parser only cares that the name in `Condition_<Name>_Type`
matches the token in `ConditionsCompleted`. Use real names:

```ini
Condition_SkiffsDead_Type=UnitDestroyed
Condition_SkiffsDead_Units=Taskforce2Vessel1,Taskforce2Vessel2
Condition_Halfway_Type=Time
Condition_Halfway_Time=2100
ConditionsCompleted=<SkiffsDead> OR <Halfway>
```

`ConditionsCompleted` is case-insensitive on the token (vanilla mixes
`<CONDITION2> AND NOT <CONDITION1>` with lowercase definitions).

Condition types actually used in vanilla: `UnitDestroyed`, `Time`, `UnitsInTheArea`,
`UnitClassified`, `Generic`, `OnMissionStart`, `HasNoUnitsOfType`, `VariableCheck`,
`UnitDetected`.

`HasNoUnitsOfType` is the clean "side wiped out" check:

```ini
Condition_NoHulls_Type=HasNoUnitsOfType
Condition_NoHulls_Taskforce=Taskforce1
Condition_NoHulls_UnitType=Vessel
```

### `UnitDetected` / `UnitClassified` — `_Taskforce=` is the *detector*

Both take `_Taskforce=` (the side **doing** the detecting/classifying) and
`_Units=` (what is being detected, **whatever side owns it**), plus optional
`_MinimumUnits=` and, on `UnitClassified`, `_UnitType=`. They respect
radar/sonar range, active/passive modes and fog of war.

The two fields are easy to read backwards, and getting it wrong is not a
no-op: naming the same side in both (`_Taskforce=Taskforce2` on
`Taskforce2Vessel*`) means "that side detects its own hulls", which is true at
t=0, so the trigger fires on the first frame.

The cross-side vanilla files settle it:

```ini
; Molina/02 Guns of Port Louis.ini Trigger7 - "TG 74.4 detect", player finds enemy
Condition_Condition1_Type=UnitDetected
Condition_Condition1_Taskforce=Taskforce1
Condition_Condition1_Units=Taskforce2Vessel4,Taskforce2Vessel5,Taskforce2Vessel6
Condition_Condition1_MinimumUnits=1
```

**This is also the "the enemy has spotted us" trigger** — invert the sides. Two
vanilla precedents, both `UnitClassified`:

```ini
; Molina/01 Wolves of the South Atlantic.ini Trigger4
; Name=Merchants move east once player detected
Condition_Condition1_Type=UnitClassified
Condition_Condition1_Taskforce=Taskforce2
Condition_Condition1_Units=Taskforce1Vessel1,Taskforce1Vessel3,Taskforce1Vessel4,Taskforce1Vessel2
Condition_Condition1_MinimumUnits=2
```

`Linear1/02 Operation Revenge.ini` Trigger3 is the same shape
(`Description=When BLUFOR classified, start bombers moving`, `_UnitType=Vessel`).
Detection is not a place, so unlike a `UnitsInTheArea` circle it cannot be
steered around — this is the correct way to make stealth matter.

`UnitDetected` = raw sensor contact; `UnitClassified` = contact resolved to a
type. Use `Classified` for anything the story treats as recognition.

Ignore `10 Vengeance at Luzon.ini` Trigger9 as a model: it names `Taskforce2`
on `Taskforce2Vessel5` and is ANDed with `Time=300`, so it is effectively a
5-minute timer and proves nothing about the field's meaning. PhantomWake
copied that shape into eight triggers before the cross-side files were checked;
all eight are now `_Taskforce=Taskforce1`.

---

## 5. `Action_Units` is per-trigger, not per-action

Every unit-targeting action in a trigger applies to the **same** `Action_Units` list.
You cannot disable one unit's sensors and enable a different unit in one trigger.
Split into two triggers with identical conditions, or move one action elsewhere.
This bites constantly.

Verified action vocabulary (values matter):

| Action | Value |
|---|---|
| `Action_SetEnabledStatus` | `True` / `False` — spawns units authored with `Disabled=True` |
| `Action_EnableDisableSensorSystems` | `Enable` / `Disable` — **not** True/False |
| `Action_EnableDisableWeaponSystems` | `Enable` / `Disable` |
| `Action_EnableDisablePropulsionSystems` | `Enable` / `Disable` |
| `Action_EnableFlightDeckAI` | `True` / `False` |
| `Action_UnitTransferToTaskforce` | `Taskforce1` / `Taskforce2` / `Neutral` |
| `Action_UnitRevealToTaskforce` | `Taskforce1\|Identify` |
| `Action_UnitRevealTime` | `-1` for permanent |
| `Action_UnitWaypoints` | same format as `Waypoints=` |
| `Action_DestroyUnits` | `True` — instant kill, vanilla uses it for minefields |
| `Action_VariableSet` | `VarName,True` |
| `Action_ObjectivesCompleted` / `Failed` / `Cancel` / `UnHide` | comma list, **one line only** |
| `Action_EnableTriggers` / `DisableTriggers` / `ReactivateTriggers` | `TriggerN` |
| `Action_Forecast` | key in `[Language_en]` |
| `Action_Taskforce1_Message` / `_Intel` | key in `[Language_en]` |

`Action_UnitTelegraph`, `Action_UnitHeading`, `Action_UnitVelocityInKnots` are
documented in the community guide but appear **nowhere** in vanilla — treat as
unverified and set redundant pairs when a scripted charge matters.

---

## 6. Message format (the current one)

The guide shows the old `Title|Body|Button` pipe format. Vanilla English text uses a
keyed format instead, and it is much better:

```ini
Taskforce1StartMessage=Title=<size=24>MISSION NAME</size>\nBody=Text here.\n\nSecond paragraph.\nButtonText=Get underway\nPopupStyle=Intro
```

`PopupStyle` values: `Intro`, `Outro`, `Notification`, `NavalMessage`.
`Notification` reads as a radio call rather than a briefing card.

`NavalMessage` renders a formatted naval message and takes a different field set:

```ini
Key=From=CTF 77\nTo={TaskForceName}\nInfo=CINCPACFLT PEARL HARBOR HI\nSubj=MISSION ACCOMPLISHED\nPrecedence=Immediate\nClassification=Secret\nTemplate=USAUSNavy\nBody=1. (S) ...\nButtonText=Return to mission\nPopupStyle=NavalMessage\nMessageRole=Outro
```

`Template` values seen: `USAUSNavy`, `USAJCS`, `AustraliaRAN`.

**`{TaskForceName}` is substituted inside mission messages**, not just campaign text.
Use it — it makes a generic mission feel like it is about the player's force.

XAML-ish tags `<size=NN>`, `<color=Lime>`, `<color={*}D2B48C>` work in popups.
`\n` is a line break. Guide's warning about `#` and `/` stands, but closing tags
(`</size>`, `</color>`) are fine and used throughout vanilla.

Objective display text lives in `[Language_en]` under an `Objective_` prefix:
`Objective_DestroySlava=Sink the Slava`.

---

## 7. Objectives take a 4th field

Guide documents `ID=CompletedScore,FailedScore,StatusAtMissionEnd`. Vanilla adds a
tag:

```ini
[Taskforce1_Objectives]
DestroyCommandos=50,-50,Complete,Main     ; Main = primary, shown prominently
DestroyRaidGroup=20,-20,,Main             ; 3rd field may be empty
DestroySSGN=10,-10,Complete,Hidden        ; revealed by Action_ObjectivesUnHide
FlagshipMustSurvive=5,-5,Complete         ; no tag = secondary
DestroySAG=30,-30,                        ; trailing comma is legal
```

`Main` and `Hidden` are both observed. `Main,Hidden` together was **not** observed —
do not assume it parses.

---

## 8. Custom ship names

Not in either guide. Put these in `[Language_en]` (localisable):

```ini
NeutralVessel1NameOverride=Isabela LP-41
NeutralVessel1ShortNameOverride=Isabela
Taskforce1Vessel5NameOverride=...
Taskforce2LandUnit1ShortNameOverride=...
```

Key is `<SectionName>NameOverride`. This is how you name a story ship without
touching unit files — the intended use for scraped `.unitgroup` name data.

---

## 9. Waypoint inline commands

`Waypoints=` entries can carry an action, appended with `/`:

```
Waypoints=x,alt,z/SetTelegraph,2|x,alt,z/SetWeaponStatus,Free|x,alt,z|Loop
```

Observed commands: `SetTelegraph,<0-5>`, `SetWeaponStatus,<Free|Tight|Hold>`,
`SetSensors,<...>`, `VID,...`, `AttackAtWaypoint,<ammo>,<target>,<count>`.

`SetSensors` arguments seen: `AirSearch_On`, `AirSearch_Off`, `SurfaceSearch_On`,
`SurfaceSearch_Off`, `Emcon` (combinable, comma-separated).

A literal `Loop` as the final waypoint makes the unit cycle the route — the only way
to author a loiter or racetrack orbit.

Vanilla often writes `220.4727` as the altitude for surface waypoints. It is an
editor artifact and is ignored for surface units; `0` is fine.

---

## 10. Unit-section fields worth knowing

| Field | Notes |
|---|---|
| `Disabled=True` | authored but not spawned; `Action_SetEnabledStatus=True` spawns it in place |
| `RandomSpawnCenter` / `RandomSpawnRange` / `RandomSpawnDirection` | scatter spawn; `Direction` accepts `90` or a `90,350` arc. Great for replayability on clutter and subs |
| `SpawnByVariableAND=Var,IsFalse` | unit only exists if a campaign variable says so — how vanilla removes forces after an optional side mission is won |
| `SpawnDifficulty=Difficult,Moderate` | unit only exists at those difficulty presets |
| `AutomateRoute=True` | game generates aimless local movement. This is what makes fishing-boat clutter cheap — no waypoints needed |
| `Morale=` | 1–5; low morale units retreat. `RetreatAfterWeaponsExpended=True` pairs with it |
| `RetreatPoint=True` | on a `[GameplayAnchor]` section, see below |
| `IsValuableUnit=True` | AI protects it |
| `StationRole=` | `Core`, `AAW`, `ASW` — station-keeping role inside a formation |
| `StationPosition=x,0,z` | explicit station offset |
| `OverrideWeaponStatus=` | `Hold` / `Tight` — overrides the side default without changing `WeaponStatus` |
| `HomeBase=Taskforce2Vessel1` | where a helo recovers |
| `CampaignTag=wp_rkr_slava_Variant1` | required for Task Force Mode persistence tracking |
| `CampaignRepair=True` | unit is repairable between missions |
| `CampaignRearm=True` | unit is rearmed between missions — seen paired with `CampaignTag` on enemy units in `share/OriginalMissions/Linear1/04B Bargaining Chips - Red.ini` and `Molina/04 Chagos Gambit.ini` |
| `SetSelected=True` | unit selected when the mission opens |
| `CallsignIndex=` | picks a specific callsign from the unit's list |
| `TaskForceModeIgnoreUnit` | exempt a unit from generator replacement |
| `Nation=US` / `UK` / `china` | flag override on civilians — sells a false-flag merchant. Vanilla is inconsistent about case (`china` lowercase in a unit section, `China` in a variant file), so it is probably case-insensitive. Full nation vocabulary: `tools/units.py nations` |

`MissionType=Patrol` is the only value used in vanilla; `WeaponStatus` values are
`Free`, `Tight`, `Hold`; `CrewSkill` values used are `Green`, `Trained`, `Seasoned`,
`Veterans`, `Ultra`.

### Per-unit magazine overrides

The Task Force guide mentions "Stores Editor container overrides" without ever giving
the syntax. It is a **sibling section named after the unit**, not a field inside it:

```ini
[Taskforce2Vessel1]
Type=ir_fab_boghammar
VariantReference=Default

[Taskforce2Vessel1_WeaponSystem1]
Ammunition1=ir_107mm_rocket
Ammunition1_Count=0
```

`<UnitSection>_WeaponSystemN` targets the Nth weapon system on that hull;
`AmmunitionN` / `AmmunitionN_Count` set how many rounds of a specific ammo type it
carries. Count `0` empties the magazine while leaving the mount installed.

This is the correct lever for "armed, but not *that* armed" — de-fanging a specific
weapon on a unit without swapping its class or loadout, capping Harpoons or heavy
torpedoes on a task group, or making a neutral craft safe to misidentify.

Both halves can now be looked up (§17). `tools/units.py arsenal <alias>` prints every
weapon system on the hull, its magazine, the ammo it holds and the default count, then
emits the override block to paste:

```
$ python3 tools/units.py arsenal ir_fab_boghammar
  WeaponSystem1   107mm_Hasheb-1     Missile  ir_107mm_rocket   x441   5 NM
  WeaponSystem2   12.7mm_DSHK_Dual   CIWS     wp_cal_05in       x3000
```

`tools/units.py check <mission.ini>` validates the override too: a `WeaponSystemN`
the hull does not have, an ammunition alias that does not exist, or an override whose
owning unit section is missing from the file.

Two gotchas the table exposes:

- **The index is the weapon system, not the magazine.** Several systems can share one
  magazine — `usn_dd_gearing`'s twin MK32 mounts are `WeaponSystem2+WeaponSystem3`
  both feeding `WeaponMagazineTorpedo`. `arsenal` shows the shared owners joined with
  `+`; override either index.
- **Some magazines have no owning weapon system at all** (decoy and noisemaker
  ejectors sometimes sit alone). Those show a blank weapon system and cannot be
  targeted by a `_WeaponSystemN` override.

Verified from an editor-generated file, not from vanilla — no Pacific Strike mission
uses it.

---

## 11. Retreat anchors

Undocumented section type, used by the morale system:

```ini
NumberOfAnchors=1
Anchor1=RetreatPoint_Red_1

[RetreatPoint_Red_1]
Type=GameplayAnchor
Side=Red
AltitudeM=0
RetreatPoint=True
GeoPoint=8.048766,117.202809
```

Without one, broken units have nowhere to run to.

---

## 12. Zones and map symbols

`[Zone1] Type=Deployment` is the only zone type in vanilla. `Shape=Rectangle` or
`Polygon`. `GeoPoint` is the **centre**; `WidthNm` is E–W, `HeightNm` is N–S.
Vanilla deployment zones run 50×50 to 90×215 NM.

`[MapSymbol_*] Kind=` values: `Label`, `UnitIcon`, `Circle`, `Oval`, `Rectangle`,
`ThreatArrow`. `UnitIcon` needs `Side=Hostile` + `Domain=Surface|Air|Submarine`.
`ThreatArrow` needs `Bearing=` plus `NumberOfGeoPoints=1` and `GeoPoint1=` duplicating
`GeoPoint`.

`VisibleIn=CampaignMap,BriefingMap` is the default; add `,Mission` to keep a symbol
on the tactical map in-game. Only 7 of 165 vanilla symbols do this — use it sparingly
for things the player must navigate to.

---

## 13. Campaign variables

```ini
[CampaignVariables]
07ASlavaDestroyed=False
```

Declared in the mission that can set them, written with `Action_VariableSet=Name,True`,
read by `Condition_*_Type=VariableCheck` + `Condition_*_Variable=Name`, by
`SpawnByVariableAND=` on units, and by `TaskForceModeRearmByVariableAND` in
`campaign.ini`. This is the whole cross-mission consequence system.

Naming convention in vanilla is `<MissionNumber><Fact>`, e.g. `08AmmoCarrierSurvived`.

---

## 14. Task Force Mode gotchas

- The **anchor's `Type` and `VariantReference` are thrown away** in `Generated`
  missions — the generator only keeps position, heading, telegraph and waypoints. So
  a wrong variant on the anchor is harmless; a wrong variant in
  `player_task_force_roster.ini` silently removes the hull from Task Force Builder.
- Triggers that reference `Taskforce1Vessel1` still work after generation, because the
  generator fills the existing section names. Triggers referencing `Taskforce1Vessel4`
  will break if the player brought three ships.
- Missions in `campaign.ini` are entries in an **event timeline**, not just missions.
  `Type=FreeEvent` entries (news, intel documents) get numbered in the same
  `[MissionN]` sequence, so `NumberOfMissions=31` for ~11 playable missions. `Parents=N`
  wires the graph.
- `RequiredResult=CostlyVictory` gates progression.
- Awarding a `TaskForceModeRibbonAwards` ID that has no `[Ribbon_<id>]` definition in
  `commander_settings.ini` breaks the debrief. Ship no ribbons rather than broken ones.
- Vanilla missions have **no briefing XML at all** — they use `MissionIntro_en` in
  `campaign.ini` instead. Briefing panes are optional.

### Awarding units between missions — two different mechanisms

`TaskForceModeCompletionRewardedUnits=<alias>,<SquadronN>,<count>|...` on a `[MissionN]`
block **files everything it is handed as an aircraft**. Vanilla only ever hands it
aircraft (`04 Sunda Strait`, `09 Shadows off Palawan`). Give it a hull and the hull
turns up under the *Fixed Wing* tab in Task Force Builder.

So:

| Awarding a… | Use |
|---|---|
| vessel or submarine | `JoinTaskForce=True` on that unit's section in the mission `.ini` |
| aircraft, VTOL or helicopter | `TaskForceModeCompletionRewardedUnits` in `campaign.ini` |

**An awarded air wing needs three things or it silently evaporates at the debrief:**

1. the `TaskForceModeCompletionRewardedUnits` line that hands it over;
2. an entry in `[AllowedHelicopters]` / `[AllowedAircraft]` in
   `player_task_force_roster.ini` — that is *where an owned airframe lives*, and
   without a home the campaign drops it between missions;
3. `TaskForceModeIncludesAirwing=True` on every receiving `[MissionN]`.

`TaskForceModeAllowedRosterUnits` is **purchase gating only** — a unit that is in the
roster file but absent from that line is still owned and still deploys, it merely
cannot be bought. That is how vanilla and PhantomWake both hold awarded-but-never-
purchasable hulls.

`CustomAirGroup=True` on a vessel section, followed by bare `<alias>=<SquadronN>,<count>`
lines, sets that ship's embarked air group **for that mission only**. It does not award
anything. Every aviation-capable hull already has a default `[AirGroup]` block in its
unit file (`wp_ms_roro_b` defaults to 8× `wp_yak-38` + 2× Ka-25), which is what you get
if you omit `CustomAirGroup`. Deck limits live in `[FlightDeck]`: `AircraftCapacity`
(hangar + deck) and `DeckParkSlots`.

Related keys, all per-`[MissionN]`: `TaskForceModeAirbasePrepAvailable` /
`…PrepReadySlots` / `…PrepInProgressSlots` (how many flights start spun up), and
`TaskForceModeAirTaskingAvailable` + `TaskForceModeAirTaskingFlightN=<id>|<label>|<Role/Role>|<count>|<Loadout/Loadout>`
(pre-launched flights; roles come from `[AI] Role=`, §17). Vanilla only pairs airbase
prep with **land** airbases, and the one helicopter air-tasking flight it wrote is
commented out — neither is confirmed to work off a ship's flight deck.

---

## 15. Workflow

- Build geometry in the editor, then **stop opening the mission in the editor**. It
  recompiles and destroys hand-written triggers, `Disabled=True` flags, name overrides
  and everything in this document. Test from the scenario browser instead.
- `NumberOfTriggers`, `NumberOf<Side><Type>s`, `NumberOfSymbols`, `NumberOfZones` must
  match the actual section count or units silently vanish. Check them last, every time.
- Cheap validation before launching the game: confirm every `<Token>` in
  `ConditionsCompleted` has a matching `Condition_<Token>_Type`, every
  `Action_*_Message` key exists in `[Language_en]`, and every objective named in an
  `Action_Objectives*` exists in `[Taskforce1_Objectives]`.
- **Vessels and submarines can now be validated locally** — see §17. Aircraft,
  helicopters, land units and weapons still cannot, so `SquadronReference=` and
  aircraft `LoadoutVariant=` must come from vanilla campaign files or `.unitgroup`
  presets and be flagged as unverified.

---

## 16. The stopwatch unit — a real relative timer

**Status: untested in-game.** Every mechanic it is built from is verified
individually (§2B, §5, §3); the combination has not been run yet. Calibrate once
before trusting the numbers.

The engine has no relative-time condition, but it does have a clock: **units move**.
Park a unit far away with `Disabled=True`, spawn it on the event you want to time,
and gate on its arrival at a circle a known distance downrange. Arrival time is
`distance / speed` **after the spawning trigger fired**, which is exactly the relative
delay `Type=Time` cannot express.

```
delay_seconds = distance_NM / speed_kt * 3600
distance_NM   = speed_kt * delay_seconds / 3600
```

```ini
; The clock. A neutral airliner parked 300 NM off in an empty corner at 35,000 ft,
; where nothing will ever see it, shoot it, or wonder what it is. Vanilla already
; scatters civ_707s at that range as background traffic, so it reads as normal.
[NeutralAircraft1]
Type=civ_707
SquadronReference=Squadron8
Disabled=True
UnlimitedFuel=True
MissionType=NoMission
WeaponStatus=Hold
RadarsActive=False
CrewSkill=Trained
RelativePositionInNM=300,35000,300
Telegraph=3
Heading=180
Waypoints=300,35000,292|300,35000,285      ; 15 NM leg, two waypoints

; Start the clock
[Trigger9]
Name=Commandos on the deck - start the boarding clock
Condition_Boarding_Type=UnitsInTheArea
Condition_Boarding_PositionNM=-0.57,0,-4.46
Condition_Boarding_AreaRadiusNM=2
Condition_Boarding_Units=Taskforce2Helicopter1
ConditionsCompleted=<Boarding>
Action_Taskforce1_Message=Taskforce1BoardingMessage
Action_SetEnabledStatus=True
Action_Units=NeutralAircraft1

; The clock runs out - 15 NM at ~270 kt cruise = ~200 s after trigger 9
[Trigger10]
Name=Boarding clock expired - cargo lost
Condition_ClockDone_Type=UnitsInTheArea
Condition_ClockDone_PositionNM=300,0,285
Condition_ClockDone_AreaRadiusNM=1
Condition_ClockDone_AreaDisplaySide=None
Condition_ClockDone_Units=NeutralAircraft1
Condition_StillThere_Type=UnitsInTheArea
Condition_StillThere_PositionNM=-0.57,0,-4.46
Condition_StillThere_AreaRadiusNM=3
Condition_StillThere_Units=Taskforce2Helicopter1
ConditionsCompleted=<ClockDone> AND <StillThere>
Action_EndMission=True
Action_Victory=Taskforce2
```

`Action_DisableTriggers=Trigger10` from a "threat destroyed" trigger stops the clock.
Several independent stopwatches = several units. They can chain: one clock's arrival
spawns the next.

### Why this beats the alternatives

- The delay starts **when the event happens**, not at a time you guessed at authoring.
- It survives the player being slow, fast, or paused, because unit movement and trigger
  evaluation run on the same game clock and both scale with time acceleration.
- It is deterministic and repeatable — same distance, same delay, every run.

### Traps

1. **Use an aircraft, not a boat.** A ship spawns at rest and spends the first minute
   or so accelerating, so a short leg is badly non-linear and the delay comes out long.
   An aircraft spawns at cruise and is at speed from the first frame. If it must be a
   boat, calibrate empirically rather than trusting the arithmetic.
2. **Telegraph → knots is known for vessels, not for aircraft.** `units.py show`
   prints the exact per-telegraph speed table for any hull (§17), so a boat clock can
   be computed rather than calibrated. Aircraft are not indexed yet, so an airliner
   clock like the example above still needs one calibration run: note when the trigger
   actually fires and adjust the leg. It is deterministic, so once is enough.
3. **The clock unit is a real unit and it counts.** This is the sharp edge.
   `HasNoUnitsOfType` (§4) will see it, and so will any "destroy all enemy vessels"
   victory condition. Put the clock on a side or a `UnitType` you never test —
   a `NeutralAircraft` is safe when your checks are about `Taskforce2` `Vessel`s.
   It will also appear in the After Action Report.
4. **It must be unreachable.** Anything that can detect it can shoot it, and a dead
   clock means the trigger never fires. Far off-map, high altitude, `RadarsActive=False`,
   `WeaponStatus=Hold`, `UnlimitedFuel=True` so it never RTBs or flames out.
5. **Give it at least two waypoints.** The Civilian Routes section of the community
   guide warns that single-waypoint units path oddly, which would corrupt the timing.
6. **The player never sees the clock**, which is the point but also the cost: a
   countdown the player cannot watch is less tense than a threat closing visibly.

### When *not* to use it

If the thing being timed is already a moving object the player can see, **make that
object its own clock** — gate on the threat's position instead of a hidden proxy. That
is what `01_rusted_sea.ini` does: the assault helicopter flies a 25 NM run-in and the
player's four-minute window *is* its approach. Same determinism, no phantom unit, no
`HasNoUnitsOfType` pollution, and the player can watch the timer close on the display.

The stopwatch unit is for delays with no visible cause — a scuttling charge, a
reinforcement call, a boarding party already below decks.

---

## 17. Unit alias / variant lookup

A bad `Type=`, `VariantReference=`, `SquadronReference=` or `LoadoutVariant=` **fails
silently** — the unit never spawns, the roster entry never appears in Task Force
Builder, nothing is logged. Never guess these.

`share/` (git-ignored: `vessels`, `aircraft`, `land_units`, `biologic`, `ammunition`)
is flattened by `tools/build_unit_index.py` into four committed tables under
`docs/glossary/` — **549 units, 5489 variants, 1049 weapon mounts, 341 ordnance
types**. Query and validate with `tools/units.py`, packaged as the
**`sea-power-units` skill**, which has the full command reference.

```bash
python3 tools/units.py check <mission.ini>       # run after every mission edit
python3 tools/units.py show wp_ka-29             # variants, loadouts, role, speeds
python3 tools/units.py arsenal usn_dd_gearing    # weapon systems and magazines
python3 tools/units.py ammo --type Torpedo --target ASW
python3 tools/units.py search --type Helicopter --role Transport --year 1985
```

`check` walks every unit section and every `_WeaponSystemN` magazine override and
reports non-existent aliases, out-of-range variants, invalid loadouts, the
Variant/Squadron mix-up, unknown ammunition, and weapon system indices the hull does
not have. Exits non-zero.

What the data says that is not obvious:

- **Vessels, submarines, land units and biologics use `VariantReference=`; aircraft,
  helicopters and VTOLs use `SquadronReference=`** with `Default`/`SquadronN` sections
  in a `_squadrons.ini` sidecar. Same shape, different key. Mixing them fails silently.
- **Every unit has a `Default`.** Vanilla rosters never list it; it is still always
  valid in a mission unit section.
- **Variants and squadrons are cosmetic** — hull number, flag, emblem, livery,
  `Nation`, `ServiceDate`, occasionally `CustomAirGroup`. Never capability. Counts run
  1 to 144. Choose by nation and date.
- **`AvailableLoadouts` is the `LoadoutVariant` vocabulary**, under `[Cargo]` on
  civilians and `[WeaponSystems]` on warships and aircraft. No section → omit the
  field. Unlike variants, loadouts *do* change capability, and a hull may simply not
  have the one the design needs: `fr_sa-321` offers only `AntiShipPrecision,AntiShip,
  ASWKiller`, so it cannot be an unarmed boarding transport no matter how it is
  configured. `usn_ch-46` with `LoadoutVariant=Transport` can.
- **`[AI] Role=` is the Air Tasking `AllowedUnitRoles` vocabulary**: `Fighter`,
  `Bomber`, `HeavyBomber`, `Attack`, `MPA`, `ASW`, `ASuW`, `ESM`, `EW`, `AEW`, `SEAD`,
  `Recon`, `Targeting`, `Transport`, `SAR`, `Airliner`. Comma-separated per unit.
- **`TelegraphVelocities=` in `[Physics]` is the Telegraph → knots table**: seven
  values, `astern,stop,T1,T2,T3,T4,T5`, in knots. Only ~50 hulls override it (mostly
  submarines); the rest use an engine default not present in the files. In 48 of those
  50, **T5 equals `MaxForwardVelocity`** — the two Oberons are the exception, capped at
  15 kt on the telegraph against a 17 kt physics limit. "Flank ≈ max speed" is a safe
  planning assumption; the exact curve is there when it matters.
- **`ServiceDate` can be `1959|1973`** — build year and refit. Earliest = in service from.
- **Class names are not in the unit files.** They live in the game's localisation.
  Alias + nation + service date is the practical identifier;
  `campaigns/PhantomWake/FleetScoring/fleet.csv` is the local alias → class-name map.
- **No unit `.ini` has a `[TaskForce]` block**, so campaign point costs come from
  `fleet.csv` or the roster, never from the unit files.

Ammunition notes:

- `ammunition/` has **no variant sidecars** — one flat `.ini` per ordnance type, and
  341 of the 415 files are real ordnance. The rest are sub-components (`Propulsion`,
  `Fueltank`, `Antenna`, `Stabilizer`, `Afterburner`, `Radar`, `ECM`, `Container`)
  that are never a valid `AmmunitionN=` value, so the builder filters by `Type`.
- Ordnance `Type` values: `Missile`, `Torpedo`, `Bomb`, `Projectile`, `RBU`, `ASROC`,
  `AerialRocket`, `MLRS`, `Sonobuoy`, `Chaff`, `Noisemaker`, `MOSS`, `CIWS`,
  `AirDepthCharge`, `Paratrooper`, `LaserDesignator`. `TargetType` is `AAW`, `ASuW`
  or `ASW`.
- **Ranges are in nautical miles, velocities in knots** (`MinLaunchRange`,
  `MaxLaunchRange`, `MaxVelocity`), except gun `MuzzleVelocity`, which is m/s.
- `GuidanceType` and `WarheadType` are integers with legends buried in file comments;
  the glossary decodes them (`3` → `ActiveRadar`, `0` → `BlastFrag`, and so on).
- `AmmoPoints` is the supply-system cost of one round, not a campaign point cost.

Everything under `StreamingAssets/original/` that matters for mission authoring is
now indexed.

---

## 18. Enemy AI — what it will and will not do

Derived while debugging a mission the player could complete without firing a shot,
by sailing around everything. Every claim here is from the vanilla files or the
unit data; where it is inference it says so.

### There is no fleet-level AI. Detection does not re-task anything.

Sea Power's AI is **unit-level**: a unit follows its waypoints, and engages when it
personally has a valid detected target in range. There is no enemy commander that
notices the player and vectors groups at them. "The enemy spots me, so the enemy
sends its boats after me" **does not happen**, no matter how good the enemy's
sensors are. A shared contact only helps units that can already shoot that far.

Vanilla never relies on emergent pursuit. The one case of hostile ships changing
plan is scripted — `05 Strike on the Monster.ini` Trigger5, where the Kirov turns
north once its search aircraft are all dead:

```ini
Condition_Condition1_Type=UnitDestroyed
Condition_Condition1_Units=Taskforce2Aircraft3,Taskforce2Aircraft4,Taskforce2Helicopter1,Taskforce2Helicopter2
Condition_Condition1_MinimumUnits=4
Action_Units=Taskforce2Vessel1
Action_UnitWaypoints=-173.4142,220.4727,320.6888
```

So a `UnitDetected` → `Action_UnitWaypoints` re-vector is legitimate and
un-dodgeable (a detection is not a place). But `Action_UnitWaypoints` re-tasks to
**fixed coordinates**, so it is a one-time redirect to a guess, not a chase.
`04 Sunda Strait.ini` Trigger7 uses the same action on friendly aircraft.

### Telegraph is the throttle, and the default table is slow

This is the trap that eats scripted intercepts. `Telegraph=` is not a percentage of
max speed. About 50 hulls override `TelegraphVelocities` in `[Physics]`, and the
overwhelmingly common shape is **fixed absolute knots for T1–T4 with only T5
scaling to the hull's maximum**:

```
TelegraphVelocities=-7,0,5,10,15,20,35        ; astern,stop,T1,T2,T3,T4,T5
TelegraphVelocities=-5,0,5,10,15,20,24
TelegraphVelocities=-7,0,5,10,15,20,41
```

Hulls with no override use an engine default not present in the files, but the
override population strongly implies the same table. Practical rule:

| Telegraph | knots |
| 1 | ~5 |
| 2 | ~10 |
| 3 | ~15 |
| 4 | ~20 |
| 5 | max speed |

**`Telegraph=3` is 15 kt on a 48 kt torpedo boat.** The editor writes `Telegraph=3`
by default, so a hand-built pursuit force ships at 15 kt and cannot catch anything
faster than a freighter. Check the chase arithmetic against the *target's* speed,
not the hull's max, and use `Telegraph=5` or a `/SetTelegraph,5` waypoint command
on the run-in. `UnlimitedFuel=True` on anything expected to sprint.

### Small combatants are effectively blind

`tools/units.py show` gives max speed, but sensor fit needs the raw unit file.
`wp_pt_libelle`, a typical fast attack craft, carries:

```
[SensorSystem1] Type=Visual  Optics        VisualIdentificationRange~7.5
[SensorSystem2] Type=Radar   Nav_Radar
```

Optics and a navigation radar. No search radar, no ESM. A picket of these detects
nothing at 30–40 NM. If the design needs the enemy to *find* the player, something
on that side has to carry a real sensor — an MPA, an AEW aircraft, or an ELINT
platform whose track feeds the units that can shoot at range.

### Vanilla solves "the player can just sail around it" with geography

Survey of all 14 Pacific Strike missions by victory condition:

| Win condition | Missions |
| `UnitDestroyed` (kill something) | **10** |
| `UnitsInTheArea` (reach a point) | 4 |

The four that ask the player to reach a point are `03A Run Silent Run Deep`
(submarine, 0 land units), `03 Running the Palawan Passage` (8 coastal land units),
`04 Sunda Strait` (3), `09 Shadows off Palawan` (26). All are straits or coastal
transits where terrain and shore batteries do the containing.

**Vanilla never asks the player to cross open ocean to a point past a mobile
threat**, because mobile threats cannot seal open ocean. If a mission must do it,
the design has to supply the walls itself: a small win circle, screening groups
spread across the *crossing width* rather than converging on the direct line, and
enough speed on those groups to convert a detection into an engagement.

Useful geometry check before shipping such a mission — decompose every hostile
position into **along-track and cross-track** components relative to the
start→objective axis. Groups that look well spread on the map often turn out to
share one cross-track lane, which is a single tooth rather than a comb.

### `[Debug]` block: `DisableEnemyAIPlayer=True` is mandatory vanilla boilerplate

Not in either guide, not in `campaigns/pacific-strike-task-force/` — but check
`share/OriginalMissions/{Linear1,Molina}/*.ini` (the original 11-mission campaigns,
a separate source from the scraped pacific-strike set) and **every single one** opens
with:

```ini
[Debug]
DisableEnemyAIPlayer=True
```

11/11 files, no exceptions, no other key ever present in that block. This is not
optional flavor — it is load-bearing boilerplate every shipped mission carries.

Mechanism is **not documented anywhere** (no dev comment, no guide text), so treat
the following as a hypothesis, not a verified fact: the engine has an
operational/strategic AI layer above individual units (re-tasking task forces,
launching on its own initiative) and `DisableEnemyAIPlayer=True` turns that layer
off so the enemy sticks to the mission's scripted waypoints and triggers instead of
improvising. Per-unit "micro" behavior — point defense, decoy/chaff, ECM, weapons
engagement within `WeaponStatus=` — is presumed to keep running regardless, since
nothing in any file ties those systems to this flag, but that presumption is
untested. This is consistent with §18's top-level finding ("no fleet-level AI,
detection does not re-task anything") — the flag may simply be making explicit what
the engine barely does anyway at this scale.

`docs/examples_from_dev/MissionFileInformation.ini:17-36` documents a *different*
pair of `[Debug]` fields — `AllowEnemyUnitsAttackPlayer=False` (blocks the enemy from
attacking the player at all) and `EnemyWeaponStatus=Tight` (mission-wide override of
per-unit `WeaponStatus=`, §10). Neither appears in any of the 11 shipped missions
checked. They're real (dev-documented), just not what production missions actually
use — `DisableEnemyAIPlayer` is the one that matters in practice.

### `MissionType` — full vanilla vocabulary, corrected

Earlier version of this note only checked `campaigns/pacific-strike-task-force/`
(18× `Patrol`, nothing else) and wrongly treated other values as unattested.
`share/OriginalMissions/{Linear1,Molina}/*.ini` (11 more vanilla missions) has the
real spread:

```
44  NoMission
28  AntiSurface
12  Patrol
12  AntiAir
 1  AntiCarrier
 1  AntiShip
```

So `AntiSurface`/`AntiAir`/`AntiCarrier`/`AntiShip` are real, used values, not
guesses or invalid enums — PhantomWake's own use of `AntiSurface` (6×) is
unremarkable, not a risk. Pattern by mission shape: strike/ambush missions
(`04A/04B Bargaining Chips`, `05A/05B`) lean on `NoMission` + scripted `Attack=`
triggers (community guide, already documented) or narrow `AntiSurface`/`AntiAir`
taskings; recon/hunter missions (`01 Operation Shadow`, `02 Operation Revenge`) use
`Patrol` on the side that has to go find something.

Behavioral claim, still unverified by any doc or comment, only by usage pattern:
`NoMission` = hold position or run the waypoint route, react in place per
`WeaponStatus` but never leave the route to chase; `Patrol` = actively search,
allowed to break off waypoints to close on and prosecute a detected contact, then
resume. Fits `01 Operation Shadow.ini`: the USSR SAG (`Taskforce2`, 6 vessels) is
set `MissionType=Patrol` throughout, and the mission's own briefing frames it as
hunting the player's Norwegian submarines in the Barents Sea — a group that's
supposed to search needs `MissionType=Patrol`, not just `WeaponStatus=Free`, if this
distinction is real.