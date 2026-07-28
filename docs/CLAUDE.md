# Sea Power mission authoring — field notes

Things learned by reading the vanilla `pacific-strike-task-force` campaign that are
**missing from, or contradict**, `Mission_Creation_Community_Guide.md` and
`Task_Force_Campaign_Guide.md`. Everything below was verified against real files
under `campaigns/pacific-strike-task-force/`; where something is inferred rather
than confirmed it says so.

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

`UnitClassified` needs `_Taskforce=` (who did the classifying) as well as `_Units=`.

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
| `SetSelected=True` | unit selected when the mission opens |
| `CallsignIndex=` | picks a specific callsign from the unit's list |
| `TaskForceModeIgnoreUnit` | exempt a unit from generator replacement |
| `Nation=US` / `UK` / `china` | flag override on civilians — sells a false-flag merchant |

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

The ammunition ID is the game's own ammo file name and is not guessable — get it by
placing the unit in the editor, setting the stores there, saving, and reading back
what the editor wrote.

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
- Repo is missing `StreamingAssets`, so `Type=`, `VariantReference=`,
  `SquadronReference=` and `LoadoutVariant=` **cannot be validated here**. Source them
  from vanilla campaign files, `.unitgroup` presets, or the game's own unit `.ini`s,
  and flag anything guessed.

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
2. **Telegraph → knots is undocumented.** There is no published mapping for
   `Telegraph=0..5`. Run the mission once, note when the trigger actually fires, and
   adjust the leg length. One calibration pass is enough because it is deterministic.
   `Action_UnitVelocityInKnots` would remove the guesswork but is unverified (§5).
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
