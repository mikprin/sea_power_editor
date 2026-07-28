# 01 Rusted Waters — build notes

## Coordinate system

`MapCenterLatitude=12.35`, `MapCenterLongitude=44.00`.

```
X = (lon - 44.00) * 60      (+X = East)
Z = (lat - 12.35) * 60      (+Z = North)
```

No cosine-of-latitude correction — see `docs/CLAUDE.md` §1 for the proof.

## The convoy axis

Everything sits on bearing 110° from the rendezvous point, which is where your two
original map markers pointed. `d` is distance in NM along that axis from the RV.

| d | Point | X, Z (NM) | lat, lon |
|---|---|---|---|
| -5 | MV Vagabond start | -14.67, 0.67 | 12.361167, 43.755500 |
| 0 | Rendezvous | -9.97, -1.04 | 12.332672, 43.833860 |
| 5 | Pirate ambush | -5.27, -2.75 | 12.304167, 43.912167 |
| 7 | EW + helo launch gate | -3.39, -3.44 | 12.292667, 43.943500 |
| 10 | Air Threat Axis "B" | -0.57, -4.46 | 12.275667, 43.990500 |
| 16 | NavPoint Alpha | 5.07, -6.51 | 12.241500, 44.084500 |

Deployment zone: 10 × 7 NM centred `12.266667 / 43.758333`, about 6 NM SW of the RV
and clear of it, so the player has an actual approach to make.

Beat order is exactly Rendezvous → Pirates → Helicopter → Escape, and the pirate
ambush at d=5 is the midpoint between the rendezvous and the Air Threat Axis.

## Why the timing works now

**MV Vagabond is underway from t=0** at a fixed speed on a fixed four-waypoint route,
and every downstream beat is a `UnitsInTheArea` gate on *her*, not on the clock:

| Beat | Gate |
|---|---|
| Congested water | Vagabond within 4 NM of d=5 |
| Pirate ambush | Vagabond within 2 NM of d=5 |
| EW jamming | skiffs destroyed **OR** Vagabond within 1.5 NM of d=7 |
| Helo launch | Vagabond within 2 NM of d=7 (trigger armed by the EW trigger) |
| Air contact warning | helo within 20 NM of B |
| Final warning | helo within 10 NM of B **AND** Vagabond within 8 NM of B |
| Cargo lost | helo within 2 NM of B **AND** Vagabond within 3 NM of B |
| Victory | Vagabond within 3 NM of Alpha |

The only absolute-time trigger left in the mission is the t=5 intro popup. Nothing can
fire out of order, and a slow or a fast player gets the same sequence.

The helicopter flies a 25 NM run-in from the north at cruise and then loiters in a
tight loop over B, so it is on station before the convoy arrives and the player has a
long visible window to shoot it. From the final warning to the boarding loss is
roughly four minutes of real shooting time; killing the transport disables the loss
trigger outright.

The escort leg is 21 NM total (start → Alpha), about 70–75 minutes at merchant speed.

## MV Vagabond changes sides

She spawns as `NeutralVessel1` — an ordinary green civilian — and the rendezvous
trigger runs `Action_UnitTransferToTaskforce=Taskforce1`, so from that moment she
displays as a friendly and the player can con her directly. She also carries
`IsValuableUnit=True` and a name override:

```ini
NeutralVessel1NameOverride=MV VAGABOND
NeutralVessel1ShortNameOverride=VAGABOND
```

Two consequences worth knowing:

1. After the transfer she counts as a `Taskforce1` vessel, so the "task force wiped
   out" trigger (13) only fires if she dies too. Trigger 12 covers her loss
   separately, and with no escorts left the helicopter will board her anyway, so the
   gap closes itself. Not worth more machinery.
2. The player can steer her. Detouring around the Air Threat Axis by more than 3 NM
   dodges the boarding trigger. That is legitimate seamanship, so it is left in.

## Map clutter

Trigger areas that exist only as logic gates are set to
`Condition_*_AreaDisplaySide=None` so they do not draw. Only these are visible:
rendezvous (3 NM), fishing grounds (4 NM), the Air Threat Axis boarding circle
(2 NM), and NavPoint Alpha (3 NM). That is what fixes the overlapping pink blobs.

## Deviations from SCRIPT.md

1. **Gulf of Aden, not Gulf of Guinea.** Every coordinate in the backbone and both
   `.unitgroup` presets is at 12°N / 43–47°E, and the preset units are Iranian and
   French/Iraqi. All text was written to match. Say the word to move the prose.

2. **Deployment zone repositioned.** Your original `Zone1` was 220 NM east of the
   rendezvous — around 13 hours of steaming.

3. **The Vagabond's start moved to d=-5.** Your `MapSymbol_New2` arrow was 11.8 NM
   from the RV, which is why she looked like she had spawned somewhere unrelated. The
   arrow symbol moved with her; bearing is still 110°.

4. **Escort leg is 21 NM.** A 45 NM leg is nearly three hours at merchant speed.

5. **The three pirate skiffs are hostile from mission start**, idling at Telegraph 1
   inside the neutral cluster alongside a genuinely neutral `ir_fab_boghammar` and
   `ir_pt_parvin`. Same "you cannot tell them apart" tension, but it avoids
   green→red `Action_UnitTransferToTaskforce`, which is not demonstrated anywhere in
   the vanilla campaign. (Green→blue, which the Vagabond now uses, is the mirror of
   the blue→green case vanilla does demonstrate.)

6. **No literal 200-second countdown.** There is no relative-time condition in the
   engine — see `docs/CLAUDE.md` §2. The four-minute window is produced by the
   helicopter's approach geometry instead, which is more robust and reads the same
   in play.

## Editor limits hit

- **No relative timers.** `Type=Time` is always absolute from mission start.
- **Area conditions are static circles, never distance-to-unit.** Hence the
  two-condition AND pattern on triggers 9 and 10 — one circle checks the threat, the
  other checks the ship, and the loss only lands when both are inside.
- **No jamming action.** Done as popup + intel + a real
  `Action_EnableDisableSensorSystems=Disable` on the Vagabond, with an actual EA-6B
  orbiting at 30,000 ft as the source.
- **`Action_Units` is per-trigger, not per-action** — the EW trigger and the helo
  spawn had to be split for this reason.
- **Unit references cannot be validated here.** StreamingAssets is not in the repo.

## Needs verifying against the game files

| Field | Value | Note |
|---|---|---|
| `ir_fab_boghammar`, `ir_pt_parvin` | `VariantReference=Default` | preset JSON says `_variantId: 0` |
| `fr_sa-321`, `iqaf_md500` | `SquadronReference=Default` | presets carry no squadron info |
| `fr_sa-321` | `LoadoutVariant=Empty` | from the preset; unarmed transport |
| `iqaf_md500` | `LoadoutVariant=Recon` | from the preset |
| `usn_ea-6b` | `SquadronReference=Squadron6` | from the vanilla campaign reward list |
| `civ_ms_c7s68` | `Variant19` + `LoadoutVariant=Containers` | copied from vanilla Okinawa |
| `ir_pf_bayandor` | `Variant1` | anchor only, generator replaces it — low risk |
| roster variants | `Variant1` except `usn_dd_gearing` | **matters** — a bad variant means the hull never appears in Task Force Builder |
| `Action_UnitTelegraph`, `Action_UnitVelocityInKnots` | trigger 4 | documented in the community guide, unused in vanilla; both set for redundancy |
| Telegraph → knots mapping | Vagabond at `Telegraph=4` | assumed ~17 kt for the leg-length estimate only; the trigger gates are positional so a different speed changes pacing, not correctness |

## Not built

- Briefing XML panes — vanilla uses `MissionIntro_en` in `campaign.ini` instead.
- Ribbons and medals — need art, and an undefined ribbon ID breaks the debrief.
- Localisation. English only.
