# 01C Rusted Spear — build notes

Mission file: [01C_rusted_spear.ini](../01C_rusted_spear.ini)
Script: [SCRIPT.md](SCRIPT.md)
Editor backbone it came from: `share/01C.ini`
Briefing: [01C_rusted_spear_briefing/](../01C_rusted_spear_briefing/)

**9 triggers, 4 objectives, 9 hostile patrol craft, 1 helicopter, 3 phases.**
For comparison: 01A is 8 triggers and 4 objectives, 01B is 13 and 5.

> Note: this folder is spelled `01C_ruested_spear`. The mission `.ini` uses the
> corrected `01C_rusted_spear`. Left the folder alone so nothing tracked moves —
> rename it if you want the two to match.

---

## Geography — measured, not guessed

Map centre unchanged from the backbone: `-6.08 / 39.04`, the Zanzibar Channel.

```
X = (lon - 39.04) * 60      Z = (lat + 6.08) * 60
```

**The first version of this mission used an inferred coastline and it was
wrong.** After the first test run the campaign-map screenshot became ground
truth: the land mask was extracted from it, calibrated on the deployment
rectangle (12.375 px per NM, cross-checked against two authored map symbols)
and cleaned of the mission's own red and blue symbol overlays. Every position
and every route leg in the file is now sampled against that mask.

What that corrected:

- The large island east of the playfield is **PEMBA**, not Unguja. A threat
  arrow at NM (40, 45) was sitting on top of it, and the deployment box at
  (54, 26) was clipping its southern tip.
- The "Unguja north-east land at X 30..34" in the first draft did not exist. It
  was the deployment rectangle's own border being read as coastline.

Measured layout:

```
Mainland (Tanzania)   X <= -12 at Z 6..14, receding to X <= -4 by Z 36
Unguja north end      X 10..20 at Z 4..22   (Tumbatu at X 10..12, Z 14..18)
Pemba                 X 32..48 at Z 36..60
Zanzibar Channel      X -12..8 at Z 6..20   <- the bay, ~20 NM wide
Open water north      X -4..30 at Z 22..60
```

So the channel really is a bounded bay, mainland west and Unguja east, and its
northern mouth at Z ~20 is a door a picket line can close. That is the mission
in one sentence, and it is why everything moved into the channel.

Audit after repositioning: **35 surface coordinates and 4 route paths all clear
of land; 7 map symbols, 1 zone and 1 retreat anchor all in water; no overlap
between any two briefed circles or between a circle and the deployment box.**

## Phase geometry

| Element | NM position | Notes |
|---|---|---|
| Deployment box | X 2..26, Z 34..42 | open water north of the channel mouth |
| Player anchor | (10, 0, 36) hdg 195 | 18 NM up-threat of the picket |
| Picket line | (6,20) (2,20) (-2,20) (-6,20) | line abreast across the mouth, 4 NM spacing, stationary |
| Nyoka holding position | (0, 0, 11) | mid-channel, 9 NM behind the picket, surfaced |
| Nyoka transit route | (1,19) → (5,25) → (9,27.5) | 21.1 NM authored |
| NavPoint Zulu | (10, 28) r=4 | clear of the mouth |
| Interceptor pair | (-8, 11) (-8.6, 10.2) | mainland shore, 38 kt |
| Coastal squadron | (14,50) (15,51) (13,51) | ~22 NM to the shelf, ~35 min |
| Mi-14 | (10, 1000, 54) | ~30 NM ingress, ~16 min |
| Retreat anchor (Red) | (-4, 26) | mainland side |

Escort leg is 21.1 NM authored; the 4 NM Zulu radius catches her early, so
**~17 NM effective, about 64 minutes at her 16 kt flank.** Player transit is
18.4 NM, so the contract runs ~90 minutes of game time. In line with 01B's two
hours, and there is no clock on it.

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

### How the boat joins the fleet — the Fixed Wing bug

**Symptom from the first test run: the awarded Foxtrot arrived in the player's
task force under the FIXED WING tab.**

Cause: the boat was awarded with
`TaskForceModeCompletionRewardedUnits=wp_ss_foxtrot,Variant66,1` in
`campaign.ini`. Every occurrence of that field in the vanilla Pacific Strike
campaign is an aircraft with a `SquadronReference`:

```
TaskForceModeCompletionRewardedUnits=usn_p-3c,Squadron31,1|usn_a-7e,Squadron10,2|...
```

Three uses, all aircraft, no vessel or submarine anywhere. The field appears to
assume aircraft and files whatever it is handed accordingly. **Do not use it for
vessels or submarines.**

Fix: award her with `JoinTaskForce=True` on the mission unit section instead —
which requires the section to be named `Taskforce...VesselN / SubmarineN /
AircraftN / HelicopterN`. So she is now authored as **`[Taskforce1Submarine1]`**,
not `NeutralSubmarine1`, with `CampaignTag`, `CampaignRepair=True` and
`TaskForceModeIgnoreUnit=True`.

**Accepted side effect:** she belongs to the player from second one rather than
defecting on contact. In exchange, the mission no longer depends on
`Action_UnitTransferToTaskforce=Taskforce1` — the one field that appeared
nowhere in vanilla — and can no longer be soft-locked by it failing. That
removes the biggest risk in the file.

The "goes under player control" beat is preserved narratively: she sits at
`Telegraph=0` with no `Waypoints`, her crew will not start engines until they
see a Phantom Wake hull, and `Trigger4` issues the route on contact. The win
trigger stays `Disabled=True` until the rendezvous fires, so sending her out
alone cannot skip the escort.

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

## Briefing

Vanilla **does** ship briefings, contrary to docs/CLAUDE.md §14 — every Pacific
Strike mission has one. They are found **by folder-name convention, with no ini
keys at all**: `<mission ini basename>_briefing/` next to the mission file,
containing `BriefingText_<lang>.xml` and `BriefingMap_<lang>.xml`.

There are no `MissionBriefing*` keys anywhere in the vanilla campaign, so the
`MissionBriefingLeftPane` / `MissionBriefingRightPane` route in the community
guide and in `docs/briefing_setup_guide.md` is not how the shipped campaign does
it. 01C had no briefing because it had no such folder.

Now at [01C_rusted_spear_briefing/](../01C_rusted_spear_briefing/):

- `BriefingText_en.xml` — `<Grid>` root, NATO message layout copied from
  Okinawa's structure (PRIORITY / FM / TO / INFO / SUBJ, then numbered
  paragraphs). Classification reads COMMERCIAL IN CONFIDENCE rather than SECRET,
  because Phantom Wake is a company, not a navy. `{TaskForceName}` substitutes.
- `BriefingMap_en.xml` — `<Viewbox>` + `<Canvas Width="810" Height="810">`.
- `01C_channel.png` — the base map, **generated from the same land mask** at
  15 px per NM covering NM X -14..40, Z 4..58. Because it is rendered from the
  boolean mask rather than copied from the screenshot, none of the mission's own
  symbols bleed into it.

Canvas mapping, for editing the overlay:

```
Canvas.Left = (X_nm + 14) * 15        Canvas.Top = (58 - Z_nm) * 15
```

Only XAML resource keys that already appear in vanilla briefings are used
(`Font.Size.Header`, `NTDS.FriendColour`, `NTDS.HostileColour`,
`NTDS.Allied.Submarine`, `NTDS.Enemy.Surface`, `NTDS.Enemy.Air`,
`ContactIconThickness`) — an unknown key fails the whole pane. Both files parse
as valid XML and the asset reference resolves.

Only `_en` is authored. Vanilla ships en/de/ja/ru and no cn, so partial language
coverage is normal.

---

## Two things worth fixing outside this mission

1. **`PopupStyle=Message` is not a valid value.** Vanilla uses exactly four:
   `Intro`, `NavalMessage`, `Notification`, `Outro`. `01_rusted_sea.ini` has 8
   occurrences of `Message` and `01A_sweeping_net.ini` has 2. 01B and 01C are
   clean. Those popups may be falling back to a default style or not rendering
   as intended.
2. **No briefing folders for 01, 01A or 01B either.** Same convention applies —
   `01_rusted_sea_briefing/`, `01A_sweeping_net_briefing/`,
   `01B_safe_heaven_briefing/`.

---

## Intel message format

Checked against vanilla. Intel strings are **plain text with no `Title=` /
`Body=` structure and no XAML** — `Action_Taskforce1_Intel=<key>` and
`<key>=One or two sentences.` in `[Language_en]`. That is what 01C already had.

One convention difference: all four vanilla missions that use intel name the key
`Taskforce1<Something>Intel`. 01C's keys were `StartIntel`, `BlockadeIntel` and
so on, so they have been renamed to `Taskforce1StartIntel` etc. to match. The
key name is arbitrary as far as the parser is concerned, so this is insurance
rather than a fix. `01A` and `01B` still use the short form.

Also confirmed correct and left alone: the popup `Title=...\nLINE\n<size=24>...`
shape with bare continuation lines inside `Title` is exactly what Okinawa does.

---

## Open items for playtest

1. **`Attack=` on vessel sections.** Not in vanilla at all. If the interceptors
   ignore the submarine and chase the player instead, this is why. Degrades to
   an ordinary intercept.
2. **`JoinTaskForce=True` on a submarine section.** Documented, and the section
   name is now legal, but vanilla never awards a submarine this way — no
   Pacific Strike mission uses `JoinTaskForce` at all. If she still lands in the
   wrong tab, the remaining lever is `CurrentTaskForce` seeding in `campaign.ini`.

**No time limit**, matching Mission 01 and 01A. 01B is the only mission in the
campaign with one — a 7200 s sunrise hard fail plus an 80-minute warning — and it
has one because that contract is explicitly a before-dawn infiltration. Nothing
in this one expires.
