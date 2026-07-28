# Phantom Wake — presentation layer, work front

Scope of this document: everything that makes the campaign *look* like a shipped
campaign rather than a mission `.ini`. None of it affects gameplay logic, all of it is
XAML + PNG, and none of it is built yet.

The reference is the vanilla `campaigns/pacific-strike-task-force/`. What follows is
what that campaign actually contains, how the pieces are wired, and what Phantom Wake
needs in dependency order.

> **Decided: English only for now. Russian localisation happens at the end, once the
> English text is frozen.** Every XAML page and every `_en` ini key is authored once.
> Do not add `_ru` keys, `art/ru/` folders or `BriefingText_ru.xml` files as you go —
> see WP8 for why, and for what "frozen" has to mean before that pass can start.

---

## 1. What "оформление" actually consists of

Inventory of the vanilla campaign, so the size of the job is honest:

| Layer | Vanilla count | What it is |
|---|---|---|
| Campaign background | 1 PNG | full-bleed art behind the campaign map |
| Mission sheets | 14 PNG (1184×640) | the card image for each mission on the campaign map |
| Story slideshows | 8 XAML + ~8 PNG | multi-page prologue, arrow-navigated |
| News / document events | 19 XAML + ~14 PNG | newspapers, JCS message traffic, intel summaries, sitreps |
| Debrief scoreboard | 2 XAML + 3 PNG | task force combat record, live-bound to campaign state |
| Briefings | 14 folders, 110 XAML, 38 PNG | per mission: text pane + map pane, per language |
| Campaign rules page | 4 XAML | tabbed rules/help page shown in the campaign UI |
| Ribbons | 18 PNG (224×56) | award ribbons for the commander's rack |
| Medals & citations | 16 PNG (431×135 and larger) | medal art, citation seals, letterhead |
| Tile backgrounds | 4 PNG | `bkg_paper`, `bkg_newsprint`, event tile art |
| Unit blurbs | 8 INI | `unit_roster_descriptions_<lang>.ini` — **already generated from CSV** |

That is 91 XAML and 81 PNG under `art/` alone, before briefings.

Those counts are for **4 languages**. Phantom Wake is English-only until the end, so
divide every XAML figure by four: 27 event pages instead of 91, and 2 briefing files
per mission instead of 8. PNG counts barely move — only a handful of vanilla images
carry `_de` / `_ru` text variants, and the rest are shared across all languages.

The English-only equivalent of the table above is roughly **35 XAML and 70 PNG** for a
campaign of Pacific Strike's length, and far less than that for the first few
contracts.

---

## 2. How the presentation layer is wired

Discovered by reading the vanilla files. Not in either official guide.

### Assets are resolved by basename

```ini
; campaign.ini, inside a [MissionN] block
AssetsPath_en=campaigns/PhantomWake/art
FilePath_en=campaigns/PhantomWake/art/pw01_contract_brief.xml
TileImagePath_en=campaigns/PhantomWake/art/bkg_tile_message.png
```

Everything under `AssetsPath` becomes addressable in XAML by **filename without
extension**:

```xml
<Image Source="{Binding Assets[bkg_paper]}"/>
```

### Events are XAML pages, opened by the campaign timeline

Root element is `Viewbox`, `Grid`, `ScrollViewer` or `Page`, with:

```xml
xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
xmlns:local="clr-namespace:SeapowerUI"
```

Simplest possible event is 7 lines — one full-bleed image:

```xml
<Viewbox xmlns="..." xmlns:x="..." HorizontalAlignment="Center" VerticalAlignment="Center">
  <StackPanel>
    <Image Source="{Binding Assets[19850626_breakingnews_image]}"/>
  </StackPanel>
</Viewbox>
```

### Multi-page slideshows

Pages chain to each other with `OpenFileCommand`. There is no slideshow container —
each page just knows its neighbours:

```xml
<Button Content="&gt;" Style="{StaticResource SlideArrowButton}"
        Command="{Binding OpenFileCommand}"
        CommandParameter="campaigns/PhantomWake/art/pw_intro_2.xml"/>
```

`SlideArrowButton` is a style the campaign defines itself in `<Grid.Resources>` — copy
it from `art/s01_window_1.xml`.

### Live campaign state is bindable

This is the interesting part. A debrief page can read the player's actual task force:

```
DataSource.PersistentData[PlayerTaskForceName]
DataSource.TaskForceCommanderShipsSunk
DataSource.TaskForceCommanderSubmarinesSunk
DataSource.TaskForceCommanderAircraftShotDown
DataSource.TaskForceScoreboardIslandsCaptured
DataSource.TaskForceScoreboardSurfaceUnits      (list, use ItemsControl)
DataSource.TaskForceScoreboardSurfaceUnitCount
DataSource.TaskForceScoreboardHasSurfaceUnits   (bool, drives Visibility)
DataSource.TaskForceScoreboardSquadrons
DataSource.TaskForceScoreboardSquadronCount
DataSource.TaskForceScoreboardHasSquadrons
```

Per-unit bindings inside a `TaskForceScoreboardSurfaceUnits` item template:
`NationFlag`, `DisplayNameWithQuantity`, `TypeLine`, `CrewSkill`, `ProficiencyDisplay`,
`BattleStarMarkers`, `BattleStarText`, `UnitType`, `VariantIndex`.

Built-in converters: `UppercaseConverter`, `CollapsedConverter`,
`InverseCollapsedConverter`, `CrewSkillToBrushConverter`, `IniToProfileConverter`.

### Built-in NTDS symbol resources

Do not draw NATO symbols by hand — the game exposes them as `Path` geometry:

```xml
<Path Data="{StaticResource NTDS.Enemy.Surface}"
      Stroke="{StaticResource NTDS.HostileColour}"
      StrokeThickness="{DynamicResource ContactIconThickness}"/>
```

Available: `NTDS.Allied.{Air,Airbase,Helicopter,SAM,Submarine,Surface}`,
`NTDS.Enemy.{AAA,Air,Airbase,Helicopter,Installation,Radar,Submarine,Surface}`,
`NTDS.Unknown.{Submarine,Surface}`, plus
`NTDS.FriendColour` / `NTDS.HostileColour` / `NTDS.UnknownColour`.
Theme keys `Font.Size.Header` and `Brush.Border.FocusAccent` also exist.

### Token substitution works inside briefing XAML

```xml
<Run Text="{TaskForceName}:"/>
{TaskForceVesselSummaryRuns}
```

So a briefing map can print the player's actual, current force composition. Same
`{TaskForceName}` token also works in mission popup messages.

### Briefings are found by folder convention, not by ini keys

`MissionBriefingLeftPane` / `MissionBriefingRightPane` from the community guide appear
in **zero** vanilla mission files. The convention is:

```
missions/
  01_rusted_sea.ini
  01_rusted_sea_briefing/
    BriefingText_en.xml       <- left pane, the operations order
    BriefingMap_en.xml        <- right pane, the map
    <mission art>.png
```

`BriefingMap` is a `Canvas` of fixed pixel size with a base map `Image` and absolutely
positioned overlays (`Canvas.Left` / `Canvas.Top`) for insets, labels and NTDS symbols.
Vanilla base maps are 1095×662; the far-view inset is a separate PNG.

`campaign_rules_<lang>.xml` at the campaign root is picked up the same way, with no ini
key. It is a `Page` with a `TabControl` — the in-game rules/help screen.

---

## 3. Creative direction for Phantom Wake

Pacific Strike's visual language is a national navy: JCS message centre letterhead,
Department of the Navy seals, newspaper front pages, USN battle stars.

Phantom Wake is a PMC operating in the grey. The paperwork should be **corporate, not
military**, and that difference is the whole aesthetic:

- Contracts instead of operation orders. A scope-of-work page with a client reference
  number, a fee, a penalty clause, and a signature block from a company that does not
  legally exist.
- Invoices and expense ledgers instead of medals. Ordnance expended, hull-hours,
  repair quotes. Reinforces "every missile fired is money burned".
- Intercepted traffic instead of official dispatches — signals the company was never
  supposed to read, arriving with the sender redacted.
- Trade-press clippings instead of national newspapers. *Lloyd's List*-style shipping
  notices reporting the incident from the outside, never naming the company.
- Awards are internal and slightly grubby: company commendations, hazard bonuses, a
  crew's own painted scoreboard. Ribbon art can be plainer and cheaper to draw than
  the vanilla national racks.

The `NavalMessage` popup style with `Template=USAUSNavy` is available and free, but
using it undercuts the fiction. A custom XAML letterhead is worth the effort here.

---

## 4. Work packages, in dependency order

Effort is rough relative sizing, not hours.

### WP0 — foundation (blocks everything)

- [ ] Create `campaigns/PhantomWake/art/` and decide the asset naming scheme
      (suggest `pw_<nn>_<slug>.png`, no spaces, since basenames become binding keys).
- [ ] Pick the palette and one display typeface direction (vanilla leans
      `Roboto` / `Roboto Mono` / `Courier New` — all safe, all present).
- [ ] Copy `SlideArrowButton` style out of vanilla `art/s01_window_1.xml` into a
      Phantom Wake page as the shared nav control.
- **Blocks:** every other package.

### WP1 — campaign map presentation (highest value per unit of effort)

- [ ] `BackgroundImage` for `[Campaign]` — one full-bleed image.
- [ ] Mission sheet for contract 01, 1184×640, wired via `MissionImage_en`.
- [ ] `TileImagePath_en` tiles for message and document events (2 PNG).
- **Depends on:** WP0. **Unblocks:** the campaign screen stops looking empty.
- This is the cheapest visible win: three images and two ini lines.

### WP2 — briefing for contract 01

- [ ] `missions/01_rusted_sea_briefing/BriefingText_en.xml` — SMEAC-shaped, but
      rewritten as a contract: Client, Scope, Execution, Known Threats, Assets, Terms.
- [ ] `missions/01_rusted_sea_briefing/BriefingMap_en.xml` — Gulf of Aden chart with
      the convoy axis, the four beats, and NTDS symbols for the ambush and air threat.
- [ ] Base chart PNG (1095×662) + far-view inset PNG + one photo inset.
- [ ] Use `{TaskForceVesselSummaryRuns}` for the friendly force box so the briefing
      always matches what the player actually bought.
- **Depends on:** WP0. Geometry is already fixed — coordinates are in
      `missions/01_rusted_sea/BUILD_NOTES.md`, and the map symbols already exist in the
      mission ini.

### WP3 — prologue slideshow

- [ ] 3–5 XAML pages establishing the company: how it formed, who the outcasts are,
      why anyone hires them. Arrow-navigated via `OpenFileCommand`.
- [ ] Supporting art per page.
- [ ] New `[MissionN]` entries of `Type=FreeEvent` in `campaign.ini` with `Parents=`
      wiring, placed *before* the contract-01 entry, and `NumberOfMissions` bumped.
- **Depends on:** WP0.
- Note: `FreeEvent` entries occupy the same `[MissionN]` numbering as real missions,
      so adding a prologue renumbers everything downstream. Do this **before** more
      missions exist, not after.

**Where to read the vanilla one.** Pacific Strike's prologue is 7 pages, entry point
declared in `campaign.ini` `[Mission1]`:

```ini
[Mission1]
Type=FreeEvent
IsUnlocked=True
UseAuthoredNavigation=True
AssetsPath_en=campaigns/pacific-strike-task-force/art
FilePath_en=campaigns/pacific-strike-task-force/art/s01_window_1.xml
TileImagePath_en=campaigns/pacific-strike-task-force/art/bkg_tile_message.png
```

The chain, each page hard-linking its neighbours — there is no slideshow container and
no index anywhere:

```
s01_window_1  →  2  →  3  →  4  →  5  →  6  →  7
   (map)      (leaders) (fleet) (tanks) (offensive) (drydock) (title)
```

Read in this order:

1. **`art/s01_window_1.xml`** — the template. 72 lines, of which ~40 are the
   `SlideArrowButton` `ControlTemplate` in `<Grid.Resources>`. Copy that block once and
   every later page is ~25 lines. The actual content is the last `<StackPanel>`: an
   `Image`, an italic caption, a heading, and a body `TextBlock`.
2. **`art/s01_window_7.xml`** — the last page, to see how the chain terminates.
3. **`art/s01_window_0.xml`** — *not part of the chain.* Nothing links to it and
   `campaign.ini` never references it. It is an older, simpler layout: `ScrollViewer` +
   `Border`, a heading, an image, text, and one `Next` button. Worth reading precisely
   because it is the minimum viable version — if the arrow-slide chrome is not wanted,
   this is a 28-line page.

Details that are easy to miss:

- The `1 / 7` page counter is **hardcoded text** on every page, not a binding. Insert
  a page in the middle and all seven counters need editing by hand.
- On page 1 the back arrow and on page 7 the forward arrow are inert decorations — a
  plain `TextBlock` at low opacity rather than a `Button`. Only real navigation is a
  `Button` with `Command="{Binding OpenFileCommand}"`.
- `CommandParameter` is a **full path from the mod root**, not relative to the page.
- Canvas is `Width="1560" Height="920"` inside a `Viewbox Stretch="Uniform"`, so pages
  scale to any window. Author to 1560×920 and stop worrying about resolution.
- Localised copies live in `art/ru/`, `art/de/`, `art/ja/` with their own copies of the
  whole chain — the single strongest argument for the English-only decision above.

### WP4 — document events between contracts

- [ ] Contract offer / scope-of-work page (reusable template, one per contract).
- [ ] Post-action invoice + expense ledger page (reusable).
- [ ] Intercepted-traffic page for the mystery thread opened by contract 01 — who paid
      for a jammer and an assault transport over a rusted container ship.
- [ ] `bkg_paper` / `bkg_newsprint` equivalents in the PMC visual language.
- **Depends on:** WP0, WP3 (numbering).

### WP5 — debrief scoreboard

- [ ] Port `art/event_task_force_77_combat_record.xml` to Phantom Wake branding.
      It is the single highest-effort XAML file in the campaign (192 lines) but almost
      all of it is bindings that work unchanged.
- [ ] Scoreboard header + results art.
- **Depends on:** WP0. Best done once several contracts exist and there is a record
      worth showing.

### WP6 — awards

- [ ] Decide the award set. Suggest 4–6, not 18.
- [ ] Ribbon PNGs at 224×56.
- [ ] Medal / citation PNGs at 431×135 plus a company seal.
- [ ] `[TaskForceRibbons] RibbonIds=` + one `[Ribbon_<id>]` block each in
      `commander_settings.ini`, with citation text.
- [ ] `TaskForceModeRibbonAwards=` on the relevant `[MissionN]`.
- **Warning:** awarding an ID with no `[Ribbon_<id>]` definition breaks the debrief.
      Nothing here can be half-done — either a ribbon is complete or it is absent.
- **Depends on:** WP0.

### WP7 — campaign rules page

- [ ] `campaign_rules_en.xml` — `Page` + `TabControl`, explaining PMC economy, ROE,
      persistence, and what losing a hull actually costs. Vanilla file is 334 lines and
      is a straight structural template.
- **Depends on:** WP0. Lowest priority, highest word count.

### WP8 — Russian localisation (last, deliberately)

**Decided: nothing here happens until the English text is frozen.** Every text change
made before this point costs one edit; every text change made after costs two.

"Frozen" means: no more wording passes on mission popups, briefings or event pages,
and the campaign has been played through at least once so the text has survived
contact with the game.

When it starts, the pass covers four separate surfaces — none of them optional:

- [ ] **Mission ini.** Duplicate the whole `[Language_en]` block as `[Language_ru]`.
      Every key: `Name`, `Description`, every `*Message`, every `*Intel`,
      `StartForecast`, every `Objective_*`, every `MapSymbol_*Label_ru`,
      `Zone*Label_ru`, every `Trigger*AreaLabel`, and the `*NameOverride` /
      `*ShortNameOverride` pairs. Vanilla localises ship names too.
- [ ] **campaign.ini.** `_ru` twins for `Name`, `Description`, `MissionIntro`,
      `MissionResupplyRules`, `MissionSpecialNote`, `MissionSequenceName`,
      `MapShortName`, `TaskForceModeBuilderSituation`, `TaskForceModeDebriefNotice*`,
      plus `AssetsPath_ru` / `FilePath_ru` / `TileImagePath_ru` per event.
- [ ] **XAML.** A `_ru` copy of every event page and every briefing pane, plus an
      `art/ru/` folder. Vanilla keeps localised pages in `art/ru/` and points
      `FilePath_ru` at them.
- [ ] **Roster blurbs.** `unit_roster_descriptions_ru.ini`. This one is cheap: add a
      `DescriptionRu` column to the CSVs and teach `tools/build_roster.py` to emit the
      second file — no hand-editing.
- [ ] **Localised art.** Only images with baked-in text need a `_ru` variant. Vanilla
      has ~8 of 81. Keep text out of PNGs wherever possible and this stays near zero.

**Depends on:** WP1–WP7 complete and signed off.

Vanilla is the warning: 110 briefing XAML files for 14 missions, because every pane
exists four times. Phantom Wake stays at one copy until the very end on purpose.

---

## 5. Suggested order

```
WP0 → WP1 → WP2 → WP3 → WP4 → WP6 → WP5 → WP7 → WP8
```

WP1 and WP2 together take the campaign from "a mission file" to "looks like a
campaign". Everything after that is depth.

---

## 6. Decisions made

- **Language scope — English only, Russian at the end (WP8).** Author every XAML page
  and every ini key once. No `_ru` keys, no `art/ru/`, no `BriefingText_ru.xml` until
  the English text is frozen.

## 7. Still open

1. **Art pipeline.** Hand-drawn, AI-generated, or photographic/archival? Mission sheets
   and event art are the bulk of the PNG count.
2. **Award set size.** 4–6 company commendations, or a full national-style rack?
3. **Prologue length.** A 3-page slideshow is cheap; Pacific Strike's is 8 pages.
4. **Does the campaign get a proper campaign map background**, or is `DisplayFormat`
   something other than `MapView` for a mercenary outfit with no theatre of operations?
5. **How much text lives in PNGs.** Every image with baked-in lettering becomes a
   second image at WP8. Keeping text in XAML `TextBlock`s instead of in the art makes
   the Russian pass dramatically cheaper.

---

## 8. Not blocked on any of this

The gameplay layer is complete and testable without a single PNG. Presentation work
can start whenever, and none of it can break mission logic — the only files it touches
are `campaign.ini` display keys, `commander_settings.ini` award blocks, and new XAML
and PNG under `art/` and `missions/*_briefing/`.
