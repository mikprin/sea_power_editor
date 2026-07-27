# How to Create a Task Force Campaign - Official Guide

Welcome to the official documentation for creating your own persistent Task Force Mode campaigns in **Sea Power: Naval Combat in the Missile Age** (updated for version 0.8.0+).

This guide covers the new features that allow you to string missions together into a cohesive, persistent campaign where forces, damage, and ammunition carry over from one operation to the next.

---

## 1. The Mission Editor Tools: Deployment Zones & Points

The foundation of a Task Force Campaign begins in the standard Mission Editor. However, instead of rigidly placing every player unit, you will designate zones where the player can deploy their custom Task Force.

* **Deployment Zones:** Use the new `Mission Points` dropdown in the editor to draw deployment areas on the map. These define where the player can place the ships they purchased in the Task Force Builder before the mission starts.
* **Unrestricted vs. Limited Dates:** You can configure the campaign parameters to restrict which ships the player can purchase based on the historical date of the scenario, or enable "Unrestricted Mode" so players can use any ship (including modded vessels).
* **Automatic Points Calculation:** The game now automatically assigns point values to all units (including user-created mods). As a campaign creator, you simply need to define the **Points Cap** for the player's starting Task Force.

## 2. Stores & Loadout Control

A key element of persistence is ammunition scarcity. Task Force Mode tracks missile, torpedo, and decoy expenditures across missions.

* **Stores Editor Overrides:** To control exactly what the player or the AI brings to the fight, use the Stores Editor container overrides. This allows you to restrict the number of Tomahawks, Harpoons, or heavy torpedoes available to specific task groups, forcing the player to conserve weapons.
* **Expenditure Tracking:** Any weapons fired in Mission 1 will be missing from the magazines in Mission 2 unless you explicitly build in resupply mechanics.

## 3. Event Logic: Damage, Repair, and Rearmament

With Update 0.8.0, several new triggers were added to the `.ini` logic to simulate a living campaign environment:

* **Simulating Battle Damage:** Use the `Enable/Disable System` actions on specific units to start a mission with damaged radar, disabled sonar, or a destroyed flight deck. This is useful for narratively punishing the player or creating "crippled ship escort" scenarios.
* **Repair & Rearm Triggers:** You can set up specific zones or time-based triggers that restore a ship's stores or fix disabled systems. For example, returning a surviving task force to a specific port coordinate can trigger a resupply event for the next mission.
* **Morale System Integration:** Ensure the Morale System is enabled for your scenario. If a unit's morale drops below 20%, it will attempt to retreat. Surviving a retreat keeps the ship in the campaign roster; sinking removes it permanently.

## 4. Campaign Briefings & Narrative

Task Force campaigns rely on strong narrative tissue to bridge the gap between combat engagements.

* **Pre-Mission Campaign Map:** The campaign map view now acts as an interactive pre-briefing. You can author display-only map symbols and operational markers that the player sees before committing their forces.
* **MissionWarningMessage:** You can use this new trigger to create custom confirmation popups (e.g., "WARNING: Proceeding past this coordinate will initiate hostilities. Are you ready?").
* **Custom Briefing Formatting:** Text briefings use XAML formatting. Make sure to use `<TextBlock>` and `</TextBlock>` tags in your briefing `.txt` files to ensure they format correctly in the UI.

---

> **Note:** If you are building a new campaign, it is highly recommended to disable any outdated unit mods, as older mods may not yet be compatible with the automated points generator or the new Task Force Builder logic.

---

## 5. Field Reference: Setting Up Task Force Mode In `.ini` Files

This section explains how mission makers and mod developers can set up a Task Force Mode campaign for Sea Power.

It is written for people who are comfortable opening and editing `.ini` files, but who may not be programmers. It explains what each Task Force Mode field does in normal campaign-building terms first, then gives the exact field names you can copy into your own files.

> Build your campaign in the user/mod area. Do not edit the base game files directly.

Use this as the working pattern:

```
Assets/StreamingAssets/user/<Your Mod Name>/
  _info.ini
  campaigns/
    <your-campaign>/
      campaign.ini
      commander_settings.ini
      player_task_force_roster.ini
      unit_roster_descriptions_en.ini
      missions/
        01 First Mission.ini
        02 Second Mission.ini
      art/
        ribbons/
        medals/
```

Inside the INI files, paths are normally written relative to the mod root, for example:

```ini
MissionFile=campaigns/my-task-force-campaign/missions/01 First Mission.ini
CommanderSettingsFile=commander_settings.ini
RosterFile=player_task_force_roster.ini
```

### What Task Force Mode Does

In a normal mission, the ships and aircraft in the mission file are fixed. The player starts the mission with whatever you placed in the Mission Editor or wrote into the `.ini`.

In Task Force Mode, the player builds a task force with campaign points, takes that force into missions, and then keeps the surviving ships, submarines, aircraft, damage, ammunition state, commander record, and awards across the campaign.

That means each mission needs extra information:

* The campaign file tells the game what the player can buy, how many points they have, which missions use Task Force Mode, and what rewards are given after each mission.
* The mission file tells the campaign mission generator where to place the player's persistent task force when the mission starts.
* Optional mission fields can tell the generator which ships already placed in the mission file should be replaced, which aircraft slots are used for Air Tasking, or which surviving mission units should join the player's task force after the mission.

Think of the mission generator as a helper that prepares a temporary launch copy of your mission. It does not permanently rewrite your original mission file. It uses the Task Force Mode fields to place the player's saved force into the mission before launch.

### Use Pacific Strike As A Reference

The Pacific Strike Task Force campaign included with the base game is useful as a working example. Use it to see how the fields fit together in a complete campaign, then copy the patterns you need into your own user campaign.

Reference files in the base game:

* `Assets/StreamingAssets/original/campaigns/pacific-strike-task-force/campaign.ini`
* `Assets/StreamingAssets/original/campaigns/pacific-strike-task-force/player_task_force_roster.ini`
* `Assets/StreamingAssets/original/campaigns/pacific-strike-task-force/commander_settings.ini`
* `Assets/StreamingAssets/original/campaigns/pacific-strike-task-force/missions/*.ini`

> Do not change those files under `original`. Treat them as read-only examples.

### The Simplest Working Campaign

The easiest Task Force Mode setup uses Generated missions. In a generated mission, you place one player ship in the mission file as an anchor. At launch, the game replaces that anchor with the player's real task force and places the rest of the force around it.

Basic steps:

1. Create a user campaign folder under `Assets/StreamingAssets/user/<Your Mod Name>/campaigns/<your-campaign>/`.
2. Add a normal `campaign.ini`.
3. Add `[TaskForceMode] Enabled=True` to `campaign.ini`.
4. Add a roster file such as `player_task_force_roster.ini`.
5. Add point costs to any modded units you want the player to buy.
6. In each Task Force Mode mission entry, add `TaskForceModeMissionGenerationType=Generated`.
7. In each generated mission file, mark one player vessel with `TaskForceModeAnchor=True`.
8. Add mission rewards, repair/rearm rules, and optional roster restrictions in each `[MissionN]` section.

Minimal `campaign.ini` example:

```ini
[Campaign]
Type=Linear
Length=1

[TaskForceMode]
Enabled=True
DefaultTaskForceName=Task Group 77.3
CommanderSettingsFile=commander_settings.ini
RosterFile=player_task_force_roster.ini
TaskForceDifficultyPresets=Easy|Moderate|Difficult
DefaultTaskForceDifficultyPreset=Moderate
StartingPoints=50
PointCap=50
ShipIncludesAirwing=True
PurchaseLoadouts=True
BasicShipLoadoutVariants=Default|Early
LockedShipLoadoutVariants=Late
CSARPointModifier=100
UnitDecommissionPointReturnModifier=0.25
UnitDismissPointReturnModifier=0.5
DamageToAllowRepair=Light,Moderate
DamageToDisallowRepair=Heavy
RepairPointsCost=Light,0.1|Moderate,0.25

[TaskForceModeDifficulty_Moderate]
Name=Moderate
StartingPoints=50
PointCap=50
ShipIncludesAirwing=True
PurchaseLoadouts=True
InitialUnlockedLoadouts=Default|Early
RepairCostModifier=1
UnitDecommissionPointReturnModifier=0.25
UnitDismissPointReturnModifier=0.5
CrewSkillInitial=Trained

[Mission1]
MissionFile=campaigns/my-task-force-campaign/missions/01 First Mission.ini
TaskForceModeMissionGenerationType=Generated
IsUnlocked=True
IsComplete=False
TaskForceModeIncludesTaskForce=True
TaskForceModeIncludesAirwing=False
TaskForceModeIncludesSubmarine=False
TaskForceModeThreatProfileShip=True,3
TaskForceModeThreatProfileAir=True,2
TaskForceModeThreatProfileSub=False
TaskForceModeThreatProfileLand=False
TaskForceModeRearm=True
TaskForceModeRepair=True
TaskForceModeEnableTaskForceBuilder=True
TaskForceModeAllowedRosterUnits=usn_ddg_kidd,Variant3|usn_ff_knox,Variant1
TaskForceModeCompletionPoints=10
TaskForceModeCompletionCapPoints=10
TaskForceModeRibbonAwards=combat_action_ribbon
Name_en=FIRST MISSION
Description_en=Build a small task force and take it into action.
```

Minimal mission-file example:

```ini
[Mission]
PlayerTaskforce=Taskforce1
NumberOfTaskforce1Vessels=1

[Taskforce1Vessel1]
Type=usn_ddg_kidd
VariantReference=Variant3
LoadoutVariant=Default
RelativePositionInNM=0,0,0
Heading=090
Telegraph=3
TaskForceModeAnchor=True
```

In plain English, this mission says:

* The player side is `Taskforce1`.
* There is one player ship in the mission file you created.
* That ship is the Task Force Mode anchor.
* When the mission launches, the generator uses the anchor's position, heading, speed, and waypoints as the starting point for the player's persistent task force.

### Campaign Folder And Paths

Recommended user-campaign layout:

```
Assets/StreamingAssets/user/<Your Mod Name>/
  _info.ini
  campaigns/
    my-task-force-campaign/
      campaign.ini
      commander_settings.ini
      player_task_force_roster.ini
      unit_roster_descriptions_en.ini
      missions/
        01 First Mission.ini
      art/
        ribbons/
        medals/
```

* `campaign.ini` is the main campaign file. It defines the campaign timeline, mission list, Task Force Mode rules, and mission rewards.
* `player_task_force_roster.ini` lists the ships, submarines, helicopters, and aircraft the player is allowed to buy.
* `commander_settings.ini` defines commander nations, ranks, same-nation discounts, ribbons, medals, and citation text.
* `unit_roster_descriptions_<language>.ini` is optional, but recommended. It gives short player-facing descriptions in Task Force Builder.
* `missions/` contains the mission `.ini` files that the campaign launches.
* `art/` contains campaign images, event XML, ribbons, medals, and other campaign-specific art.

### Task Force Builder and Unit Points Cost

Task Force Builder is the screen where the player spends campaign points to build and maintain their persistent force. In normal play, the player uses those points to buy ships, submarines, aircraft, and helicopters before a mission. The units that survive are carried forward, and the player's remaining points are saved for later repairs, rearming, and new purchases.

Every unit that appears in Task Force Builder needs a point cost. Think of this as the campaign price for one ship, one submarine, one helicopter, or one aircraft. A more capable unit costs more points, so the player has to make choices instead of buying everything.

For base game units, point costs are already set up. You do not need to add prices to the base game files just to make a Task Force Mode campaign.

The default point cost is stored in the unit's own `.ini` file:

```ini
[TaskForce]
TaskForceCost=27
LoadoutCost_Late=10
```

* `TaskForceCost` is the default number of campaign points needed to buy one unit.

If you are making a new modded unit and want it to appear in Task Force Builder, add a `[TaskForce]` section to that unit's `.ini` file and give it a `TaskForceCost`.

### Campaign-Specific Price Overrides

A campaign can use a different point cost without changing the unit file. Put the override in that campaign's roster file, such as `player_task_force_roster.ini`.

The basic roster format is:

```
unit_type=variant_or_squadron_list|point_cost
```

Ship and submarine example:

```ini
[AllowedVessels]
usn_ddg_kidd=Variant3,Variant4|30

[AllowedSubmarines]
usn_ssn_permit=Variant3,Variant10|22
```

Aircraft and helicopter example:

```ini
[AllowedAircraft]
usn_p-3c=Squadron14,Squadron31|8

[AllowedHelicopters]
usn_sh-2f=Squadron4,Squadron6|4
```

In those examples, the number after the `|` is the campaign's base point cost for that unit. If the player has a commander discount, the final price shown in Builder may be lower.

If you leave the `|point_cost` part out, Task Force Builder uses the unit's default `TaskForceCost` from the unit file:

```ini
[AllowedVessels]
usn_ddg_kidd=Variant3,Variant4
```

That means most campaigns can keep the roster simple and rely on the default prices. Use roster-file price overrides only when your campaign needs different balance.

### Loadout Point Costs

For ships and submarines, some upgraded loadouts can also cost points. This is separate from the unit purchase price.

Unit-file loadout cost example:

```ini
[TaskForce]
TaskForceCost=27
LoadoutCost_Late=10
LoadoutCost_AntiShipHeavy=3
```

`LoadoutCost_<LoadoutName>` must match the actual loadout reference in that unit file.

Campaigns can also override loadout prices in the roster file:

```ini
[LoadoutPrices]
usn_ddg_kidd=Late,10|AntiShipHeavy,3
```

Aircraft loadouts are currently included with the aircraft purchase. Paid loadout costs are mainly for ships and submarines.

### Campaign-Wide Task Force Rules

These fields go in `[TaskForceMode]`.

This section answers big campaign questions:

* Is Task Force Mode enabled?
* What is the task force called?
* Which roster file should Builder use?
* Which difficulty settings are available?
* How many points does the player start with?
* Are ships repaired and rearmed between missions?
* Which loadouts start unlocked?

| Field | Description |
|---|---|
| `Enabled` | Set `True` to turn on Task Force Mode for this campaign. |
| `TaskForceRequireFlagship` | If true, losing the flagship can fail the mission. For new authoring, use this name. |
| `DefaultTaskForceName` | Starting name for the player's force. The player may be able to edit it. |
| `TaskForceNameOptions` | Optional random task force names, separated with `\|`. |
| `CommanderSettingsFile` | Usually `commander_settings.ini`. This file controls commander setup and awards. |
| `RosterFile` | Usually `player_task_force_roster.ini`. This file controls what the player can buy. |
| `TaskForceDifficultyPresets` | Difficulty preset IDs, separated with `\|`. Each needs a matching `[TaskForceModeDifficulty_<Id>]` section. |
| `DefaultTaskForceDifficultyPreset` | The difficulty selected by default. |
| `StartingPoints` | Fallback starting points if no preset is used. |
| `PointCap` | Fallback starting point cap if no preset is used. |
| `ShipIncludesAirwing` | If true, ships come with their normal airwing. If false, aircraft must be bought separately. |
| `PurchaseLoadouts` | If true, some ship/submarine loadouts can cost points. |
| `BasicShipLoadoutVariants` | Loadouts available at campaign start, such as `Default\|Early`. |
| `LockedShipLoadoutVariants` | Loadouts that exist but are locked until a mission unlocks them. |
| `CSARPointModifier` | Number of rescued survivors needed for 1 campaign point. 100 means 100 survivors gives 1 point. |
| `CrewSkillInitial` | Starting crew skill for new units, such as `Green` or `Trained`. |
| `CrewSkillThresholds` | Optional survival-based skill thresholds, such as `Veteran:3\|Elite:6`. |
| `UnitDecommissionPointReturnModifier` | Refund fraction when decommissioning a unit. 0.25 means 25 percent. |
| `UnitDismissPointReturnModifier` | Refund fraction when dismissing a unit. 0.5 means 50 percent. |
| `DamageToAllowRepair` | Damage levels that can be repaired, usually `Light,Moderate`. |
| `DamageToDisallowRepair` | Damage levels that cannot be repaired, usually `Heavy`. |
| `RepairPointsCost` | Repair cost by damage level. `Light,0.1\|Moderate,0.25` means repairs cost 10 percent or 25 percent of unit cost. |

Advanced optional field:

* `CurrentTaskForce`: Seeds a campaign with a starting task force. Most first-time authors should skip this and let the player buy the starting force.

### Difficulty Presets

Difficulty presets let you offer different Task Force Mode rules when the player starts the campaign.

Example:

```ini
[TaskForceModeDifficulty_Easy]
Name=Easy
StartingPoints=65
PointCap=65
ShipIncludesAirwing=True
PurchaseLoadouts=False
InitialUnlockedLoadouts=Default|Early|Late
RepairCostModifier=0.75
UnitDecommissionPointReturnModifier=0.35
UnitDismissPointReturnModifier=0.65
CrewSkillInitial=Trained

[TaskForceModeDifficulty_Moderate]
Name=Moderate
StartingPoints=50
PointCap=50
ShipIncludesAirwing=True
PurchaseLoadouts=True
InitialUnlockedLoadouts=Default|Early
RepairCostModifier=1
UnitDecommissionPointReturnModifier=0.25
UnitDismissPointReturnModifier=0.5
CrewSkillInitial=Trained

[TaskForceModeDifficulty_Difficult]
Name=Difficult
StartingPoints=40
PointCap=40
ShipIncludesAirwing=False
PurchaseLoadouts=True
InitialUnlockedLoadouts=Default|Early
RepairCostModifier=1.25
UnitDecommissionPointReturnModifier=0.15
UnitDismissPointReturnModifier=0.35
CrewSkillInitial=Green
```

* `Name` or `Name_<lang>`: Display name shown to the player.
* `StartingPoints`: Points available at campaign start.
* `PointCap`: Maximum points available at campaign start.
* `ShipIncludesAirwing`: Whether ships bring their airwing for free.
* `PurchaseLoadouts`: Whether upgraded ship/submarine loadouts cost points.
* `InitialUnlockedLoadouts`: Loadouts available at campaign start.
* `RepairCostModifier`: Multiplies repair costs. 0.75 is cheaper; 1.25 is more expensive.
* `UnitDecommissionPointReturnModifier`: Refund fraction for decommissioning.
* `UnitDismissPointReturnModifier`: Refund fraction for dismissing.
* `CrewSkillInitial`: Crew skill for newly purchased units.

The chosen preset is saved when the player starts the campaign. After that, the save file owns those values.

### The Purchase Roster

The roster file controls what the player can buy in Task Force Builder.

Example:

```ini
[AllowedVessels]
usn_ddg_kidd=Variant3,Variant4
usn_ff_knox=Variant1,Variant3,Variant14

[AllowedSubmarines]
usn_ssn_permit=Variant3,Variant10

[AllowedHelicopters]
usn_sh-2f=Squadron8

[AllowedAircraft]
usn_p-3c=Squadron14,Squadron31
```

* Ships and submarines use `VariantReference` values.
* Aircraft and helicopters use `SquadronReference` values.

The campaign roster is the broad list. Individual missions can narrow the list with `TaskForceModeAllowedRosterUnits`, but they cannot make a unit available if it is missing from the roster file.

### Individual Mission Rules In campaign.ini

These fields go in each `[MissionN]` section of `campaign.ini`.

Each mission can decide:

* Whether it uses the player's task force.
* Whether ships, aircraft, and submarines deploy.
* Whether Builder is open before the mission.
* Whether repair and rearm are available.
* Which units can be bought before this mission.
* What points, units, loadouts, ranks, and awards are granted after completion.

#### Mission Generation Type

```ini
TaskForceModeMissionGenerationType=Generated
```

This is one of the most important fields.

* **Blank/empty:** Leave this field totally blank if you want the mission to launch as-is without any persistent task force units (useful for side missions, or other missions that should be in the campaign timeline but do not affect the player's built task force).
* **Generated:** You want the game to place the player's saved task force around one anchor ship. This is the easiest Task Force Mode setup.
* **Replaced:** You want the player's ships to fill specific ship slots you placed in the mission. Use this when exact positions and triggers matter.

Use `Generated` for your first Task Force Mode campaign.

Use `Replaced` later, when you need more control over ship placement.

#### Mission Capability Display

These fields tell the campaign map display what the mission expects -- they are meant to give the player a rundown of the available forces that will deploy, and the expected threat level in the mission. These are display-only and do not affect the mission in any way.

```ini
TaskForceModeIncludesTaskForce=True
TaskForceModeIncludesAirwing=True
TaskForceModeIncludesSubmarine=False
TaskForceModeThreatProfileShip=True,3
TaskForceModeThreatProfileAir=True,2
TaskForceModeThreatProfileSub=True,1
TaskForceModeThreatProfileLand=False
```

Threat profile fields use:

```
False
True,<level>
```

The level is a rough display value for the mission card, rated as N / 5 with 5 being the max threat -- so a 1/5 submarine threat may have the player facing lower tier or older submarines, and a 5/5 ship threat will have the player facing very capable enemy surface threats, and so on.

#### Repair And Rearm

```ini
TaskForceModeRearm=True
TaskForceModeRepair=True
```

`TaskForceModeRearm=True` means generated ships and submarines will be rearmed before the mission. If the field is blank or missing, rearm is treated as `TRUE`.

`TaskForceModeRepair=True` means the Task Force Manager allows repairs before the mission. If the key is blank or missing, repair is treated as available. Repairs must be bought with points, it is not automatic.

You can also make rearm depend on campaign variables:

```ini
TaskForceModeRearmByVariableAND=AmmoCarrierSurvived,IsTrue
TaskForceModeRearmByVariableOR=AmmoShipSurvived,IsTrue|DepotCaptured,IsTrue
```

`TaskForceModeRearmByVariableAND` means all listed conditions must be true.

`TaskForceModeRearmByVariableOR` means at least one listed condition must be true.

Common checks include:

* `VariableName,IsTrue`
* `VariableName,IsFalse`
* `VariableName,NumberGreaterThan,5`
* `VariableName,NumberLessThan,5`
* `VariableName,StringEqual,SomeValue`

For a first campaign, use simple `TaskForceModeRearm=True` and `TaskForceModeRepair=True`.

#### Builder Availability And Mission Roster

```ini
TaskForceModeEnableTaskForceBuilder=True
TaskForceModeAllowedRosterUnits=usn_ddg_kidd,Variant3,Variant4|usn_ff_knox,Variant1|usn_sh-2f,Squadron8
```

`TaskForceModeEnableTaskForceBuilder` controls whether the player can buy units before this mission. If the key is blank or missing, Builder is allowed.

`TaskForceModeAllowedRosterUnits` narrows what the player can buy before this mission.

Example:

```ini
TaskForceModeAllowedRosterUnits=usn_ddg_kidd,Variant3|usn_ff_knox,Variant1,Variant3|usn_p-3c,Squadron14
```

#### One-Ship Restricted Missions

```ini
TaskForceModeRequiredUnitType=Vessel
TaskForceModeMaxUnits=1
```

Use this when a mission should only allow a small restricted deployment, such as one surface ship. `TaskForceModeMaxUnits` can be any numeric value. For example, campaign mission 03B requires a single unit, while mission 08 allows only 3 units.

> **Current behavior note:** `Vessel` is the useful value here. `Submarine` is ignored by the current restricted-mission rule because detached submarine missions use submarines already placed in the mission file instead.

#### Completion Rewards

```ini
TaskForceModeCompletionPoints=10
TaskForceModeCompletionCapPoints=10
TaskForceModeCompletionRewardedUnits=usn_p-3c,Squadron31,1|usn_a-7e,Squadron10,2
TaskForceModeLoadoutsToUnlock=Late
TaskForceModeCommanderIncreaseRank=1
```

* `TaskForceModeCompletionPoints` gives the player spendable points after successful completion.
* `TaskForceModeCompletionCapPoints` raises the maximum number of points the player can hold.
* `TaskForceModeCompletionRewardedUnits` gives free units after completion. They do not cost points.

Rewarded-unit format:

```
unit_type,VariantOrSquadron,count|unit_type,VariantOrSquadron,count
```

* `TaskForceModeLoadoutsToUnlock` unlocks one or more loadout names, separated with `|`.
* `TaskForceModeCommanderIncreaseRank` promotes the commander by the number of rank levels listed.

#### Debrief Notice

```ini
TaskForceModeDebriefNoticeTitle_en=Airwing Operations Unlocked
TaskForceModeDebriefNoticeText_en=Fixed-wing aircraft can now be added to your airwing.
```

Use these fields when you want the Task Force debrief to explain a new feature, reward, or campaign change.

Add localized versions with suffixes such as `_de`, `_ja`, `_ru`, and so on.

#### Ribbon Awards

```ini
TaskForceModeRibbonAwards=combat_action_ribbon|jmsdf_defense_memorial_cordon
```

This grants ribbons after mission completion.

The ribbon IDs must exist in `commander_settings.ini`.

You can restrict an award to certain commander nations:

```ini
TaskForceModeRibbonAwards=navy_cross,US,Japan|australian_distinguished_service_cross,Australia
```

The first value is the ribbon ID. Extra comma-separated values are eligible commander nation keys. If no nation keys are listed, all commander nations can receive the award.

#### Final Mission

```ini
TaskForceModeFinalMission=True
```

Use this on the last playable Task Force Mode mission.

#### Service Record Onboarding

For an event or mission section:

```ini
TaskForceModeServiceRecordOnboarding=True
```

This opens the commander Service Record setup if the player has not committed a commander yet.

### Mission File Fields

These fields go inside the individual mission `.ini` files. The mission files must be edited with fields that tell the campaign mission generator where to place the player's persistent task force.

The mission file does not decide the whole campaign economy. Its job is to give the generator clear placement instructions and mark any mission sections you placed by hand that need special Task Force Mode behavior.

#### TaskForceModeAnchor

```ini
[Taskforce1Vessel1]
TaskForceModeAnchor=True
RelativePositionInNM=0,0,0
Heading=090
Telegraph=3
```

`TaskForceModeAnchor=True` marks the ship section used as the starting point for the generated task force.

For a generated mission:

* The first player ship starts at the anchor's position.
* The first player ship uses the anchor's heading, telegraph, and waypoints.
* Other ships are placed around the anchor or by the player's saved formation.
* If no anchor is marked, the generator uses `Taskforce1Vessel1`.

For your first campaign, put one player ship in the mission and mark it as the anchor.

#### TaskForceModePlaceholderUnit

```ini
[Taskforce1Vessel2]
TaskForceModePlaceholderUnit=True
```

This marks a player vessel as a temporary placeholder.

Use it when you want a ship visible while editing the mission, but you do not want that exact ship to remain when the generated mission launches.

#### Replaced Generation Fields

Use replaced generation when the player's ships need to appear in exact slots you placed in the mission.

In `campaign.ini`:

```ini
TaskForceModeMissionGenerationType=Replaced
```

In the mission file:

```ini
[Taskforce1Vessel1]
TaskForceModeAnchor=True
TaskForceModeReplacedUnitIndex=1

[Taskforce1Vessel2]
TaskForceModeReplacedUnitIndex=2
```

`TaskForceModeReplacedUnitIndex` tells the generator, "Put one of the player's ships into this vessel slot you placed in the mission."

Slots are filled in number order:

* `TaskForceModeReplacedUnitIndex=1`
* `TaskForceModeReplacedUnitIndex=2`
* `TaskForceModeReplacedUnitIndex=3`

The generator keeps the mission section's position and mission setup, but changes the ship type, variant, loadout, campaign tag, crew skill, logistics rules, and air group to match the player's actual ship.

Use Replaced when triggers, formations, starting geometry, or scenario scripting depend on specific section names or positions.

### Air Tasking Fields

Air Tasking lets the campaign offer special flight assignments before a mission. For example, the player might assign two fighters to CAP and one patrol aircraft to Recon. These aircraft will start the mission already in the air, allowing for easier pacing and balancing of missions as aircraft do not need to either ready up or launch from a distant airfield to be in play at mission start.

Air Tasking has two parts:

* The campaign mission entry creates the flight rows the player sees.
* The mission file provides aircraft or helicopter slots that those rows will fill.

Campaign example:

```ini
TaskForceModeAirTaskingAvailable=True
TaskForceModeAirTaskingFlight1=CAP|CAP|Fighter|2|AirToAir/AirToAirLongRange
TaskForceModeAirTaskingFlight2=Recon|Recon|MPA/ASW/ESM/AEW|1|ASW/Recon/AntiShip/AEW
TaskForceModeAirTaskingFlight3=Recon|Recon|MPA/ASW/ESM/AEW|1|ASW/Recon/AntiShip/AEW
```

Five-part format:

```
RoleId|DisplayName|AllowedUnitRoles|SlotCount|AllowedLoadouts
```

Four-part older format:

```
RoleId|DisplayName|SlotCount|AllowedLoadouts
```

What the parts mean:

* `RoleId`: Flight role name. This must match `TaskForceModeAirTaskingRole` in mission aircraft sections.
* `DisplayName`: Player-facing row name.
* `AllowedUnitRoles`: Aircraft roles allowed for this row, such as `Fighter`, `MPA`, `ASW`, `ESM`, or `AEW`.
* `SlotCount`: Number of aircraft sections this flight can fill.
* `AllowedLoadouts`: Loadout references allowed for this flight. Separate with `/` or `,`.

Mission file example:

```ini
[Taskforce1Aircraft1]
TaskForceModeAirTaskingSlot=1
TaskForceModeAirTaskingRole=CAP

[Taskforce1Aircraft2]
TaskForceModeAirTaskingSlot=2
TaskForceModeAirTaskingRole=CAP

[Taskforce1Aircraft3]
TaskForceModeAirTaskingSlot=1
TaskForceModeAirTaskingRole=Recon
```

Important notes:

* Use unique flight keys: `TaskForceModeAirTaskingFlight1`, `Flight2`, `Flight3`, and so on.
* Do not repeat the same key name for multiple rows.
* Only unassigned aircraft are eligible for Air Tasking.
* Ship-assigned helicopters stay with their ship and are not used for Air Tasking.
* If a row asks for two aircraft and the player only has one available, the generator launches the one available aircraft and removes the unused slot.

### Airbase Preparation

Airbase Prep lets the player prepare land-based aircraft before a mission.

Campaign fields:

```ini
TaskForceModeAirbasePrepAvailable=True
TaskForceModeAirbasePrepReadySlots=2
TaskForceModeAirbasePrepInProgressSlots=4
```

* `TaskForceModeAirbasePrepAvailable`: Enables the Airbase Prep window for this mission.
* `TaskForceModeAirbasePrepReadySlots`: Number of aircraft groups ready at mission start.
* `TaskForceModeAirbasePrepInProgressSlots`: Number of additional aircraft groups that start partially prepared.

The mission must include a player land unit whose `Type` contains `airbase` or `airfield`. The generator looks for it under:

```ini
NumberOfTaskforce1LandUnits=1

[Taskforce1LandUnit1]
Type=some_airbase_type
```

### JoinTaskForce

`JoinTaskForce=True` lets a mission unit you placed by hand join the player's persistent task force after the mission, if that unit survives.

This is useful when you want the player to rescue, recover, link up with, or otherwise gain a specific unit during the campaign. The unit is placed in the mission by hand, and then the campaign adds it to the player's task force after debrief.

Example:

```ini
[Taskforce1Vessel3]
Type=usn_avp_barnegat_mod
VariantReference=Variant1
LoadoutVariant=Default
CrewSkill=Trained
JoinTaskForce=True
```

Aircraft and helicopters can also join this way:

```ini
[Taskforce1Helicopter1]
Type=usn_sh-2f
SquadronReference=Squadron6
LoadoutVariant=ASWLongRange
CrewSkill=Veterans
JoinTaskForce=True
```

`JoinTaskForce=True` works on these normal mission unit sections:

* `Taskforce1Vessel3`
* `Taskforce1Submarine1`
* `Taskforce1Aircraft1`
* `Taskforce1Helicopter1`

It does not work on:

* Land units
* Airbases
* Weapons
* Enemy units

The debrief uses that tag to check whether the unit survived. If it survived, the unit is added to the current task force at zero point cost.

Joined units keep the skill and selected loadout they had when the mission launched. For joined aircraft and helicopters, the player will be able to use that loadout with the joined unit later.

Aircraft and helicopters that join through `JoinTaskForce=True` are added as unassigned campaign roster air units. They are not automatically assigned to a ship, flight deck, airbase, or Air Tasking slot after the mission. The player can use them later through the normal Task Force Mode setup flow.

Use `TaskForceModeCompletionRewardedUnits` when you want to give the player a free unit after a mission regardless of whether that exact unit appeared in the mission and survived.

```ini
TaskForceModeCompletionRewardedUnits=usn_a-7e,Squadron1,2|usn_ddg_kidd,Variant1
```

This will reward the player with 2 x A-7E attack aircraft and 1 x Kidd-class destroyer at mission complete.

### Commander Settings

The commander settings file is usually named:

```ini
CommanderSettingsFile=commander_settings.ini
```

This file controls:

* Which commander nations are available.
* What default names are used.
* What rank list each nation uses.
* What same-nation purchase discount is applied.
* Which ribbons and medals exist.
* What citation text appears for awards.

For the default vanilla game nations included in Pacific Strike campaign (USA, Australia, Japan), Sea Power already includes commander emblems, rank insignia, and name pools. You do not need to set those up again just to make a Task Force Mode campaign. Only change those entries if you are adding a new commander nation, replacing the default art, or changing the names and ranks for your campaign.

#### CommanderSettings

```ini
[CommanderSettings]
CommanderNations=US|Japan|Australia
CommanderDefaultNation=US
CommanderNameDefaultUS=Charles Robinson
CommanderNameDefaultJapan=Hiroshi Watanabe
CommanderNameDefaultAustralia=Grant Morrison
CommanderNamePoolUS=Names_USA
CommanderNamePoolJapan=Names_Japan
CommanderNamePoolAustralia=Names_Australia
CommanderStartingRankLevel=6
SameNationUnitDiscount=0.2
NavyNameUS=United States Navy
NavyEmblemUS=ui/campaign/navy_emblems/usn_emblem.png
```

* `CommanderNations`: Nation keys offered during commander setup.
* `CommanderDefaultNation`: Nation selected by default.
* `CommanderNameDefault<Nation>`: Default commander name for that nation.
* `CommanderNamePool<Nation>`: `ui.ini` name-pool section for random names.
* `CommanderStartingRankLevel`: Starting rank level.
* `SameNationUnitDiscount`: Discount for buying units from the commander's nation. 0.2 means 20 percent off.
* `NavyName<Nation>`: Display name of the navy.
* `NavyEmblem<Nation>`: Image path for the navy emblem.

#### OfficerRanks

```ini
[OfficerRanks]
US=Ensign,ENS,O-1,1,ui/campaign/officer_ranks/usa/insignia_ens.png|Lieutenant,LT,O-3,3,ui/campaign/officer_ranks/usa/insignia_lt.png
```

Each rank uses this format:

```
DisplayName,Abbreviation,Grade,RankLevel,ImagePath
```

Ranks are separated with `|`.

The number in `RankLevel` is what promotions use.

#### Ribbons

First, list every ribbon ID:

```ini
[TaskForceRibbons]
RibbonIds=combat_action_ribbon|navy_unit_commendation|silver_star_medal
```

Then define each ribbon:

```ini
[Ribbon_combat_action_ribbon]
Type=ServiceRibbon
Precedence=100
Name_en=Combat Action Ribbon
ImagePath=campaigns/my-task-force-campaign/art/ribbons/combat_action_ribbon.png
MedalImagePath=campaigns/my-task-force-campaign/art/medals/combat_action_medal.png
ReferenceSource=USN
CitationIssuingBody_en=Department of the Navy
CitationIssuance_en=This is to certify that the Secretary of the Navy has awarded the
CitationAwardName_en=Combat Action Ribbon
CitationAuthority_en=To
CitationRecipient_en={CommanderRank} {CommanderName}
CitationDate_en=26 June 1985
CitationSignatureName_en=John Lehman
CitationSignatureTitle_en=Secretary of the Navy
CitationSealImagePath=campaigns/my-task-force-campaign/art/medals/dept_of_the_navy_seal.png
CitationText_en=For service as Commander, {TaskForceName}, during operations in the Western Pacific.
CitationTextJapan_en=For service as an allied commander attached to {TaskForceName}.
CitationTextAustralia_en=For service as an allied commander attached to {TaskForceName}.
```

Common ribbon fields:

* `Type`: Award category.
* `Precedence`: Sort order in the ribbon rack. Lower numbers sort first.
* `Name_en` and `Name_<lang>`: Ribbon display name.
* `ImagePath`: Ribbon image path.
* `MedalImagePath`: Medal or citation image path.
* `Devices`: Optional device type, such as `GoldStar`.
* `StripeColors`, `StripeWidths`: Optional ribbon drawing data.
* `ReferenceSource`, `SourceUrl`: Optional source/reference data.
* `CitationIssuingBody_en`: Citation header text.
* `CitationIssuance_en`: Citation opening text.
* `CitationAwardName_en`: Award name shown in the citation.
* `CitationAuthority_en`: Usually `To`.
* `CitationRecipient_en`: Recipient line. Supports tokens.
* `CitationDate_en`: Citation date.
* `CitationSignatureName_en`: Signature name.
* `CitationSignatureTitle_en`: Signature title.
* `CitationSealImagePath`: Optional seal image.
* `CitationText_en`: Default citation body.
* `CitationTextUS_en`, `CitationTextJapan_en`, `CitationTextAustralia_en`: Nation-specific citation bodies.

Useful citation tokens:

* `{CommanderRank}`
* `{CommanderName}`
* `{CommanderLastName}`
* `{TaskForceName}`
* `{Self}`

Mission awards should be granted with `TaskForceModeRibbonAwards` in `campaign.ini`.

## 6. Checklists

### First Campaign Checklist

Use this checklist if you are building your first Task Force Mode campaign.

**Campaign folder:**

- [ ] Put your files under `Assets/StreamingAssets/user/<Your Mod Name>/`.
- [ ] Do not edit `Assets/StreamingAssets/original/...`.
- [ ] Create `campaigns/<your-campaign>/campaign.ini`.
- [ ] Create `player_task_force_roster.ini`.
- [ ] Create `commander_settings.ini`, even if it starts simple.

**Campaign rules:**

- [ ] Add `[TaskForceMode] Enabled=True`.
- [ ] Add starting points and point cap.
- [ ] Add at least one difficulty preset.
- [ ] Add a roster file reference.
- [ ] Add a commander settings file reference.

**Roster:**

- [ ] Add at least a few ships to `[AllowedVessels]`.
- [ ] Make sure every allowed unit has a `[TaskForce] TaskForceCost=...` value in its unit INI.
- [ ] If you use aircraft, add `[AllowedAircraft]` or `[AllowedHelicopters]`.

**Each generated mission:**

- [ ] Add `TaskForceModeMissionGenerationType=Generated`.
- [ ] Add `TaskForceModeIncludesTaskForce=True`.
- [ ] Decide if airwing or submarines are included.
- [ ] Add `TaskForceModeRearm` and `TaskForceModeRepair`.
- [ ] Add `TaskForceModeEnableTaskForceBuilder`.
- [ ] Add completion points and cap points.
- [ ] Add ribbon awards if desired.
- [ ] In the mission file, mark one player ship with `TaskForceModeAnchor=True`.

### Replaced Mission Checklist

Use this once you are comfortable with generated missions.

- [ ] Add `TaskForceModeMissionGenerationType=Replaced`.
- [ ] Place the player vessel slots exactly where you want them.
- [ ] Add `TaskForceModeReplacedUnitIndex=1, 2, 3`, etc. to replaceable vessel sections.
- [ ] Mark the preferred first slot with `TaskForceModeAnchor=True`.
- [ ] Make sure triggers still point at section names that will exist after generation.
- [ ] Remember that replaced vessel slots are filled by player surface ships.

### Air Tasking Checklist

- [ ] Add `TaskForceModeAirTaskingAvailable=True`.
- [ ] Add one unique `TaskForceModeAirTaskingFlightN` key for each flight row.
- [ ] In the mission file, author enough `Taskforce1AircraftN` or `Taskforce1HelicopterN` sections.
- [ ] Add `TaskForceModeAirTaskingRole=<RoleId>` to those aircraft sections.
- [ ] Add `TaskForceModeAirTaskingSlot=<slot number>` to those aircraft sections.
- [ ] Do not rely on ship-assigned helicopters for Air Tasking.
- [ ] Use loadout names that actually exist and are unlocked.

### JoinTaskForce Checklist

- [ ] Use `JoinTaskForce=True` only on `Taskforce...VesselN`, `Taskforce...SubmarineN`, `Taskforce...AircraftN`, or `Taskforce...HelicopterN` sections.
- [ ] Add a `CampaignTag` to the unit.
- [ ] Make sure the unit can survive and the mission reaches debrief.
- [ ] Do not use `JoinTaskForce` for land units or biologics.

## 7. Common Pitfalls and Booby Traps

Setting up a campaign using this method is complex. These are some of the common pitfalls users may encounter:

* Editing files under `Assets/StreamingAssets/original/...`. Those are base game files. Put your work under `Assets/StreamingAssets/user/<Your Mod Name>/...`.
* Forgetting `[TaskForceMode] Enabled=True`.
* Forgetting `[TaskForce] TaskForceCost=...` on a modded unit. Missing costs default to 0.
* Adding a unit to `TaskForceModeAllowedRosterUnits` but not to the main roster file.
* Repeating `TaskForceModeAirTaskingFlight1` for multiple flights. Use `Flight1`, `Flight2`, `Flight3`, etc.
* Using `JoinTaskForce=True` on land units, airbases, weapons, or custom sections. It only works on normal vessel, submarine, aircraft, and helicopter unit sections.
* Expecting `TaskForceModeRepair=True` to repair everything automatically. It only makes repair available. The unit still needs repairable damage, saved damage state, and enough points.
* Using Airbase Prep without a player airbase or airfield land unit.

## Wrap Up

Task Force Mode is a big step forward for campaign creation in Sea Power, and we are excited to finally get these tools into the hands of the community.

We built this system so mission makers and mod teams can create campaigns where the player's force has a history: ships survive or are lost, aircraft are added over time, commanders earn awards, and each mission can carry consequences into the next.

We are looking forward to see what the community creates with these new tools!

*- The Triassic Games team*
