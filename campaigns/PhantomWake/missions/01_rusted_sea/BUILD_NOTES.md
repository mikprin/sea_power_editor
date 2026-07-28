# 01 Rusted Waters — build notes

## Coordinate system

`MapCenterLatitude=12.35`, `MapCenterLongitude=44.00`.

```
X = (lon - 44.00) * 60      (+X = East)
Z = (lat - 12.35) * 60      (+Z = North)
```

No cosine-of-latitude correction — see `docs/CLAUDE.md` §1 for the proof.

## The convoy axis

Rebuilt onto the map markers **as you repositioned them**. All three of your markers
sit on one straight 110° line to within 0.2 NM, so the axis is exactly where you drew
it. `d` is distance in NM from the rendezvous.

| d | Point | X, Z (NM) | lat, lon | Source |
|---|---|---|---|---|
| -9 | MV Vagabond start | -21.028, 2.957 | 12.399286, 43.649535 | your `MapSymbol_New2` |
| 0 | Rendezvous | -12.510, 0.072 | 12.351196, 43.791505 | your `MapSymbol_New1` |
| 6.3 | Fishing grounds / ambush | -6.590, -2.083 | 12.315, 43.890 | abeam your `MapSymbol_New4` |
| 9 | Air raid trigger line | -4.053, -3.006 | 12.299900, 43.932450 | your `MapSymbol_New6`, moved |
| 13 | Air Threat Axis "B" | -0.294, -4.374 | 12.277, 43.995 | helicopter loiter |
| 17.8 | NavPoint Alpha | 4.128, -6.168 | 12.247200, 44.068800 | your `MapSymbol_New3` |

Deployment zone is yours unchanged: 16 × 7 NM at `12.271197 / 43.633711`.
Helicopter spawn is your `MapSymbol_New5` (`12.5163 / 44.0603`), 15 NM from B.

Player anchor is 8.1 NM from the rendezvous, the Vagabond 9.0 NM, both at
`Telegraph=4`, so they converge on the marker at about the same time.

## The dodge is closed — barrier instead of a circle

You were right: a single 2 NM circle for the helicopter gate could be sailed around.

Trigger conditions **cannot be rectangles** — `Kind=Rectangle` and `Shape=Rectangle`
exist for map symbols and zones only, and conditions accept nothing but
`AreaRadiusNM`. So your line is built as **seven overlapping 3 NM circles spaced 5 NM
apart on bearing 040 through d=9**, ORed inside trigger 6. Effective gate: 6 NM wide,
30 NM long, no gaps.

Geometry check against the convoy route (minimum distance from each gate centre to
every leg):

```
gate1 14.10 NM   clear
gate2  9.40 NM   clear
gate3  4.70 NM   clear
gate4  0.00 NM   HIT
gate5  4.70 NM   clear
gate6  9.39 NM   clear
gate7 14.12 NM   clear
```

Exactly one gate fires on the planned track, and the neighbours sit 4.7 NM off — which
is what catches a player who steers 5 NM wide to duck the raid. All seven are
`AreaDisplaySide=None`; `MapSymbol_New6` was moved onto d=9 so the drawn rectangle and
the real gate are the same line. Your bearing 40 is kept; width/length now match the
circle chain (6 × 30 NM instead of 4 × 200).

Pattern is written up in `docs/CLAUDE.md` §3 for reuse.

## EW is now much later, and only on the sector

Trigger 6 used to fire on `SkiffsDead OR Time=2100`, so killing the pirates quickly
pulled the whole third act forward. **The `SkiffsDead` and time conditions are gone** —
EW fires only when the convoy crosses the trigger line at d=9, which is 51% of the way
along the escort leg and unavoidable. The jamming popup now names the sector.

Trigger 7 (helicopter launch) is armed by trigger 6 and has **no conditions at all**,
so it fires the instant it is enabled. Split from trigger 6 only because `Action_Units`
is per-trigger and trigger 6 needs it for the Vagabond's sensors.

## Pirates: one group, south, no rockets

- One `Taskforce2_Formation1=Taskforce2Vessel1,Taskforce2Vessel2,Taskforce2Vessel3|Skiff Group|Loose|1.5`,
  all three sharing spawn `-7.64,0,-7.02` — the formation spreads them. Back to
  `ir_fab_boghammar` as you had it.
- Lying up **5 NM south of the track at d=7**, clear of the fishing cluster, and
  breaking north-east across the convoy's bow when it reaches d=6.3.
- **Rocket pods emptied**, using the syntax from your file:

```ini
[Taskforce2Vessel1_WeaponSystem1]
Ammunition1=ir_107mm_rocket
Ammunition1_Count=0
```

  This was the useful find of the round — the Task Force guide mentions "Stores Editor
  container overrides" but never gives the syntax, and no vanilla mission uses it.
  Now documented in `docs/CLAUDE.md` §10.
- The two neutral decoy Boghammars carry the same override, so a mistaken
  identification is never lethal.

**Triggers 4, 5, 10, 11 and the victory chain all still reference
`Taskforce2Vessel1..3`**, so the regrouping changed nothing they depend on — checked,
not assumed.

## Naming MV Vagabond

Three belts, since the editor drops the rename on save:

```ini
NeutralVessel1NameOverride=MV VAGABOND
NeutralVessel1ShortNameOverride=VAGABOND
Neutral_Formation1=NeutralVessel1|MV VAGABOND|Loose|1.5
```

The one-ship Neutral formation is the sturdy one — formation labels survive an editor
round-trip, name overrides do not. She also transfers to `Taskforce1` at the
rendezvous, so from that point she is a blue contact the player can con directly.

## Helicopter task is hidden until contact

`DestroyCommandoHelo=25,-25,Complete,Hidden`, revealed by
`Action_ObjectivesUnHide=DestroyCommandoHelo` on the air-contact trigger. Dropped the
`Main` tag: `Main,Hidden` together is not demonstrated anywhere in vanilla and may not
parse.

## Not fixed, on purpose

The MD500 escort now sweeps southwest down the trigger line, so a convoy trying to slip
past to the south still gets found. But the **boarding** check is still a circle pair at
B (helicopter within 2 NM, convoy within 4 NM) — a player who detours the Vagabond more
than 4 NM around B avoids the boarding entirely. That costs real distance and time and
leaves the helicopter alive and the objective failed, so it reads as a legitimate
choice rather than an exploit. Making it unavoidable would need paired circles per
barrier segment and parenthesised `ConditionsCompleted`, which vanilla never uses.

## Timing estimate

At `Telegraph=4` (~17 kt assumed): rendezvous ~32 min, ambush ~45 min, trigger line
~55 min, boarding ~72 min, Alpha ~95 min. Every gate is positional, so a different
Telegraph-to-knots mapping changes the pacing but not the order or the correctness.

## Deviations from SCRIPT.md

1. **Gulf of Aden, not Gulf of Guinea.** Every coordinate and both `.unitgroup` presets
   are at 12°N / 43–47°E and the preset units are Iranian and French/Iraqi. All text
   written to match.
2. **Escort leg is 17.8 NM**, set by where you put NavPoint Alpha.
3. **The skiffs are hostile from mission start**, idling at Telegraph 1. Avoids
   green→red `Action_UnitTransferToTaskforce`, which vanilla never demonstrates.
   (Green→blue, which the Vagabond uses, is the mirror of the blue→green case vanilla
   does demonstrate.)
4. **No literal 200-second countdown.** No relative-time condition exists — see
   `docs/CLAUDE.md` §2. The window comes from the helicopter's approach geometry.

## Editor limits hit

- **No relative timers.** `Type=Time` is always absolute from mission start.
- **No rectangular trigger areas.** Hence the circle chain above.
- **Area conditions are static circles, never distance-to-unit.** Hence the
  two-condition AND pattern on triggers 9 and 10.
- **No jamming action.** Popup + intel + a real
  `Action_EnableDisableSensorSystems=Disable` on the Vagabond, with an EA-6B orbiting
  at 30,000 ft as the source.
- **`Action_Units` is per-trigger, not per-action.**
- **Unit references cannot be validated here.** StreamingAssets is not in the repo.

## Needs verifying against the game files

| Field | Value | Note |
|---|---|---|
| `ir_107mm_rocket` | ammo ID in the `_WeaponSystem1` blocks | from your editor-generated file, so this one is solid |
| `ir_fab_boghammar` | `VariantReference=Default` | from your file |
| `fr_sa-321`, `iqaf_md500` | `SquadronReference=Default` | presets carry no squadron info |
| `fr_sa-321` | `LoadoutVariant=Empty` | from the preset; unarmed transport |
| `iqaf_md500` | `LoadoutVariant=Recon` | from the preset |
| `usn_ea-6b` | `SquadronReference=Squadron6` | from the vanilla campaign reward list |
| `civ_ms_c7s68` | `Variant19` + `LoadoutVariant=Containers` | copied from vanilla Okinawa. Your file had `Default` — if `Variant19` misbehaves, switch it back |
| `ir_pf_bayandor` | `Variant1` | anchor only, generator replaces it — low risk |
| roster variants | `Variant1` except `usn_dd_gearing` | **matters** — a bad variant means the hull never appears in Task Force Builder |
| `Action_UnitTelegraph`, `Action_UnitVelocityInKnots` | trigger 4 | documented in the community guide, unused in vanilla; both set for redundancy |
| `Kind=Rectangle` + `Bearing=` | `MapSymbol_New6` | your editor wrote it; vanilla only uses `Kind=Oval` with `RadiusXNm` |

## Not built

- Briefing XML panes — vanilla uses `MissionIntro_en` in `campaign.ini` instead.
- Ribbons and medals — need art, and an undefined ribbon ID breaks the debrief.
- Localisation. English only.
