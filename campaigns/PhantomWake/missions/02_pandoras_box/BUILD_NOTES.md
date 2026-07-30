# 02 Pandora's Box — build notes

Mission file: [02_pandoras_box.ini](../02_pandoras_box.ini)
Script: [SCRIPT.md](SCRIPT.md)
Editor backbone it came from: `share/02_pandoras_box.ini`
Campaign entry: `[Mission5]` in [campaign.ini](../../campaign.ini)

**13 triggers, 5 objectives, 31 hostile vessels, 3 aircraft, 4 phases.**
For comparison: 01 is 15 triggers, 01A 8, 01B 13, 01C 9.

First mission in the campaign with **full `en` + `ru` localisation** — every
popup, intel line, forecast, objective, ship name and map label exists in both.

---

## Geography

Map centre unchanged from the backbone: `19.92 / 67.88`, open water in the
central Arabian Sea. No land anywhere in the playfield, so unlike 01C there was
no coastline to sample against and no positions to correct.

```
X = (lon - 67.88) * 60      Z = (lat - 19.92) * 60
```

Convoy axis is the backbone's own: bearing **113** from the Pandora's start at
`(-4.58, -45.14)`, which is exactly where and how the editor had her.

| d (NM) | position | what happens |
|---|---|---|
| 0 | (-4.58, -45.14) | MV Pandora start |
| 10 | (4.63, -49.05) | **Gate A** — jamming, Pandora blinded, decoy swarm spawns |
| 20 | (13.83, -52.95) | **Gate B** — three Hound packs released |
| 22 | (15.67, -53.74) | **Trigger13** — FAIRWAY's decrypt, r=3, fires at d=19 |
| 30 | (23.04, -56.86) | **Gate C** — the improvised strike |
| 36 | (28.56, -59.20) | **NavPoint Keystone**, r=6 — victory |

### The one geometry change that mattered

The backbone's delivery circle sat at `(101.8, -95.0)`, **117 NM** from the
start. `wp_ms_roro_b` tops out at 20 kt, so that is a **four hour** mission with
three scripted events in it and an hour of empty ocean between each.

Axis and bearing are untouched; only the length was cut. 36 NM authored, 30 NM
effective because the Keystone circle catches her early — **about 90 minutes at
her flank speed**, in line with 01C. No time limit, same as 01, 01A and 01C.

Deployment box also shrank, 20×50 → 20×20 centred at `(-6, -45)`. The original
was tall enough to let a player deploy 25 NM astern of the ship they are
supposed to be screening.

---

## Script → implementation decisions

### The ARAPAHO is `Taskforce1Vessel3`, not `Taskforce1Vessel1`

The backbone had the RO-RO as the only `Taskforce1` vessel. In a `Generated`
mission that hull **is the anchor**, and the generator throws away the anchor's
`Type` and `VariantReference` — the escorted ship would simply not have existed.

The layout used instead is copied straight out of vanilla
**`09 Shadows off Palawan`**, which is `Generated`, has a player force of unknown
size, and still carries four hand-placed amphibs:

```ini
[Taskforce1Vessel1]  TaskForceModeAnchor=True           ; generator seed
[Taskforce1Vessel2]  TaskForceModePlaceholderUnit=True  ; removed at launch
[Taskforce1Vessel3]  TaskForceModeIgnoreUnit=True       ; author placed, kept
```

So `Taskforce1Vessel3` survives generation and its section name is safe to point
triggers at. Only `Vessel1` and `Vessel3` are referenced anywhere in the file, so
the player may bring as many hulls as they can afford.

### How the ship joins the fleet

`JoinTaskForce=True` on the mission unit section, **not**
`TaskForceModeCompletionRewardedUnits` in `campaign.ini` — the lesson from 01C,
where that field filed a submarine under the **Fixed Wing** tab because every
vanilla use of it is an aircraft.

Vanilla precedent for a *vessel* joining this way is
`08 Defense of North Borneo`, `[Taskforce1Vessel4] usn_avp_barnegat_mod` with
`JoinTaskForce=True` and a `CampaignTag`. Same shape here, plus
`CampaignRepair=True` so she can be repaired between contracts.

`player_task_force_roster.ini` gained `wp_ms_roro_b=Variant2|120` under
`[AllowedVessels]` **only so the awarded hull has a roster entry to live in** —
deliberately absent from every `TaskForceModeAllowedRosterUnits` line, so it is
never purchasable. Identical treatment to the Foxtrot. The roster variant and
the mission's `CampaignTag=wp_ms_roro_b_Variant2` have to agree, and do.

### The air wing fits

`wp_ms_roro_b` has `Role=CVL` and `AircraftCapacity=10` in its unit file. The
script's eight airframes fit with two slots spare, so the `CustomAirGroup` block
is used verbatim from SCRIPT.md.

`ReadyUpTime` is **15 minutes** on every loadout of all five types. That is the
single most important number in the mission and it is why E.C.H.O. opens with a
deck-readiness advisory and why the campaign's `MissionSpecialNote` repeats it.
Gate A is ~30 minutes in, so a player who launches at t=0 has aircraft up before
the first contact; a player who waits for the jamming message gets them at
roughly the same moment the Hounds arrive.

### The Hounds really do carry torpedoes

`tools/units.py arsenal wp_pt_libelle` only reports the 23 mm ZU-23, which looks
like it contradicts the script. It does not — the tool lists mounts *by
magazine*, and the raw unit file has three weapon systems:

```
WeaponSystem1  OTA-53_533mm torpedo tube   Ammunition=wp_53-38
WeaponSystem2  OTA-53_533mm torpedo tube   Ammunition=wp_53-38
WeaponSystem3  23mm ZU-23                  2400 rounds
```

The tubes carry their round directly rather than through an `AssociatedMagazine`,
which is also why they **cannot be magazine-overridden** the way the Boghammar
rocket pods were in Mission 01.

`wp_53-38`: **5.5 NM, 34 kt, guidance None.** Straight runners. The pack has to
close inside a few miles to have any chance, which is what turns the phase into
a knife fight rather than a standoff. Hull is 35 t and 48 kt flat out.

### The decoys are real unmanned target boats

`usn_septar_qst-35` is the game's **SEPTAR** — a Seaborne Powered Target, an
18 m unmanned radio-controlled boat the US Navy actually shoots at.
`tools/units.py` reports *"carries no ammunition"*: it has no weapon systems at
all, so unlike the empty-magazine Boghammars these **cannot fire under any
circumstance** and need no override. `WeaponStatus=Hold` and
`OverrideWeaponStatus=Hold` are belt and braces.

Sixteen of them against twelve real Hounds — 28 small fast returns inside a
jamming envelope, 57% of them fake. Two ways to tell them apart:

- **Speed.** SEPTAR tops out at 20 kt, the Libelle at 48. That is exactly the
  discriminator E.C.H.O. offers in the Phase 2 popup, and it is a discoverable
  skill rather than a handout.
- **Visual identification from the air**, which is the one the script wants.

`RandomSpawnRange` scatters every drone on every run, so memorising the layout on
a second attempt buys nothing. Telegraph is mixed 4/10 kt and 5/20 kt so the
swarm does not read as one machine-generated block — SEPTAR is one of the ~50
hulls that author `TelegraphVelocities`, so those speeds are exact rather than
inferred.

### Jamming is implemented twice, on purpose

1. **Mechanically** — `Action_EnableDisableSensorSystems=Disable` on the Pandora
   at Gate A. Same treatment the Vagabond got in Mission 01.
2. **Practically** — the decoy swarm *is* the jamming. Blinding the player's own
   warships with a switch would be unrecoverable and miserable; polluting their
   radar picture with 28 identical contacts is the same experience with agency
   in it.

The escorts keep their sensors throughout. Only the unarmed ship goes blind.

### Killing the jammer is worth something

`usn_eka-3b` at 25,000 ft on a racetrack 40–50 NM east of the lane, radars off,
empty loadout. Unlike the EA-6B in Mission 01 this one is **reachable** — a
Harrier on `AirToAir` can get to it, and Trigger6 restores the Pandora's sensor
suite when it dies.

That is the reason the air wing carries two AV-8As, and the reason the jammer is
a hidden objective instead of scenery. `Nation=us` is kept from the backbone and
deliberately unexplained.

### The missile problem, and how the fiction solved it

The first draft gave both Super Frelons `LoadoutVariant=AntiShipPrecision` — 2 ×
`fr_am-39` Exocet each, **four missiles**, against a roster in which *nothing*
carries a surface-to-air missile. That was flagged as the number one balance
risk, with a mechanical dial as the fallback.

**Miksolo replaced the dial with a story**, and it is a much better fix:

> The Syndicate was never sent here to sink the Pandora. The tasking order was
> **SEIZURE** — board her, take her, and let Meridian's creditors write the
> technology off as an asset that was never delivered. Anti-ship missiles were
> *explicitly prohibited* under that order, because you cannot capture a hull you
> have put on the bottom. Meridian's lawyers signed the title over an hour ahead
> of schedule, the player got there first, and the order was reissued as
> **DENIAL**. Everything now flying is hanging whatever could be found on
> airframes that launched rigged for a boarding escort.

So the missile scarcity is not a difficulty setting, it is **the consequence of
the player winning a race they did not know they were in**. Implemented as:

| Airframe | Loadout | Weapon | Range |
|---|---|---|---|
| `Taskforce2Helicopter1` | `AntiShipPrecision` | 2 × `fr_am-39` Exocet | 35 NM |
| `Taskforce2Helicopter2` | `AntiShip` | 2 × `fr_e15` aircraft torpedo | 6.5 NM |

**Two anti-ship missiles in the whole mission**, down from four. The second
airframe now has to run inside 6.5 NM of the ship it is trying to kill, in front
of the escorts — a visible, beatable, dramatic threat instead of another pair of
sea skimmers appearing on the horizon.

Both spawn over 40 NM out, outside even Exocet range on purpose, and close at
134 kt. That transit is the player's warning and the Harriers' window.

Both `Attack=` lines name the Pandora, matching the reissued order and matching
what E.C.H.O. announces. Helicopter2 attacks off `wp_2` rather than `wp_1`
because it has to be far closer before its weapon is in range at all.

### Trigger13 — FAIRWAY's decrypt

The intercept is delivered as its own beat, `Trigger13`, at d=22 with a 3 NM
radius so it fires at **d=19** — after Gate B has put the Hounds in the water at
d=15, before Gate C launches the helicopters at d=25. About ten minutes of
warning at the Pandora's twenty knots.

It does three things at once:

1. Explains why there are only two missiles, in-fiction, before the player has a
   chance to wonder.
2. Delivers real tactical intel — *one* airframe shoots from 35 NM, the other
   must come inside 6.
3. Lands the campaign beat: ATLAS gets *"we beat them to her by about sixty
   minutes. That is all. Sixty minutes."*

`AreaDisplaySide=None`, so no circle is drawn. The player is not navigating to
it, and a third blue circle on the lane would clutter the plot. Sets
`02SeizureOrderIntercepted` for later missions to read.

The same reveal is seeded earlier in the briefing, where FAIRWAY reports the
seizure order as *current* — so on the tactical map the player already knows
missiles are prohibited, and Trigger13 is the moment that stops being true.

### The support group is deliberately out of reach

Sacramento + T2 tanker + Baleares, holding a slow racetrack 35–40 NM southeast
of the lane. The Baleares carries `usn_rim-66b` out to 25 NM, so parked where it
is the group **cannot** reach the convoy — the player is never sniped by
something they were not told about. Going after it is a choice, and a hidden
bonus objective.

### The "don't lose an escort" objective is scoped to the flagship

The script's third objective is *"не потерять ни одного корабля из эскадры
прикрытия"*. The player's ships past the anchor are generated and the mission
file cannot know their section names, so there is no way to write a condition
that covers them. `Taskforce1Vessel1` is the one hull guaranteed to exist after
generation, so `EscortIntact` is scoped to it.

Honest and always evaluable, rather than an objective that silently never fires.

---

## Structural notes

- **Every gate is positional, never a clock.** A player who runs the Pandora at
  flank meets the Hounds sooner; one who creeps meets them later with more time
  to get aircraft up. Pacing follows the player.
- **Phase overlap is intentional.** The three packs need ~30 min to close from
  Gate B; the Pandora covers Gate B → Gate C in ~30 min at 20 kt. The missile
  strike therefore lands while the knife fight is still going.
- **`Trigger2` and `Trigger3` are one event split in two**, because
  `Action_Units` is per-trigger, not per-action (docs/CLAUDE.md §5). Trigger2
  needs it for the Pandora's sensors, Trigger3 for the 17-unit spawn list.
  Trigger3 has no conditions at all, so it fires the instant it is enabled (§2B).
- **Only pack leaders carry waypoints.** `Loose|1|OverrideSpawnPositions` brings
  the other three along — same pattern as 01C's interceptor pair.
- **Retreat anchor added.** Hounds run Morale 2–3 with
  `RetreatAfterWeaponsExpended=True`, so most will break once their two fish are
  gone. Anchored on the support group, which is where they came from.
- **Neutral merchants have no fail condition.** Three of them, texture only. This
  is a weapons-free contract and punishing a stray round in a swarm fight would
  be miserable.
- **Environment adjusted from the backbone**, both changes deliberate:
  - `Time` 21:00 → **19:00**. The script asks for "late evening, slightly reduced
    visibility"; 21:00 at this latitude in August is full dark, and the entire
    Phase 2 mechanic is visual identification from aircraft. Dusk degrades VID
    range without removing it.
  - `SeaState` 7 → **4**. Sea State 7 is a near gale — it would have crippled the
    35 t Libelles that are supposed to be the threat and grounded the player's
    own helicopters. 4 keeps the swell the script asks for without deleting both
    sides' toys.
- **`PopupStyle` uses only the four valid values** (`Intro`, `Notification`,
  `Outro`, `NavalMessage`). No `Message`, which the 01C notes established is not
  a real style.

---

## Localisation

`[Language_en]` and `[Language_ru]` are both complete: 11 popups, 5 intel lines,
the forecast, 5 objectives, 4 trigger area labels, 8 map and zone labels and 4
ship-name overrides each. The remaining seven language sections carry map and
zone labels in English, which is how vanilla ships partial coverage.

Two key conventions, both confirmed against vanilla `09 Shadows off Palawan`:

- **Map symbol and zone labels take the language suffix in the key itself** —
  `LabelKey=MapSymbol_New1Label` resolves to `MapSymbol_New1Label_ru`. This is
  the only class of key that differs between the `en` and `ru` blocks.
- **Everything else is looked up bare** inside the active `[Language_xx]`
  section — messages, intel, objectives, `NameOverride`, area labels.

Character tags are Cyrillic in the Russian text (`[АТЛАС]`, `[СИРЕНА]`,
`[ФАРВАТЕР]`) following IDEA.md, except `[E.C.H.O.]`, which stays Latin in both
because it is the AI's designation rather than a name.

`campaign.ini` `[Mission5]` also carries `_ru` for `Name`, `MissionSequenceName`,
`MapShortName`, `Description`, `MissionIntro`, `MissionResupplyRules`,
`TaskForceModeBuilderSituation`, `MissionSpecialNote` and both debrief notice
fields.

---

## Campaign wiring

`campaign.ini` gained `[Mission5]`, `NumberOfMissions=4 → 5`.

- `Parents=1`, `MissionType=Main`, `RequiredResult=CostlyVictory` — the second
  story contract, hanging off Mission 01 alongside the three optionals.
- Threat profile: ship 4, air 3.
- `TaskForceModeCompletionPoints=90`, `CapPoints=50`. Higher than 01's 70
  because this is a heavy escort action, and the fee is a hull the player could
  never buy.
- `TaskForceModeIncludesAirwing=False` — display only, and correct going *in*:
  the player still owns no air units, the eight airframes belong to the escorted
  ship. That is what changes after this mission.
- Roster subset identical to Missions 1–4. Kept in sync deliberately; the answer
  to the Exocet phase is meant to be the Harriers, not a hull purchase.

---

## Validation run

```
python3 tools/units.py check campaigns/PhantomWake/missions/02_pandoras_box.ini
-- 40 unit section(s) checked, 0 problem(s)
```

Scripted checks, all clean:

- every `<Token>` in a `ConditionsCompleted` has a matching
  `Condition_<Token>_Type`, and no condition is defined but unused
- every `Action_*_Message` / `_Intel` / `_Forecast` / `_AreaLabel` key resolves
  in **both** `[Language_en]` and `[Language_ru]`
- every objective named in an `Action_Objectives*` exists in
  `[Taskforce1_Objectives]`, has display text in both languages, and every
  defined objective is actioned by at least one trigger
- every `Action_Units` entry and every formation member names a real section
- all 34 `Disabled=True` units are enabled by exactly one trigger, and every
  `Action_SetEnabledStatus=True` target is actually authored `Disabled=True`
- every `Disabled=True` trigger is enabled by another trigger
- every `Action_VariableSet` name is declared in `[CampaignVariables]`
- all `NumberOf*` counts match the real section counts
- no `#` anywhere in the file
- `en` / `ru` key parity, modulo the intentional label suffixes

Cross-file:

- `NumberOfMissions` matches the `[MissionN]` count and every `MissionFile` exists
- every `TaskForceModeAllowedRosterUnits` entry is a strict subset of
  `player_task_force_roster.ini`, variants included
- `wp_ss_foxtrot` and `wp_ms_roro_b` appear in **no** allowed-roster line
- roster variant and mission `CampaignTag` agree

---

## Open items for playtest

1. **Two Exocets plus two aircraft torpedoes.** Should be survivable by gun
   escorts with chaff, and trivially survivable by a player who kept a Harrier
   on CAP, which is the designed answer. If it still reads as too much, the
   remaining lever is dropping `Taskforce2Helicopter1` to `ASWKiller` so that
   nothing in the mission carries an anti-ship missile at all - the fiction
   already supports it, since under the original seizure order there should not
   have been any.
2. **`Generated` + `TaskForceModeIgnoreUnit` + `JoinTaskForce` together.** Each
   half has vanilla precedent — `IgnoreUnit` in `09 Shadows off Palawan`
   (Generated), `JoinTaskForce` on a vessel in `08 Defense of North Borneo`
   (Replaced) — but the combination is new. If the Pandora fails to join, the
   fallback is switching Mission5 to `Replaced` and giving Vessel1/Vessel2
   `TaskForceModeReplacedUnitIndex`, exactly as 08 does.
3. **`Action_EnableDisableSensorSystems` on a player-owned unit.** Mission 01
   did this to a Neutral vessel that had just been transferred; here it targets
   a hull the player owns from second one. If it is ignored, the decoy swarm
   still carries the phase on its own.
4. **`Attack=` on vessel and helicopter sections.** Still absent from all of
   Pacific Strike, still community-guide only. If it is ignored the Hounds run
   authored routes straight through the convoy lane weapons-free and the Frelons
   engage freely on the same approach — degrades to an ordinary intercept, does
   not break.
5. **SEPTAR toughness.** `usn_septar_qst-35` is 1 t but reports `armor Medium`.
   If the drones soak an unreasonable number of rounds, swap some for
   `usn_septar_qst-35_small`, or accept it as "the decoys are built to be shot
   at", which is literally true.
6. **28 simultaneous surface contacts.** Performance and UI clutter unmeasured.
   The dial is dropping decoy count; the mission does not depend on any
   individual drone.

---

## Briefing

At [02_pandoras_box_briefing/](../02_pandoras_box_briefing/). Found by
folder-name convention, no ini keys — same as vanilla and as 01C.

```
02_pandoras_box_briefing/
  BriefingText_en.xml   BriefingText_ru.xml
  BriefingMap_en.xml    BriefingMap_ru.xml
  02_arabian_sea.png
```

Folder shape matches vanilla `09 Shadows off Palawan_briefing/` exactly, which
also ships four panes in two languages plus its PNG assets and nothing else.

### Format: chat log, not operations order

01C used a straight NATO five-paragraph order. This one follows **IDEA.md's own
instruction** — *"текстовые брифинги форматировать как лог чата"* — so the body
is a transcript with all four HQ characters speaking in turn, colour-coded:
ATLAS, SIREN and E.C.H.O. in `NTDS.FriendColour`, FAIRWAY in
`NTDS.HostileColour` because he is broadcasting from somewhere he should not be.

The message header (FM / TO / INFO / SUBJ) and a numbered EXECUTION block are
kept around the transcript so it still reads as a company document rather than a
chat window. FAIRWAY appears in the INFO line as *"UNLISTED THIRD PARTY - SOURCE
FAIRWAY"*, which is the joke: nobody added him to the distribution list.

### It carries the campaign arc

A **COMPANY STATUS - STAGE TWO** section sits above the transcript and does the
work the campaign map cannot:

- Stage 1 is closed. Four contracts done, the company is solvent, and it is
  moving east because the Horn of Africa has run out of clients — which is the
  Stage 1 → Stage 2 transition from CAMPAIGN_SCRIPT.md stated in-fiction.
- **E.C.H.O.'s origin is named for the first time**: lifted off MV Vagabond's
  server deck during Contract 01 and now wired into the flagship, *"it does not
  explain where it came from"*. That is the IDEA.md secret, planted rather than
  revealed.
- **The Syndicate becomes a named antagonist.** Contract 01 ended with an
  unanswered question — who paid for a military jammer and an assault transport
  to take a rusted container ship. This briefing answers half of it and gives
  the black boats their name, ABYSSAL HOUNDS.
- The closing line sets up what the reward changes: *"Phantom Wake stops being a
  company with boats and becomes a company with an air arm."*

Nothing about the Nereus AI or the Stage 4 endgame is touched. Too early —
FAIRWAY's line about radar showing *"what somebody else has decided you should
see"* is as close as it gets, and it is deliberately readable as ordinary
tradecraft on a first pass.

### Intelligence photos

Two period photographs down the right-hand edge of the map pane, following the
vanilla pattern from **`05 Strike on the Monster`** — a white 5 px border, a soft
`DropShadowEffect` and a small `RotateTransform`, so each reads as something
pinned to the chart rather than drawn on it.

They are not decoration. Both are real precedent for exactly what the player is
escorting, and one of them is the mission's third phase:

- **ATLANTIC CONVEYOR, 1982.** Container hull, welded deck, Harriers embarked —
  the ARAPAHO concept proven in the Falklands. *Sunk by a single air-launched
  Exocet.* The caption says so plainly, so a player who reads the briefing walks
  into the missile phase already knowing what one hit does to this kind of ship.
- **AGOSTINHO NETO, 1984.** Yak-38M lifting off an ordinary commercial container
  deck. Caption: *"The idea is not new. It has simply never been for sale."* —
  which is the Syndicate's whole motive in one line.

Format notes:

- **Vanilla ships PNG only** (38 assets, zero JPG), so the supplied
  `Intel_ship.jpg` / `Intel_ship2.jpg` were converted to `02_intel_conveyor.png`
  and `02_intel_yak38.png` rather than bound directly. The originals are left in
  the folder untouched and can be deleted.
- `Intel_ship2.jpg` had a Russian caption baked into its white margin. The photo
  block was auto-detected and cropped out of it, so the pane carries its own
  caption in whichever language is being displayed instead of a hardcoded one.
  Vanilla solves the same problem the other way, with `01_tropic.png` and
  `01_tropic_ru.png`; cropping is cheaper and scales to every language.

### Task force summary

`{TaskForceVesselSummaryRuns}` in a strip under the plot, the same token and the
same usage as `05 Strike on the Monster`. Lists the player's actual hulls on the
briefing screen.

### Map pane

Open ocean, so unlike 01C there is no coastline to render and the base PNG is a
plain 10 NM graticule generated from the same numbers as the mission file.

```
810 x 540 px = 90 x 60 NM at 9 px per NM, covering NM X -20..70, Z -90..-30
Canvas.Left = (X_nm + 20) * 9        Canvas.Top = (-30 - Z_nm) * 9
```

Shown: the holding box, MV Pandora at her start, the dashed transit lane through
all four gate positions, the Keystone circle at its true 6 NM radius, the three
Hound packs with threat arrows on their real bearings, the jammer, the support
group, the missile carriers, and the decoy belt as a single
`NTDS.UnknownColour` wash labelled *"contacts unresolved"* rather than 16
individual icons — because the player is not supposed to know where they are.

The three phase gates are labelled on the lane (EW ONSET, INTERCEPT, MISSILE
THREAT) so the briefing telegraphs the shape of the fight without giving away
which contacts are real.

### Validation

All four panes parse as XML. Every `StaticResource` / `DynamicResource` key used
is one that already appears in a vanilla Pacific Strike briefing — an unknown
key fails the entire pane, so the set is deliberately restricted to:
`Font.Size.Header`, `NTDS.FriendColour`, `NTDS.HostileColour`,
`NTDS.UnknownColour`, `NTDS.Allied.Surface`, `NTDS.Enemy.Surface`,
`NTDS.Enemy.Air`, `NTDS.Enemy.Helicopter`, `NTDS.Unknown.Surface`,
`ContactIconThickness`. The `Assets[02_arabian_sea]` binding resolves to a file
that exists.

`{TaskForceName}` substitutes in both panes and both languages.

### Still missing elsewhere

01, 01A and 01B have no briefing folders — `01_rusted_sea_briefing/`,
`01A_sweeping_net_briefing/`, `01B_safe_heaven_briefing/`. 01C is text+map in
`en` only and could take a `_ru` pair now that the pattern is established.
