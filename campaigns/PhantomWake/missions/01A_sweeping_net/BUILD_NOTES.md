# 01A Sweeping Net — build notes

## Coordinate system

`MapCenterLatitude=-5.64`, `MapCenterLongitude=39.6`.

```
X = (lon - 39.6) * 60      (+X = East)
Z = (lat - (-5.64)) * 60   (+Z = North)
```

No cosine-of-latitude correction — see `docs/CLAUDE.md` §1.

## Correction: the backbone's unit positions are trusted, not scattered

An earlier pass assumed the pirate and neutral positions in your backbone were
editor auto-scatter, since they didn't line up with the two map symbols, and
rebuilt them clustered around the search circle. **That was wrong.** You
confirmed you placed them deliberately, so this version restores every
`RelativePositionInNM`, `Waypoints`, `Heading`, and `Nation` value exactly as
you authored them. Nothing about unit placement in this file is invented —
only the plumbing that was missing (player anchor, `Zone1`, triggers,
objectives) is new.

Re-reading the data with that correction in mind, it actually holds together
well:

- `Taskforce2Vessel1` (the only pirate with `Waypoints`) is the formation
  leader — `Taskforce2_Formation1=...|Pirates|Loose|1.5` means Vessel2-4 keep
  station on it rather than needing their own routes. That's standard
  formation behaviour, not unfinished authoring.
- Vessel1's route runs from the spawn point (X=3.43, Z=67.44) down to
  (X=-13.07, Z=21.65) — **11.2 NM from the search circle's centre**, i.e.
  inside your 25 NM "Pirates Search Area." The flotilla starts north of the
  circle and patrols into it. I'd misread the spawn point being outside the
  circle as a mismatch; it's the intended approach.
- The `220.4727` altitude on several surface waypoints (Vessel1, both
  freighters, some neutrals) is the same benign editor artifact documented in
  `docs/CLAUDE.md` §9 (ignored for surface units) — not something to fix.
- `Nation=pirates` on the four skiffs is a nation you set up yourself in the
  original editor. `tools/units.py nations` only reflects what's indexed from
  `share/`, so its absence there was never evidence of a problem — reverted my
  earlier "fix" to `Terrorists`.

## The pirate detection trigger doesn't use a fixed circle

Since the flotilla moves along its own authored route rather than sitting at
one hiding spot, a static `UnitsInTheArea` circle would only catch it at one
point on that route. Used the sensor-based condition instead:

```ini
[Trigger3]
Condition_PiratesSpotted_Type=UnitDetected
Condition_PiratesSpotted_Taskforce=Taskforce2
Condition_PiratesSpotted_Units=Taskforce2Vessel1,Taskforce2Vessel2,Taskforce2Vessel3,Taskforce2Vessel4
Condition_PiratesSpotted_MinimumUnits=1
```

Verified syntax, not a guess — copied from `pacific-strike-task-force/missions/10 Vengeance at Luzon.ini`,
Trigger9 (`Condition_Type=UnitDetected` + `_Taskforce=` + `_Units=`). Fires a
warning popup whenever the player's sensors actually pick up any one skiff,
wherever that happens on the patrol route. No `Action_UnitWaypoints` override
on aggro — the flotilla is already `WeaponStatus=Free` from spawn and follows
its own authored route, same principle Mission 1 used for its Boghammars
("hostile from mission start," no live status change needed).

## Restored: the secret Syndicate submarine

`NeutralSubmarine1` (`ran_ss_oberon`, `Nation=terrorists`, active sonar +
towed array, `IdentifySelf=No`, `CrewSkill=Veterans`) is back exactly as
authored — position, `RandomSpawnRange=10`, and the waypoint with inline
`SetTelegraph,1/SetSensors,Sonar_Off,Towed_Off` partway through (it goes quiet
and shallow mid-patrol, which is exactly the kind of deliberate authoring that
told me this wasn't scatter).

Per your note, this is a hidden Syndicate spy asset, not part of the fishing
conglomerate's contract. Gave it an actual role instead of silent loitering:

- **`Trigger7`** fires on `Condition_Type=UnitDetected` (`Taskforce=Neutral`,
  `Units=NeutralSubmarine1`) — an ECHO sonar-anomaly popup plus an intel line,
  and reveals a new **Hidden** objective, `MysteryContact` (5 points, no
  penalty, optional — never shows in the AAR unless triggered).
- **`Trigger8`** completes that objective if the player sinks it, with an
  ATLAS line acknowledging the boat "wasn't on any manifest."
- **Deliberately excluded from `Trigger5`** (the neutral-kill contract
  termination) — the fishing conglomerate cares about its own boats, not a
  mystery contact nobody sent you after. Sinking it is a free bonus, not a
  ROE violation.
- `Condition_Taskforce=Neutral` on `UnitDetected` is **unverified** — the one
  vanilla example I found (`10 Vengeance at Luzon.ini`) uses `Taskforce2`
  against an enemy-side unit, not `Neutral`. Low risk either way: this is an
  optional flavour subplot, so if it silently never fires, nothing else in
  the mission breaks.
- Two new `[CampaignVariables]` seed a future payoff: `01AMysterySubDetected`,
  `01AMysterySubDestroyed`. Not consumed anywhere yet.

## Deviations from SCRIPT.md

1. **Pemba Channel / Tanzanian coast, not Somali coastline.** Your map centre
   (-5.64, 39.6) is south of the equator, off Tanzania near Pemba/Zanzibar —
   Somalia sits entirely north of the equator. Same call as Mission 1's Gulf
   of Aden-vs-Guinea deviation: coordinates win, text is rewritten to match.
2. **4 pirate skiffs, not 5.** Your backbone had exactly 4 built, positioned,
   and formed up. Kept your 4 rather than fabricate a 5th hull from nothing;
   objective/victory text says "skiffs," not a specific count.
3. **Defeat on civilian kill is immediate**, per SCRIPT.md's "Alliance
   Engagement Violation" — `Trigger5` ends the mission outright
   (`Action_EndMission=True`, `Victory=Taskforce2`), unlike Mission 1 where a
   civilian kill only fails one objective.
4. **Defeat uses whole-task-force wipeout, not "flagship sunk."**
   `campaign.ini` already declares `TaskForceRequireFlagship=False` for this
   campaign, so `Trigger6` uses `HasNoUnitsOfType`, matching Mission 1.
5. **No scripted island/shoal placement.** There's no authored-land mechanism
   beyond the game's real-world terrain, and the Pemba Channel already has
   that geography at these coordinates.
6. **"Conserve heavy ordnance" is flavour text, not an enforced mechanic** —
   there's no ammo-type-fired condition in the engine. Stated in the intro
   popup and the campaign's `MissionSpecialNote_en` instead.

## Zone1: converted from a decorative rectangle, not repositioned

`MapSymbol_New1` ("PMC Deployment," a plain `[MapSymbol]` rectangle) doesn't
gate Task Force deployment — only `[Zone1] Type=Deployment` does (see
`docs/Task_Force_Campaign_Guide.md` §1 and `01_rusted_sea.ini`'s own Zone1).
This is the one structural change to something you drew: same rectangle,
same `GeoPoint`, same 10×20 NM footprint, now wired up as the real deployment
zone. The redundant map symbol was dropped since `Zone1` renders on its own.

## Timing estimate

Deployment zone to the pirates' actual spawn point is about **124 NM**
(anchor at -5.73,-56 to Vessel1's spawn at 3.43,67.44) — a long patrol leg,
expect heavy time acceleration before the player closes on the search sector.
Once Vessel1's route carries the flotilla into the search circle, detection
and the fight itself are open-ended (no timer).

## Editor limits hit

- **`UnitDetected` needs a real unit/side to check against `Taskforce`,
  `Units`** — confirmed syntax from `pacific-strike-task-force/missions/10
  Vengeance at Luzon.ini`, not guessed.
- Same core limits as Mission 1 — see `docs/CLAUDE.md` §2-5: no relative
  timers (not needed here), `Action_Units` is per-trigger, area conditions
  are static circles (worked around here with `UnitDetected` instead, since
  the target moves).
- Unit references validated locally: `python3 tools/units.py check
  campaigns/PhantomWake/missions/01A_sweeping_net.ini` → 15 sections, 0
  problems.

## Not built

- Briefing XML panes — this campaign uses `MissionIntro_en` in `campaign.ini`
  instead, same as Mission 1.
- Ribbon awards — `commander_settings.ini` has no `[TaskForceRibbons]` block
  yet, so none are granted here either.
- Localisation — non-English `[Language_*]` blocks are the minimal stubs your
  editor export already had (Name + map symbol label only), not real
  translations.
