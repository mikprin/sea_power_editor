# 01 Rusted Waters — build notes

## Coordinate system

`MapCenterLatitude=12.35`, `MapCenterLongitude=44.00`.

`RelativePositionInNM=X,alt,Z` converts as:

```
X = (lon - 44.00) * 60      (+X = East)
Z = (lat - 12.35) * 60      (+Z = North)
```

No cosine-of-latitude correction. Verified against vanilla `01 Raid on Okinawa.ini`:
map center 26.53/127.47, Kume trigger area geo 26.37616/126.748406 →
`PositionNM=-43.33733,0,-9.341428`. `-0.721594 * 60 = -43.30` matches; with a
cosine term it would be `-38.75`. Same check passes on `07A Hunt for the Cruiser.ini`.

## Key points

| Point | X, Z (NM) | lat, lon | Source |
|---|---|---|---|
| MV Vagabond start | -21.03, 2.96 | 12.399286, 43.649535 | your `MapSymbol_New2` |
| Rendezvous | -9.97, -1.04 | 12.332672, 43.833860 | your `MapSymbol_New1` |
| Ambush point | -6.21, -2.41 | 12.3098, 43.8965 | RV + 4 NM on 110° |
| Boarding point | -1.51, -4.12 | 12.2813, 43.9748 | RV + 9 NM on 110° |
| NavPoint Alpha | 4.13, -6.17 | 12.2472, 44.0688 | RV + 15 NM on 110° |
| Helo spawn | 3.62, 9.98 | 12.5163, 44.0603 | 15 NM on 020° from boarding pt |
| Jammer orbit | 10, 25 @ 30000 ft | 12.7667, 44.1667 | standoff, over the Yemeni coast |

Bearing from your two markers is exactly 110°, matching the `Bearing=110` on the
ThreatArrow — so the convoy axis is 110° and the whole mission runs down it.

## Timeline

| t (s) | Event | Trigger |
|---|---|---|
| 5 | Intro popup, forecast, intel | 1 |
| ~900 | Player within 2 NM of RV → Vagabond gets underway to Alpha at Telegraph 4 | 2 |
| Vagabond within 7 NM of ambush pt | "congested water" popup | 3 |
| Vagabond within 4 NM of ambush pt | 3 skiffs go to flank speed and charge | 4 |
| skiffs dead | "skiffs neutralised" | 5 |
| skiffs dead **OR** 2100 | EW jamming popup + intel, jammer spawns, arms trigger 7 | 6 |
| 2400 (armed only) | Commando helo + escort spawn 15 NM out at Telegraph 5 | 7 |
| ~2540 | Helo inside 10 NM of boarding pt → "inbound" warning | 8 |
| ~2830 | Helo inside 3 NM → "COMMANDOS ARE BOARDING" | 9 |
| 3050 **and** helo still inside 4 NM | Cargo lost, defeat | 10 |
| any | Helo destroyed → threat clear, trigger 10 disabled | 11 |
| ~4100 | Vagabond inside 3 NM of Alpha → victory | 14 |

Effective boarding grace window is ~220 s (helo arrives ~2830, deadline 3050),
close to the 200 s in SCRIPT.md.

## Deviations from SCRIPT.md, and why

1. **Location is the Gulf of Aden, not the Gulf of Guinea.** Every coordinate in
   your backbone and both `.unitgroup` presets sits at 12°N / 43–47°E, and the
   preset units are Iranian (`ir_fab_boghammar`, `ir_pt_parvin`) and
   French/Iraqi (`fr_sa-321`, `iqaf_md500`). All mission text was written to
   match the coordinates. Say the word if you want the text moved to West Africa
   instead — the geometry does not change, only the prose and the map center.

2. **Deployment zone moved and shrunk.** Your `Zone1` was centred at
   12.354523/47.425778 — about 220 NM east of the rendezvous, roughly 13 hours of
   steaming for a corvette. It is now 16 × 12 NM centred at 12.3167/43.75, about
   6 NM WSW of the rendezvous. The name "Zone Alpha" moved onto a new map-symbol
   circle at the actual NavPoint Alpha destination.

3. **Escort leg shortened to 15 NM.** At merchant speed a 45 NM leg is nearly
   three hours. 15 NM gives roughly a 70-minute mission.

4. **The three pirate skiffs are hostile from mission start**, not neutrals that
   flip sides. They sit idle at Telegraph 1 inside the neutral cluster, mixed in
   with a `ir_fab_boghammar` and a `ir_pt_parvin` that are genuinely neutral, and
   they only charge when trigger 4 fires. This keeps the "you cannot tell them
   apart" tension while avoiding `Action_UnitTransferToTaskforce` green→red,
   which is not demonstrated anywhere in the vanilla campaign (only blue→green
   and red→red appear there). If you would rather have the on-screen side flip,
   the swap is two lines in trigger 4 — but test it first.

5. **No relative timer** — see limits below.

## Editor limits hit

- **There is no relative-time condition.** `Condition_*_Type=Time` is always
  absolute seconds from mission start, so a literal "start a 200-second timer
  when X happens" cannot be written. Trigger 10 fakes it with
  `<HeloStillOverhead> AND <Deadline>`: the deadline is an absolute clock time
  chosen to land ~220 s after the helo's scheduled arrival, and the area
  condition means killing the helo cancels the loss. That is why trigger 7 fires
  the helo at a fixed t=2400 instead of keying off the skiffs — a deterministic
  launch is what makes a fixed deadline behave like a timer.
- **Area conditions are fixed circles, not "distance to unit".** The boarding
  check is a circle at the Vagabond's *expected* position, not on the Vagabond
  itself. The radius is 4 NM to absorb drift. If you slow the Vagabond down, move
  the boarding point.
- **No jamming action exists.** The EW spike is done narratively (popup + intel)
  plus a real `Action_EnableDisableSensorSystems=Disable` on the Vagabond, which
  is what SCRIPT.md describes for her nav suite. The jammer itself is a real
  airframe orbiting at 30,000 ft so the player has something to find.
- **I cannot validate `Type=` / `VariantReference=` / `SquadronReference=` values.**
  StreamingAssets is not in this repo, so every unit reference here came from the
  vanilla Pacific Strike files, your `.unitgroup` presets, or `fleet.csv`. See
  the unverified list below.

## Needs verifying against the game files

| Field | Value | Note |
|---|---|---|
| `ir_fab_boghammar`, `ir_pt_parvin` | `VariantReference=Default` | preset JSON says `_variantId: 0`; `Default` is the usual mapping but unconfirmed |
| `fr_sa-321`, `iqaf_md500` | `SquadronReference=Default` | presets carry no squadron info |
| `fr_sa-321` | `LoadoutVariant=Empty` | from the preset; unarmed transport, which suits a boarding threat |
| `iqaf_md500` | `LoadoutVariant=Recon` | from the preset |
| `usn_ea-6b` | `SquadronReference=Squadron6` | taken from vanilla `campaign.ini` reward list; no loadout set |
| `ir_pf_bayandor` | `Variant1` | anchor only — the generator replaces this hull, so a wrong variant is low risk |
| roster variants | `Variant1` for everything except `usn_dd_gearing` | **this one matters** — a bad variant means the hull never shows in Task Force Builder |
| `Action_UnitTelegraph`, `Action_UnitVelocityInKnots` | triggers 2 and 4 | documented in the community guide but unused in vanilla; both are set for redundancy |

## Not built

- Briefing XML panes. Vanilla Pacific Strike uses `MissionIntro_en` in
  `campaign.ini` instead of briefing files, so that is what this uses.
- Ribbons and medals — they need PNG art, and awarding an undefined ribbon ID
  breaks the debrief. `commander_settings.ini` has no `[TaskForceRibbons]` block
  on purpose.
- Localisation. English only.
