# Campaign Intel Documents (FreeEvent) — authoring guide

How to build the between-mission paper the player reads on the campaign map: SITREPs,
INTSUMs, HUMINT reports, BDA reports, intercepts, newspapers, slideshows.

Everything here is verified against `campaigns/pacific-strike-task-force/` (the vanilla
Task Force Mode campaign): `campaign.ini` + the 30-odd XAML files in its `art/` folder.
The template file the game ships as a starting point is
`campaigns/pacific-strike-task-force/art/19850808_sitrep.xml` — its first line says so,
and it is deliberately *not* wired into `campaign.ini`. Copy it, don't edit it.

Related: `docs/briefing_setup_guide.md` covers **mission** briefing panes
(`MissionBriefingLeftPane=`), which is a different system with a different XAML dialect.
This document is about **campaign timeline events**.

---

## 1. What a document event is

In `campaign.ini`, the campaign timeline is a list of `[MissionN]` blocks. Two kinds:

| `Type=` | What it is |
|---|---|
| `Mission` | a playable mission, `MissionFile=` points at a `.ini` |
| `FreeEvent` | a document — no gameplay, `FilePath_XX=` points at a XAML file |

Both are numbered in the same `[MissionN]` sequence and both count toward
`NumberOfMissions`. Pacific Strike has `NumberOfMissions=31` for ~14 playable missions —
the other 17 are documents. Documents are the cheap way to carry campaign narrative,
so vanilla uses roughly one document per mission.

The graph is wired with `Parents=` (the `[MissionN]` number, not the mission name).
A document node between two missions is what forces the player to read it.

---

## 2. Wiring it into `campaign.ini`

Minimal English-only block:

```ini
[Mission8] # Doc: JCS SITREP - Palawan
Type=FreeEvent
IsUnlocked=False
IsComplete=False
Parents=7

Name_en=JCS SITREP\n9 July 1985
Description_en=Palawan invasion changes tasking
AssetsPath_en=campaigns/pacific-strike-task-force/art
FilePath_en=campaigns/pacific-strike-task-force/art/19850709_jcs_sitrep_palawan.xml
TileImagePath_en=campaigns/pacific-strike-task-force/art/bkg_tile_message.png
```

| Key | Meaning |
|---|---|
| `Type=FreeEvent` | document, not a mission |
| `IsUnlocked` | `True` only on the very first node (`[Mission1]`); everything else `False` |
| `IsComplete` | always `False` in a shipped campaign |
| `Parents=N` | unlocks after event N. Two children with the same `Parents` = a branch |
| `Name_XX` | tile caption. `\n` is a line break — vanilla puts the date on line 2 |
| `Description_XX` | subcaption on the tile. May be empty, key still present |
| `AssetsPath_XX` | **directory** scanned for images. Not a file |
| `FilePath_XX` | the XAML document |
| `TileImagePath_XX` | timeline tile art. `bkg_tile_message.png` for paperwork, `bkg_tile_newspaper.png` for press |
| `UseAuthoredNavigation=True` | the document draws its own next/prev buttons (§6). Omit for single-page docs |

Paths are relative to the game's `StreamingAssets` root, always starting
`campaigns/<campaign>/…`. They are **not** relative to `campaign.ini`.

`FreeEvent` blocks take no `RequiredResult`, no Task Force Mode keys and no
`MissionIntro`. Those are `Type=Mission` only.

### Inserting a document into an existing campaign — the renumbering trap

`[MissionN]` numbers are the identity used by `Parents=`. Inserting a document in the
middle means renumbering **every** later block *and* every `Parents=` that points past
the insertion point, then bumping `NumberOfMissions`. Do it in one pass, bottom-up.

Cheaper alternative: append the new block at the end with the number
`NumberOfMissions + 1` and set its `Parents=` to whatever should precede it. The
timeline is a graph, not an array — the block order in the file does not have to match
the display order. Then bump `NumberOfMissions`.

A `NumberOfMissions` that does not match the block count silently drops nodes, same as
`NumberOfTriggers` in a mission file.

---

## 3. The document is WPF XAML, not the briefing dialect

Mission briefing panes accept a bare `<TextBlock>`. Campaign documents do not — they are
real WPF pages with `Grid`, `Border`, `StackPanel`, `ImageBrush`, `Viewbox`, styles and
data binding. Everything below is standard WPF.

Two root patterns, both used in vanilla:

| Root | When | Behavior |
|---|---|---|
| `<ScrollViewer>` | text documents of unknown length (all SITREPs) | fixed font size, page scrolls |
| `<Page><Viewbox>` | fixed-layout pages (newspaper, intercept, `Height=` set) | whole page scales to fit the window |

`Viewbox` guarantees the layout is never cut off but shrinks text on small windows.
`ScrollViewer` keeps text readable and lets long documents run. **Default to
`ScrollViewer` for a SITREP.**

Escaping: it is XML. `&lt;` `&gt;` `&amp;` for `<` `>` `&`. `<LineBreak/>` for newlines
inside a `TextBlock`; raw newlines in the source collapse to a single space.

---

## 4. The naval-message template, dissected

This is the shape of `19850808_sitrep.xml`, `19850701_intel_event.xml`,
`19850808_intel_event.xml`, `19850709_jcs_sitrep_palawan.xml`,
`19850819_coastwatcher_report.xml`, `19851001_palawan_bda_report.xml` and
`19850921_17mau_targeting_intel.xml` — seven documents, one layout.

```xml
<ScrollViewer xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
  xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
  xmlns:local="clr-namespace:SeapowerUI">

  <!-- the sheet of paper -->
  <Border HorizontalAlignment="Center" VerticalAlignment="Center" Width="900"
          TextElement.FontFamily="Courier New" TextElement.Foreground="Black"
          TextElement.FontSize="16" Padding="45">
    <Border.Effect><DropShadowEffect /></Border.Effect>
    <Border.Background>
      <ImageBrush ImageSource="{Binding Assets[bkg_paper]}" Stretch="UniformToFill"/>
    </Border.Background>

    <StackPanel Orientation="Vertical">

      <!-- masthead: NAVAL MESSAGE | classification | NAVY DEPARTMENT -->
      <Grid>
        <Grid.RowDefinitions><RowDefinition Height="Auto"/></Grid.RowDefinitions>
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="Auto"/>
          <ColumnDefinition Width="3*"/>
          <ColumnDefinition Width="Auto"/>
        </Grid.ColumnDefinitions>
        <TextBlock Grid.Column="0" Text="NAVAL MESSAGE" FontFamily="Arial Narrow Bold" FontSize="26" FontWeight="Bold" TextAlignment="Left"/>
        <TextBlock Grid.Column="1" Text="*******S E C R E T*******" Margin="40,0,40,0" FontWeight="Bold" TextAlignment="Center"/>
        <TextBlock Grid.Column="2" Text="NAVY DEPARTMENT" FontFamily="Arial Narrow Bold" FontSize="26" FontWeight="Bold" TextAlignment="Right"/>
      </Grid>

      <!-- double rule under the masthead -->
      <Rectangle HorizontalAlignment="Stretch" Height="1" Fill="Black" Margin="0,0,0,1"/>
      <Rectangle HorizontalAlignment="Stretch" Height="1" Fill="Black" Margin="0,0,0,10"/>

      <!-- message body: 4 columns (label | gutter | value | right-hand field) -->
      <Grid>
        <Grid.RowDefinitions>
          <!-- one RowDefinition per Grid.Row used below - see the gotcha in §8 -->
          <RowDefinition Height="Auto"/>   <!-- x25, one per row -->
        </Grid.RowDefinitions>
        <Grid.ColumnDefinitions>
          <ColumnDefinition Width="Auto"/>  <!-- FM / TO / INFO / SUBJ -->
          <ColumnDefinition Width="10"/>    <!-- gutter -->
          <ColumnDefinition Width="*"/>     <!-- addressees, body -->
          <ColumnDefinition Width="Auto"/>  <!-- routing line -->
        </Grid.ColumnDefinitions>

        <TextBlock Grid.Row="1" Grid.ColumnSpan="4" HorizontalAlignment="Left">
          IMMEDIATE<LineBreak/>
          O 082100Z AUG 85
        </TextBlock>
        <TextBlock Grid.Row="1" Grid.Column="3" Text="ZYUW RUHGOAA0777 2202100"/>

        <TextBlock Grid.Row="3"  Grid.Column="0" Text="FM"/>
        <TextBlock Grid.Row="3"  Grid.Column="2" Text="CTF 77"/>
        <TextBlock Grid.Row="4"  Grid.Column="0" Text="TO"/>
        <TextBlock Grid.Row="4"  Grid.Column="2" Text="TF 77, CVW-9, NAVFAC DARWIN"/>
        <TextBlock Grid.Row="11" Grid.Column="0" Text="INFO"/>
        <TextBlock Grid.Row="11" Grid.Column="2" Text="CINCPACFLT"/>
        <TextBlock Grid.Row="13" Grid.Column="0" Text="SUBJ:"/>
        <TextBlock Grid.Row="13" Grid.Column="2" Text="SITREP 09/1200Z - 10/1200Z - MSG NO 047/85"/>

        <!-- numbered paragraphs: one TextBlock per paragraph, ColumnSpan=4 -->
        <TextBlock Grid.Row="15" Grid.ColumnSpan="4" TextWrapping="Wrap">
          <LineBreak/>SECRET<LineBreak/><LineBreak/>
          1. (S) STRATEGIC SITUATION: ...
          <LineBreak/>
        </TextBlock>
        <TextBlock Grid.Row="16" Grid.ColumnSpan="4" TextWrapping="Wrap">
          2. (S) MISSION: ...
          <LineBreak/>
        </TextBlock>

        <!-- a heading + its indented bullets = two TextBlocks -->
        <TextBlock Grid.Row="17" Grid.ColumnSpan="4" TextWrapping="Wrap">
          3. (S) TF 77 STATUS:
        </TextBlock>
        <TextBlock Grid.Row="18" Grid.ColumnSpan="4" TextWrapping="Wrap" Margin="20,0,0,0">
          - KITTY HAWK remains at Puget Sound for repairs.<LineBreak/>
          - Elements of CVW-9 operating shore-based from Darwin.<LineBreak/>
        </TextBlock>

        <TextBlock Grid.Row="24" Grid.ColumnSpan="4" TextWrapping="Wrap">
          SIGNED: CAPT C. F. ROBINSON<LineBreak/>
          CTF 77<LineBreak/><LineBreak/>
          SECRET<LineBreak/>
          DO NOT DECLASSIFY WITHOUT APPROVAL OF ADDRESSEE
        </TextBlock>
      </Grid>
    </StackPanel>
  </Border>
</ScrollViewer>
```

Rules the template encodes, worth keeping:

- **`TextWrapping="Wrap"` on every body paragraph.** Without it the line runs off the
  sheet — the single most common mistake.
- **One `TextBlock` per numbered paragraph.** Do not put the whole message in one block;
  the row grid is what gives the vertical rhythm.
- Indented sub-bullets are a separate `TextBlock` with `Margin="20,0,0,0"`.
- A trailing `<LineBreak/>` inside each paragraph is the paragraph spacing.
- Classification banner repeats at top and bottom of the body. Vanilla is strict about it.
- `FontSize="16"` is repeated on individual `TextBlock`s even though the `Border` sets
  `TextElement.FontSize="16"` — harmless, and it is how the template ships.

### The message header fields (real-world DIM format)

| Line | Content | Example |
|---|---|---|
| precedence | `ROUTINE` / `PRIORITY` / `IMMEDIATE` / `FLASH` | `IMMEDIATE` |
| DTG | `O DDHHMMZ MON YY` — day, time Zulu, month, year | `O 082100Z AUG 85` |
| routing | comms-station gibberish, decorative | `ZYUW RUHGOAA0777 2202100` |
| `FM` | originator, optionally with location | `CTF 77 DARWIN NT AU` |
| `TO` | action addressees | `TF 77, CVW-9, NAVFAC DARWIN, 10 SQN RAAF` |
| `INFO` | copy-to addressees | `CINCPACFLT PEARL HARBOR HI` |
| `SUBJ` | report type + covering period + serial | `SITREP 09/1200Z - 10/1200Z - MSG NO 047/85` |
| `BT` | "break text", separates header from body. Optional — `19850808_intel_event.xml` has it, `19850808_sitrep.xml` doesn't | `BT` |

Body paragraphs are numbered and each carries its own classification marking `(S)`,
`(C)`, `(U)`. Keep the paragraph skeleton consistent across documents of the same type;
a SITREP that always runs SITUATION → MISSION → OWN STATUS → ALLIED → INTEL/THREAT →
REMARKS reads as a real recurring report.

---

## 5. Assets and dynamic text

### Images

`AssetsPath_XX` in `campaign.ini` names a **directory**. Every image in it becomes
available as `Assets[<filename without extension>]`:

```xml
<ImageBrush ImageSource="{Binding Assets[bkg_paper]}" Stretch="UniformToFill"/>
<Image Source="{Binding Assets[19850626_breakingnews_image]}"/>
```

`bkg_paper.png` → `Assets[bkg_paper]`. Case matters. A missing key renders nothing and
logs nothing — check the spelling first when a background comes up blank.

Shared backgrounds already in `pacific-strike-task-force/art/`: `bkg_paper.png`
(typewriter paper), `bkg_newsprint.png`, `bkg_tile_message.png`, `bkg_tile_newspaper.png`.

### Putting a photo or map inside a naval-message document

The binding is the same everywhere, so **a paper document can embed images exactly like
the newspaper does** — a recon photo, an annotated chart, a damage assessment plot.
Vanilla never does it (all ten `bkg_paper` documents contain zero `<Image>` elements;
every image in the campaign lives in a newspaper, a breaking-news PNG, a slideshow page
or the scoreboard), but nothing in the format prevents it. `19850626_newspaper_event.xml`
is the working reference for image + caption:

```xml
<StackPanel Grid.Column="0" Grid.Row="1" Orientation="Vertical" VerticalAlignment="Top">
  <Image Source="{Binding Assets[19850626_newspaper_event_tanks]}" Stretch="Uniform"/>
  <TextBlock Text="U.S Army tanks move east towards the frontline on Wednesday morning. (AP Wire Photo)"
             TextWrapping="Wrap" TextAlignment="Left" Margin="0,10,0,0"/>
</StackPanel>
```

Dropped into the message grid of the SITREP template, as an annex after the last
paragraph:

```xml
<!-- annex: needs its own RowDefinition, like any other row -->
<StackPanel Grid.Row="25" Grid.ColumnSpan="4" Margin="0,10,0,0">
  <TextBlock Text="ANNEX A - RECONNAISSANCE PHOTOGRAPH, LOMBOK ANCHORAGE 191430Z"
             FontWeight="Bold" TextWrapping="Wrap"/>
  <Border BorderThickness="1" BorderBrush="Black" Margin="0,8,0,0" HorizontalAlignment="Center">
    <Image Source="{Binding Assets[19850819_lombok_recon]}" Stretch="Uniform"
           MaxWidth="700" HorizontalAlignment="Center"/>
  </Border>
  <TextBlock Text="FIG 1. Two KRIVAK II at anchor, bearing 070 from OP GANNET. NPIC EVAL: CONFIDENT."
             FontStyle="Italic" FontSize="14" TextWrapping="Wrap" Margin="0,6,0,0"/>
</StackPanel>
```

Rules for images on a paper sheet:

- **Constrain the width.** The sheet is `Width="900"` with `Padding="45"`, so usable
  width is **810 px**. An unconstrained `<Image>` renders at native pixel size and will
  overhang the paper. Use `Stretch="Uniform"` plus `MaxWidth` (or `Width`) — the
  scoreboard does exactly this: `Stretch="Uniform" Width="600"`.
- Inside the message `Grid`, an image needs `Grid.Row="N"` + `Grid.ColumnSpan="4"` and a
  matching `RowDefinition`, same as any `TextBlock` (§8). Easier: wrap image + heading +
  caption in one `StackPanel` and place that in a single row.
- Under a `ScrollViewer` root the image renders at its real size and the page scrolls.
  Under `Page`+`Viewbox` the whole sheet — image included — scales to the window, so a
  tall image shrinks the text with it. Another reason to prefer `ScrollViewer` for a
  document with an attachment.
- Formats: PNG throughout vanilla; JPG and BMP are also accepted.
- Caption goes in a separate `TextBlock` below, small and italic. Do not bake caption
  text into the PNG unless you accept re-exporting it per language.
- The file must sit in the `AssetsPath_XX` **directory**. Adding an image is: drop the
  file in `art/`, reference `Assets[<filename-without-extension>]`. No manifest, no
  search-pattern key — that is a mission-briefing thing, not a campaign-event thing.
- Language: keep image-only art in the shared `art/` folder. A picture with baked-in
  English text needs a per-language copy and its own `AssetsPath_XX` pointing at that
  language's folder — the trap `[Mission31]` walks into.

Fit-for-purpose note: a grainy grayscale photo, a hand-annotated chart crop, or a
typewritten table screenshot all sit naturally on `bkg_paper`. A clean modern colour
render does not — it breaks the 1985 typewriter illusion the template is built around.

### The player's task force name

Campaign documents can address the player's actual force:

```xml
<TextBlock Grid.Row="4" Grid.Column="2">
  <Run Text="COMMANDER"/>
  <Run Text="{Binding DataSource.PersistentData[PlayerTaskForceName], Converter={StaticResource UppercaseConverter}}"/>
  <Run Text="DARWIN NT AU"/>
</TextBlock>
```

This is the campaign-document equivalent of `{TaskForceName}` in mission messages. Used
in the `TO` line of `19850808_intel_event.xml` and in `19850719_logistics_advisory.xml`.
Note the three-`Run` split — a `Run` cannot contain both literal text and a binding.

### Other bindings seen in vanilla

| Binding | Where |
|---|---|
| `DataSource.PersistentData[PlayerTaskForceName]` | any document |
| `DataSource.TaskForceCommanderShipsSunk` / `…SubmarinesSunk` / `…AircraftShotDown` | scoreboard |
| `DataSource.TaskForceScoreboardSurfaceUnits` / `…Squadrons` (+ `…Count`, `…Has…`) | scoreboard `ItemsControl` |
| `DataSource.TaskForceScoreboardIslandsCaptured` | scoreboard |
| `OpenFileCommand` + `CommandParameter="<path to xml>"` | navigation button |
| `NextCommand` | advance past the last page of the event |

Converters available: `UppercaseConverter`, `CollapsedConverter`,
`InverseCollapsedConverter`, `CrewSkillToBrushConverter`, `IniToProfileConverter`.
Style resource: `SlideArrowButton`.

The scoreboard bindings only make sense on an end-of-campaign record page — see
`art/event_task_force_77_combat_record.xml` for the full working example. There is no
documented list of these names beyond what vanilla uses; anything not in the table above
is a guess and will silently render empty.

---

## 6. Multi-page documents

Set `UseAuthoredNavigation=True` on the `[MissionN]` block and draw your own buttons.
Each page is its own XAML file; the button jumps to the next by path:

```xml
<Button Width="96" Height="190" Style="{StaticResource SlideArrowButton}" Content="&gt;"
        Command="{Binding OpenFileCommand}"
        CommandParameter="campaigns/pacific-strike-task-force/art/s01_window_3.xml"/>
```

`Content="&lt;"` / `"&gt;"` are the escaped `<` / `>` arrows. The last page uses
`Command="{Binding NextCommand}"` instead, which closes the event and returns to the map.
`campaign.ini` only ever points at page 0 (`FilePath_en=…/s01_window_1.xml`); the chain
lives entirely in the XAML.

Pattern: `art/s01_window_0.xml` … `s01_window_7.xml` (the campaign intro slideshow), and
`event_task_force_77_combat_record.xml` → `event_pacific_strike_outro.xml`.

For an intel document this is worth it when the paperwork has an attachment — a message
sheet followed by a map or photo page.

---

## 7. The vanilla document catalogue — pick a genre

| Style | Files | Look |
|---|---|---|
| Naval message on typed paper | `19850701_intel_event`, `19850808_sitrep`, `19850709_jcs_sitrep_palawan`, `19851001_palawan_bda_report`, `19850921_17mau_targeting_intel`, `19850819_coastwatcher_report` | `ScrollViewer` + `bkg_paper` + Courier New. **The default.** |
| Typed intercept / memo | `19850821_senyavin_intercept`, `19850921_china_intercept_sandakan` | `Page`+`Viewbox`, white `Border` with a heavy black `BorderThickness="0,10,10,10"` frame, Times New Roman headings |
| Newspaper | `19850626_newspaper_event` | `bkg_newsprint`, Impact masthead, multi-column `Grid`, inline photos. Localizable |
| Breaking news (flat image) | `19850626_breakingnews_event` and siblings | 8 lines: `Viewbox` → `StackPanel` → one `Image`. All content baked into the PNG — fast, but needs a new PNG per language |
| Dark briefing slide | `s01_window_0..7` | `#2b2d31` background, `#949aa1` text, image + prose + nav buttons. Not paperwork — narrative |
| Data scoreboard | `event_task_force_77_combat_record` | `ItemsControl` over campaign stats bindings, `Export PNG` button |

For a mid-campaign intel report, copy `19850808_sitrep.xml`. For "the player intercepted
something", copy `19850821_senyavin_intercept.xml`.

---

## 8. Gotchas

- **A `Grid.Row="N"` with no matching `RowDefinition` is dropped silently.** The template
  declares ~32 `<RowDefinition Height="Auto"/>` up front precisely so paragraphs can be
  renumbered freely. If you add paragraph rows, add row definitions. This is the single
  most common way a document loses its last paragraph.
- Row numbers in the template are **sparse on purpose** (1, 3, 4, 11, 13, 15…) — the gaps
  are where an author adds more `TO`/`INFO` addressees without touching anything below.
  Empty rows collapse to zero height with `Height="Auto"`.
- **`AssetsPath_XX` is a directory, `FilePath_XX` is a file.** Swapping them gives a blank
  page.
- Paths are `StreamingAssets`-relative and use forward slashes, in `campaign.ini` and in
  `CommandParameter` alike.
- The document is **never opened by the mission editor** — it is hand-written XAML. Nothing
  recompiles it, so unlike mission `.ini` files there is no editor round-trip risk here.
- `NumberOfMissions` must equal the `[MissionN]` block count, documents included.
- `Description_XX` may be empty but vanilla still writes the key. `Name_de` sometimes has
  no `Description_de` at all — the key is genuinely optional.
- No syntax validation exists. Malformed XAML gives a blank or broken event page with no
  error. Check the XML is well-formed before launching: `xmllint --noout file.xml`.

---

## 9. Localization

Per-language keys on the `[MissionN]` block: `Name_`, `Description_`, `AssetsPath_`,
`FilePath_`, `TileImagePath_`, each suffixed `_en` `_ru` `_de` `_ja`. English is the
fallback; a language with no `FilePath_XX` gets the English document.

File conventions in vanilla (inconsistent, both work):

- **Russian**: same filename, `art/ru/` subdirectory — `art/ru/19850808_sitrep.xml`
- **German**: `_de` suffix *and* `art/de/` subdirectory — `art/de/19850808_sitrep_de.xml`
- **Japanese**: often reuses the English file, or `art/ja/`

`AssetsPath_XX` normally stays pointed at the shared `art/` directory for every language,
so `bkg_paper` resolves. `[Mission31]` sets `AssetsPath_ru=…/art/ru`, which means
Russian-only asset copies must live there — follow the shared-directory pattern unless a
language genuinely needs its own images (baked-in newspaper PNGs do).

Only translate the text nodes. Leave the `Grid`, row numbers and bindings identical, so a
layout fix can be applied to all languages the same way.

---

## 10. Checklist for adding one intel document

1. `cp campaigns/<campaign>/art/19850808_sitrep.xml campaigns/<campaign>/art/YYYYMMDD_<name>.xml`
   (copy from Pacific Strike if the campaign has no template of its own).
2. Rewrite the header block: precedence, DTG, `FM`/`TO`/`INFO`, `SUBJ`.
3. Rewrite the numbered paragraphs. One `TextBlock` per paragraph, `TextWrapping="Wrap"`,
   trailing `<LineBreak/>`, `Grid.ColumnSpan="4"`.
4. Count paragraph rows; make sure `Grid.RowDefinitions` still has at least as many rows
   as the highest `Grid.Row` used.
5. `xmllint --noout <file>` — catches unescaped `&`, `<`, unclosed tags.
6. Add the `[MissionN]` block to `campaign.ini` with `Type=FreeEvent`,
   `Parents=<preceding node>`, and the five `_en` path/name keys.
7. Bump `NumberOfMissions`.
8. Point the *next* node's `Parents=` at the new block, so it sits in the chain rather
   than dangling off the side.
9. Launch the campaign, walk the timeline to the node, read the sheet.
