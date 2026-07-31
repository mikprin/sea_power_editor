# 02 Pandora's Box — build notes

Mission file: [02_pandoras_box.ini](../02_pandoras_box.ini)
Script: [SCRIPT.md](SCRIPT.md)
Hand-built backbone: `share/02_pandoras_box.ini`
Briefing: [02_pandoras_box_briefing/](../02_pandoras_box_briefing/)
Campaign entry: `[Mission5]` in [campaign.ini](../../campaign.ini)

**13 triggers, 5 objectives, 27 hostile vessels, 3 aircraft. One positional
condition in the entire file.**

Full `en` + `ru` localisation — every popup, intel line, forecast, objective,
ship name, map label and both briefing panes exist in both.

---

## The rewrite, and why

The first build gated every event on a circle drawn across the convoy lane.
**Playtest killed it outright.**

Those circles are rendered to the player on the tactical map. The player saw
three red discs labelled EW CONTACT ZONE, HOSTILE INTERCEPT ZONE and MISSILE
THREAT ZONE, steered ten miles south of all three, sailed the length of the map
and entered the delivery circle from the south-east. **Contract complete, not a
shot fired, not one popup seen.**

Two separate mistakes, both mine:

1. **The tripwires were drawn for the player.** `AreaDisplaySide=Blue` on a
   gate condition is an instruction to route around it.
2. **The enemy did not exist.** Everything hostile was `Disabled=True` waiting
   on a gate, so avoiding the gate avoided the mission.

That also explains the reported "intel messages don't show" bug. Nothing was
wrong with the keys or the strings — every `Action_Taskforce1_Intel` resolved
correctly in both languages. The triggers simply never fired.

### What replaced it

**Everything hostile now exists at t=0 and moves on its own route**, on the
positions, headings, telegraph settings and waypoints laid out by hand in the
editor backbone. Nothing is `Disabled=True` except the two strike helicopters.

All three Hound pack routes terminate in the player's start area, so the packs
close on the convoy wherever the convoy actually is. There is no course that
avoids them because they are hunting, not waiting. The southern detour that
broke the first build now sails straight into pack two, which starts at
`(42.23, -84.7)` — south-east of everything.

**Narrative triggers use `UnitDetected`, not `UnitsInTheArea`.** A radio call
fires when the player's sensors actually acquire the thing being talked about,
wherever that happens. It cannot be walked around because it is not a place.
Verified pattern, already used in `01A_sweeping_net` Trigger3 and Trigger7:

```ini
Condition_HoundsSeen_Type=UnitDetected
Condition_HoundsSeen_Taskforce=Taskforce2
Condition_HoundsSeen_Units=Taskforce2Vessel1,...,Taskforce2Vessel12
Condition_HoundsSeen_MinimumUnits=1
```

**One positional condition survives** — Trigger12, the win circle. That one is
the objective, so the player is supposed to steer to it, and it is the only
thing this file draws on the tactical map.

Trigger inventory after the rewrite:

| Type | Count | Triggers |
|---|---|---|
| `UnitDetected` | 5 | 3, 4, 5, 6, 7 |
| `UnitDestroyed` | 4 | 8, 9, 10, 11 |
| `Time` | 2 | 1, 2 (+ deadline arm on 5 and 6) |
| `HasNoUnitsOfType` | 1 | 13 |
| `UnitsInTheArea` | **1** | 12 — the win |

---

## Geometry — the hand-built layout, preserved

Map centre `19.92 / 67.88`, unchanged. Open water, no land in the playfield.

```
X = (lon - 67.88) * 60      Z = (lat - 19.92) * 60
```

Every hostile position, heading, telegraph and waypoint below is transcribed
verbatim from `share/02_pandoras_box.ini`.

| Element | NM | Notes |
|---|---|---|
| Deployment box | X −12..8, Z −73.7..−23.7 | hand-placed, 20 × 50 |
| MV Pandora start | (−4.58, −45.14) hdg 113 | hand-placed |
| Pandora route | → (21.48, −56.22) → (67.35, −77.37) | hand-drawn, 78.8 NM |
| Handover circle | (67.35, −77.37) r=40 | centre moved onto WP2, radius as placed |
| Pack one | (60, −57) → (38.57, −60.85) → (2.52, −43.03) | 59 NM run-in |
| Pack two | (42.23, −84.7) → (36.72, −64.56) → (−1.45, −47.74) | 57 NM run-in |
| Pack three | (69.48, −59.64) → (40.51, −64.26) → (−2.03, −44.95) | 73 NM run-in |
| Support group | (53.36, −76.24) → … → (−0.35, −54.54) | hand-drawn, runs west into the convoy's water |
| Jammer | (110.52, 20000, 92.27) + hand-drawn orbit | `Loop` appended |

Only two things changed:

- **Pandora `Telegraph` 4 → 5**, so the passage runs at her 20 kt maximum
  rather than about 16.
- **`Loop` appended to the jammer's waypoint list**, so it works the sector
  instead of flying off the end of the last leg.

### Runtime — the marker was moved, deliberately

The handover marker originally sat at `(101.76, −94.97)`, which put the circle
edge **77.5 NM** down the route — **3 h 52 m** at the Pandora's twenty knots,
of which the last two hours were empty ocean with the fight long finished.

The centre is now the **Pandora's own second waypoint**, `(67.35, −77.37)`,
with the hand-placed r=40 untouched:

```
leg 1  start -> WP1                28.32 NM
leg 2  WP1 -> circle edge          10.51 NM   (WP1 is 50.51 NM from the centre)
                                   -------
                                   38.82 NM   = 1 h 56 m at 20 kt
```

Steering direct instead of via the waypoint is also 38.82 NM, so there is no
corner to cut. The crossing point falls at NM `(31.0, −60.6)`, which is 27 to
39 NM from every hostile start — the packs have closed long before the player
gets there, and pack three is likely still inbound when the line is crossed.

Shape of the mission now: **~1 h approach, ~1 h fighting, cross the line while
still in contact.**

`MapSymbol_New1` and `Trigger12` must stay in step; the validation script
asserts they agree in both position and radius.

---

## Design decisions kept from the previous build

### The ARAPAHO is `Taskforce1Vessel3`

The backbone had the RO-RO as the only `Taskforce1` vessel, which in a
`Generated` mission makes it the anchor — and the generator discards the
anchor's `Type`, so the escorted ship would not have existed. Layout is the
vanilla `09 Shadows off Palawan` shape:

```ini
[Taskforce1Vessel1]  TaskForceModeAnchor=True           ; generator seed
[Taskforce1Vessel2]  TaskForceModePlaceholderUnit=True  ; removed at launch
[Taskforce1Vessel3]  TaskForceModeIgnoreUnit=True       ; author placed, kept
```

Awarded by `JoinTaskForce=True` on the section, **not**
`TaskForceModeCompletionRewardedUnits` — that field files everything it is
handed as an aircraft, which is how the 01C Foxtrot landed under the Fixed Wing
tab.

### The Hounds really do carry torpedoes

`arsenal wp_pt_libelle` reports only the 23 mm ZU-23 because the tool lists
mounts by magazine. The raw unit file has three weapon systems — two OTA-53
533 mm tubes firing `wp_53-38`, plus the gun. The tubes carry their round
directly with no `AssociatedMagazine`, which is also why they cannot be
magazine-overridden.

`wp_53-38`: **5.5 NM, 34 kt, guidance None.** Straight runners, so the packs
must close to a few miles. 35 t hull, 48 kt flat out.

### The decoys are real unmanned target boats

`usn_septar_qst-35` is the game's SEPTAR — an 18 m unmanned radio-controlled
target the US Navy actually shoots at. `units.py` reports *"carries no
ammunition"*: no weapon systems at all, so they cannot fire under any
circumstance.

Twelve of them, **salted through the three Hound approach lanes and present
from t=0**, not spawned as a swarm. Twenty-four small contacts converging out
of a jamming envelope, half of them nothing. Only remote tell is speed —
SEPTAR tops out at 20 kt against the Libelle's 48 — which is exactly what
E.C.H.O. offers the player. An aircraft overhead is the other way.

### Two anti-ship missiles, for a story reason

The Syndicate came to **seize** the Pandora before her title transferred, not
to sink her; missiles were prohibited under that order because you cannot
capture a hull you have sunk. Meridian's lawyers signed an hour early, the plan
collapsed, and the order was reissued as **denial**. The two airframes already
airborne launched rigged for a boarding escort and now carry whatever could be
hung on them:

| Airframe | Loadout | Weapon | Range |
|---|---|---|---|
| Helicopter1 | `AntiShipPrecision` | 2 × `fr_am-39` Exocet | 35 NM |
| Helicopter2 | `AntiShip` | 2 × `fr_e15` aircraft torpedo | 6.5 NM |

They are the only `Disabled=True` units in the file, launched by Trigger6 on
`<LeaderSeen> OR <Deadline 5400>` — so the strike lands relative to the fight
for any player who has made contact, and still lands for one who somehow has
not. They fly in from off the player's plot, which is the one place a launch
event is honest.

---

## Campaign wiring

`[Mission5]`, `NumberOfMissions=5`. `Parents=1`, `MissionType=Main`,
`RequiredResult=CostlyVictory`. Threat profile ship 4 / air 3.
`TaskForceModeCompletionPoints=90`, `CapPoints=50`.
`TaskForceModeDeploymentOptions=True` + `DefaultDisposition=Formation`.

`player_task_force_roster.ini` carries `wp_ms_roro_b=Variant2|120` under
`[AllowedVessels]` so the awarded hull has a roster entry to live in — absent
from every `TaskForceModeAllowedRosterUnits` line, so never purchasable.

All "NavPoint Keystone" and "transit lane" wording removed from `campaign.ini`
in both languages; the passage is now described honestly as a long crossing
with no route around the opposition.

---

## Briefing

At [02_pandoras_box_briefing/](../02_pandoras_box_briefing/), found by
folder-name convention with no ini keys, same as vanilla and as 01C.

Chat-log format per IDEA.md, with ATLAS / SIREN / E.C.H.O. in
`NTDS.FriendColour` and FAIRWAY in `NTDS.HostileColour`. A **COMPANY STATUS —
STAGE TWO** block above the transcript carries the campaign arc: Stage 1
closed, E.C.H.O.'s origin off MV Vagabond named for the first time, the
Syndicate named, and the closing line setting up what the reward changes.

Two period photographs down the right edge as vanilla-pattern pinned insets
(white border, drop shadow, small rotation — copied from
`05 Strike on the Monster`):

- **ATLANTIC CONVEYOR, 1982** — the ARAPAHO concept proven in the Falklands,
  *"Sunk by a single air launched Exocet."*
- **AGOSTINHO NETO, 1984** — Yak-38M off a commercial container deck,
  *"The idea is not new. It has simply never been for sale."*

Base map regenerated for the full passage: `840 × 600 px = 140 × 100 NM at
6 px per NM`, covering NM X −20..120, Z −120..−20. The southern extension is
needed because the 40 NM handover circle reaches down to Z −117.

```
Canvas.Left = (X_nm + 20) * 6      Canvas.Top = (-20 - Z_nm) * 6
```

The handover circle is drawn at true scale, all 40 NM of it, because its size
is information — it is an area of international water, not a pinpoint. The
crossing mark on the track is annotated with its 38.8 NM range. The old
transit-lane rectangle and the three gate labels are gone; they described
tripwires that no longer exist.

Format notes: vanilla ships PNG only (38 assets, zero JPG), so the supplied
JPGs were converted. `Intel_ship2.jpg` had a Russian caption baked into its
margin; the photo block was auto-detected and cropped so each pane supplies its
own caption per language. Originals left in the folder, safe to delete.

---

## Validation

```
python3 tools/units.py check campaigns/PhantomWake/missions/02_pandoras_box.ini
-- 36 unit section(s) checked, 0 problem(s)
```

Scripted checks, all clean:

- every `<Token>` has a matching `Condition_<Token>_Type`, none unused
- every message / intel / forecast key resolves in **both** `[Language_en]` and
  `[Language_ru]`
- every objective actioned exists, has text in both languages, and every
  defined objective is actioned somewhere
- every `Action_Units` entry, formation member and `UnitDetected` unit list
  names a real section
- both `Disabled=True` units are enabled by exactly one trigger, and nothing
  else is targeted by `Action_SetEnabledStatus`
- every `Action_VariableSet` name declared in `[CampaignVariables]`
- all `NumberOf*` counts match real section counts
- `en` / `ru` key parity modulo the intentional label suffixes
- **exactly one positional condition in the file** (asserted, not assumed)
- all four briefing panes parse; every resource key and `{Token}` verified
  present in vanilla; all three assets resolve; no stale KEYSTONE / TRANSIT
  LANE / gate wording anywhere

---

## Open items for playtest

1. **Runtime.** ~1 h 56 m to the line at 20 kt, with first contact around the
   one hour mark. If the fight consistently outlasts the crossing and that
   feels anticlimactic, the lever is the radius: 40 → 25 pushes entry out to
   ~54 NM (~2 h 40 m) without moving the marker.
2. **`UnitDetected` against a large unit list.** 01A uses it against four
   units; here the decoy condition lists twelve and the Hound condition lists
   twelve. If a long list misbehaves, split into per-pack triggers.
3. **`Generated` + `TaskForceModeIgnoreUnit` + `JoinTaskForce` together.** Each
   half has vanilla precedent, the combination is new. Fallback is switching
   Mission5 to `Replaced` with `TaskForceModeReplacedUnitIndex`, as `08 Defense
   of North Borneo` does.
4. **`Action_EnableDisableSensorSystems` on a player-owned hull.** Mission 01
   did this to a Neutral; here it targets a ship the player owns from second
   one. If ignored, the decoy swarm still carries the phase.
5. **`Attack=` on vessel and helicopter sections.** Community-guide only,
   absent from all of Pacific Strike. Degrades to an ordinary engagement.
6. **Twenty-four surface contacts plus the support group.** Performance and
   clutter unmeasured. Dial is decoy count; nothing depends on an individual
   drone.
