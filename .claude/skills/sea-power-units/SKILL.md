---
name: sea-power-units
description: Look up and validate Sea Power unit and ordnance references - aliases, VariantReference / SquadronReference lists, LoadoutVariant values, Role, hull specs, telegraph speeds, weapon systems, magazines and ammunition stats - before writing a mission .ini or a Task Force roster. Use whenever placing a unit, choosing a variant, filling AllowedVessels / TaskForceModeAllowedRosterUnits / TaskForceModeAirTaskingFlightN, writing a magazine override, or checking a finished mission file. Triggers on "what variants does X have", "find me a frigate / transport helicopter", "is this alias real", "which loadouts", "what does this ship carry", "empty its magazine", "missile range", "validate my mission", "pick a ship for".
---

# Sea Power unit lookup and validation

A bad `Type=`, `VariantReference=`, `SquadronReference=` or `LoadoutVariant=` **fails
silently**. The unit never spawns, the roster entry never appears in Task Force
Builder, and nothing is logged. Never guess these — look them up, then check the file.

## Check the mission before you ship it

```bash
python3 tools/units.py check campaigns/PhantomWake/missions/01_rusted_sea.ini
```

Walks every `[Taskforce1Vessel3]` / `[NeutralAircraft2]` / … section and reports:

- a `Type=` alias that does not exist
- a variant outside the unit's real range
- a `LoadoutVariant` the hull does not offer, or set on a hull with no loadouts
- `VariantReference=` used where the unit needs `SquadronReference=` (or the reverse)
- a `[<Unit>_WeaponSystemN]` magazine override naming a weapon system the hull does
  not have, an ammunition alias that does not exist, or a unit section missing from
  the file

Exits non-zero when it finds anything, so it works as a pre-commit or hook check.
**Run it after every edit to a mission file.** It costs a second and it is the only
thing standing between a typo and a silently broken mission.

## Look things up

```bash
python3 tools/units.py show <alias>              # start here
python3 tools/units.py search <text> [--type Helicopter] [--role Transport] \
                                     [--category aircraft] [--nation Soviet] [--year 1985]
python3 tools/units.py variants <alias> [--nation X] [--year 1985] [--limit N]
python3 tools/units.py loadouts <alias>
python3 tools/units.py nations
python3 tools/units.py arsenal <alias>           # weapon systems, magazines, ammo
python3 tools/units.py ammo <alias-or-search> [--type Torpedo] [--target ASW]
```

`show` is the one-stop card:

```
$ python3 tools/units.py show wp_ka-29
Type=wp_ka-29
  category      aircraft  (Helicopter)
  Role          Attack,Transport,SAR   <- Air Tasking AllowedUnitRoles
  LoadoutVariant  Strike,CAS,AntiArmor
  SquadronReference  Default,Squadron1-3  [4 total]
  nations       Soviet
  service       1985-1985
  mission section  [Taskforce1Helicopter1] (or Taskforce2.../Neutral...)
```

`Squadron1-3` is a compressed run. `search` with no text plus filters is how you
answer "what could play this part" — e.g. `--type Helicopter --role Transport`
finds the five airframes that can carry a boarding party.

`arsenal` answers "what is this thing actually armed with", and prints the magazine
override block ready to paste:

```
$ python3 tools/units.py arsenal ir_fab_boghammar
  WeaponSystem1   107mm_Hasheb-1     Missile  ir_107mm_rocket   x441   5 NM
  WeaponSystem2   12.7mm_DSHK_Dual   CIWS     wp_cal_05in       x3000

zero a magazine in a mission with a sibling section:
  [Taskforce2Vessel1_WeaponSystem1]
  Ammunition1=ir_107mm_rocket
  Ammunition1_Count=0
```

`ammo` goes the other way — stats for one round, and every hull that carries it.

## Rules

- **`Default` always exists** on every unit and is always valid in a mission section.
  Vanilla *rosters* never list it, so leave it out of `player_task_force_roster.ini`.
- **Vessels, submarines, land units and biologics use `VariantReference=`.
  Aircraft, helicopters and VTOLs use `SquadronReference=`.** Same idea, different
  key; `show` prints the correct one. Mixing them is a silent failure.
- **Variants and squadrons are cosmetic** — hull number, flag, emblem, livery,
  `Nation`, `ServiceDate`, occasionally `CustomAirGroup`. Never capability. Pick by
  nation and date, never by "which is better".
- **`LoadoutVariant` is not free text.** It must come from that unit's
  `AvailableLoadouts`. If the unit has none, omit the field — do not write
  `LoadoutVariant=Default` as a guess. Loadouts *do* change capability: `Transport`
  on a CH-46 is an unarmed troop carrier, `AntiShip` on a Super Frelon is a missile
  shooter. Choose the loadout that matches the role the mission needs.
- **`Role=` is the Air Tasking vocabulary.** `TaskForceModeAirTaskingFlightN`'s
  `AllowedUnitRoles` field draws from it: `Fighter`, `Bomber`, `HeavyBomber`,
  `Attack`, `MPA`, `ASW`, `ASuW`, `ESM`, `EW`, `AEW`, `SEAD`, `Recon`, `Targeting`,
  `Transport`, `SAR`, `Airliner`.
- **`Telegraph=N` maps to real knots** via the `Telegraph=` line in `show`, read from
  `TelegraphVelocities` in `[Physics]`. Use it to compute transit times instead of
  guessing. Only ~50 hulls carry the override; the rest print
  `engine default; T5 ~ max speed`, which held in 48 of the 50 measured cases.
- **A roster entry must list real variants.** `alias=Variant3,Variant4|cost` in
  `player_task_force_roster.ini`; `TaskForceModeAllowedRosterUnits` in `campaign.ini`
  can only narrow that list, never widen it. Keep the two in sync.
- **Point costs are not in the unit files.** No `[TaskForce]` block exists in any of
  them. Costs come from `campaigns/PhantomWake/FleetScoring/fleet.csv` or the roster.
- **Class names are not in the unit files either** — they live in the game's
  localisation. Alias + nation + service date is the practical identifier.

## Coverage

549 units across four categories, generated from the game's own files:

| category | count | types |
|---|---|---|
| `vessels` | 248 | 203 Vessel, 45 Submarine |
| `aircraft` | 111 | 87 Aircraft, 21 Helicopter, 3 VTOL |
| `land_units` | 187 | LandUnit (airfields, SAM sites, vehicles, buildings) |
| `biologic` | 3 | whales |

Plus **1049 weapon mounts** (`unit_weapons.csv`) and **341 ordnance types**
(`ammunition.csv`).

Ammunition notes:
- Ranges are in **nautical miles**, velocities in **knots**; gun `MuzzleVelocity` is
  the exception, in m/s.
- 341 of the 415 files in `ammunition/` are real ordnance. The rest are
  sub-components (`Propulsion`, `Fueltank`, `Antenna`, `Stabilizer`, `Afterburner`,
  `Radar`, `ECM`, `Container`) and are never valid `AmmunitionN=` values.
- `AmmoPoints` is the supply-system cost of one round, **not** a campaign point cost.
- Several weapon systems can share one magazine — `arsenal` joins them with `+`
  (`WeaponSystem2+WeaponSystem3`). Override either index. Magazines with a blank
  weapon system have no owning mount and cannot be overridden this way.

## Rebuilding

`share/` is gitignored — the raw game files stay local, the CSVs are committed.
After a game update or a new folder:

```bash
python3 tools/build_unit_index.py share/vessels share/aircraft share/land_units share/biologic share/ammunition
```

Categories come from the folder name. Rows for scanned categories are replaced and
other categories are left alone, so folders can be added one at a time. The builder
auto-detects whether a unit uses `_variants.ini` or `_squadrons.ini`.
