# Mission Creation Community Guide

**Game:** Sea Power
**By:** Techno
**Posted:** Dec 26, 2024 @ 8:32pm | **Updated:** Nov 4, 2025 @ 2:23pm
**Source:** https://steamcommunity.com/sharedfiles/filedetails/?id=3392721470

> A one stop shop for everything to do with advanced mission creation. Contains information from both official documentation as well as from extensive community testing and experimentation.

---

## Introduction

This guide is a big work in progress, I will be filling out the sections as well as editing existing sections in the coming days. Formatting and structure will be inconsistent until all the content is complete. I am trying to get all the information into the guide first and then go back to make things more readable. If you have suggestions or feedback please leave a comment!

A big thanks to iBlank, Ian, that_person, SirNuggles, and everyone else in the sp-scenario-discussion channel on the modding discord.

Want to see a lot of this guide in action? Check out the author's mission pack on the workshop (id=3366829667).

## Table of Contents

Currently available sections:

- Basics & Sources
- (Conditional) Triggers
- Weather & Seastate
- Custom Air Groups
- Teleports, Formations, & Changing Sides
- Messages: Pop Up
- Messages: Intelligence (Incl. Voice Lines)
- Messages: Objectives
- Voice Lines
- Scripted Attacks
- Civilian Routes
- Briefings

---

## Basics & Sources

This guide assumes you have basic knowledge of mission creation using the mission editor. You understand the basics of creating and placing unit groups, changing their behavior, and creating and using basic triggers; all accomplished inside the mission editor.

From this base, we will explore editing the mission .ini file itself, working outside of the mission editor to achieve things otherwise not possible.

By default, your missions will save to:

```
SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\user\missions
```

> **Note:** Any changes you make outside the mission editor will be lost if you open your mission inside the editor and then save it. For this reason, create the bones of the mission (position units, set waypoints) inside the mission editor. Once you are happy with what you have, you can shift to editing the .ini directly to put in all the logic for your mission (triggers, objectives, civilian routes, etc). You should also do any testing via the scenarios menu instead of loading your mission via the editor. The editor recompiles every time you launch a mission — removing any changes you manually made.

There are two sources of official documentation available:

1. A document that covers the mission editor and explains triggers and conditions:
   ```
   SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\documentation\Mission Editor. Triggers and conditions.docx
   ```
2. An .ini that lists a lot of what you can do inside a mission:
   ```
   SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\missions\Demo\MissionFileInformation.ini
   ```

There is also a vanilla mission that utilizes a lot of what is discussed in this guide — the Warsaw Pact mission Breakthrough. You can look inside that .ini for examples of how certain things work:

```
SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\missions\Warsaw Pact\Breakthrough.ini
```

Outside of the above, almost all of the information in this guide has come from the sp-scenario-discussion channel on the official modding discord. We have a wonderful little community full of knowledgeable mission makers who are happy to test things and help each other out. If you're looking to make missions and have questions, you're encouraged to join: https://discord.gg/vc8uAVH6Sh

---

## (Conditional) Triggers

### Anatomy of a Trigger

Triggers are the fundamental building blocks of your mission logic. It is important you understand how they work and what you can do with them. Triggers have three parts:

- Trigger Definition
- Conditions
- Trigger Actions

As an example:

```ini
[Trigger1]
Name=MissionFail_CarrierLost
Description=Ends mission if the player carrier is sunk
Condition_NimitzSunk_Description=Checks if the Nimitz is sunk
Condition_NimitzSunk_Type=UnitDestroyed
Condition_NimitzSunk_Units=Taskforce1Vessel1
Condition_NimitzSunk_MinimumUnits=1
ConditionsCompleted=<NimitzSunk>
Action_Taskforce1_Message=Taskforce1MissionFail_CarrierLostMessage
Action_EndMission=True
Action_Victory=Taskforce2
```

**Trigger Definition**
- *Name* is the trigger name, it is used to reference this Trigger in other places.
- *Description* is for your own use to keep track of what each Trigger does.

**Conditions**

Conditions are the logic systems inside of triggers. You can have multiple Conditions inside a single trigger and you can use logic operators to set rules on which Conditions complete the Trigger.

You can create a Condition simply by defining a name and a type:

```
Condition_<name>_Type=<type>
```

You can get a list of valid types from the mission editor.

- *Description* is for your own use to keep track of what each Condition does.
- *Units* defines which units the Condition applies to.
- *MinimumUnits* defines how many units must be destroyed before the condition is considered complete.

Depending on the condition type, there could be other Condition fields — `_Time` or `_Position` as examples. As a general rule, time is in seconds from mission start and position is in NM relative to the mission center. Create different Conditions via the mission editor and have a look in the resulting .ini to see the details. As you get more familiar with conditions and triggers, you will be able to write them entirely from scratch.

**Trigger Actions**
- *ConditionsCompleted* defines what Conditions must be completed before the Trigger takes its actions. Typically, as in the above example, only one Condition is used.
- *Taskforce1_Message* displays a popup message for the player. The actual message is defined in the *Language_en* section near the top of the .ini.
- *EndMission* ends the mission.
- *Victory* sets which side won the mission.

There are plenty more actions a Trigger can accomplish; you can see more by jumping to a section of the guide that you are interested in.

**Remember:** Conditions are the rules you set up, checking to see if something has happened. Trigger Actions are the actions that take place once the Conditions have been met.

> **Note:** If you manually add Triggers, make sure to update the *NumberOfTriggers* field in the *Mission* section of your .ini. Also note that Triggers have a chance of not working properly if they are set to fire right at mission start or if they fire during heavy time acceleration.

### Conditional Triggers

You can have multiple Conditions defined inside a Trigger and you can use terms such as AND, OR, NOT, etc to create some rules for your Conditions. See section **Conditions Complete Rule** in the official Triggers and Conditions document for more details.

As an example, you could have a Trigger fire if you lose a ship but only if that ship has not reached a certain area yet. If the ship is lost after reaching the defined area, the Trigger will not fire. This would be accomplished using a UnitLost Condition and a UnitsInTheArea Condition with the ConditionsCompleted being `<ConditionLost> AND NOT <ConditionArea>`.

Using conditional Triggers is an easy and powerful way of adding more advanced logic into your missions.

---

## Weather & Sea State

Weather and Sea State can be controlled via Triggers, giving you control of the environment during longer missions.

Inside your trigger:

```ini
Action_SetSeaState=3 (0 to 12, with 1 to 10 being recommended)
Action_SetClouds=Clear (Clear,Scattered,Scattered_1,Scattered_2,Broken,Broken_2,Broken_3,Overcast)
Action_SetRain=True/False
Action_SetThunderstorm=True/False (Only works if clouds are also Overcast)
Action_SetSnow=True/False
Action_SetFog=True/False
```

You can see examples of this in action in *Breakthrough.ini* (mentioned in the Basics & Sources section of this guide). Note that the sea state and weather change the level of ambient noise, making it easier/harder to detect submarines.

---

## Custom Air Groups

You can overwrite the default air wing of any unit that has a flight deck — carriers, airbases, etc.

As an example:

```ini
[Taskforce2Vessel7]
Type=wp_takr_kiev
VariantReference=Variant1
MissionType=NoMission
WeaponStatus=Free
RadarsActive=True
CrewSkill=Trained
Stores=Full
Damage=None
RelativePositionInNM=-24.15,0,-3.13
Heading=60
CustomAirGroup=True
FlightDeckAIDisabled=True
wp_yak-38=Squadron2,12|Squadron4,12
wp_mig-23a=Squadron1,6
wp_ka-25=Default,4
wp_ka-27=Squadron1,16
```

Adding in *CustomAirGroup=True* overwrites the default air group. If you do not specify any further information, the unit will spawn with no aircraft.

- The Mig-23A squadron will not be added because Kiev class does not support it.
- Only 8 KA-27s will be added because of Kiev's max capacity of 36 aircraft.

See the following folder for a list of all aircraft in the game:

```
SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\aircraft
```

*FlightDeckAIDisabled=True* is optional. This line prevents this unit from launching anything of its own accord. Presumably with a custom air group you want to control what launches when and what the aircraft do. See the Civilian Routes section for more.

*This example was copied straight out of the official MissionFileInformation.ini*

---

## Teleports, Formations, & Changing Sides

### Teleports & Formations

Using *Action_TeleportToPositon* it is possible to teleport a group of units upon a Trigger firing. However, if multiple units are being teleported they will spawn in the same location, inside of each other. To prevent this, a default formation **must** be used.

Place your unit group down in the mission editor as usual. When you are ready to edit the .ini, find the formation under the *[Mission]* section of the file. As an example:

```ini
Taskforce1_Formation1=Taskforce1Vessel1,Taskforce1Vessel2|My Teleport Squadron|LineAbreast|0.5|OverrideSpawnPositions
```

The arguments of the formation in order:

- All the vessels in the formation, separated by commas
- Name of the formation that shows up in game
- The default formation type (see below)
- Formation spacing in NM
- *OverrideSpawnPositions* means when the formation is teleported, they will be spawned in formation (optional)

When teleporting into formation, units will reform the **original** formation shape and spacing, not the relative positions they were in at the moment of teleporting. If you remove a vessel from the formation or disband the formation entirely, the units will teleport into one location; inside of each other.

The available default formations are:

```
Loose, Circle, Vic, Echelon, LineAbreast, LineAstern, Box
```

There are two WIP additional types, Convoy and Battlegroup. Use these at your own peril.

### Changing Sides

Using *Action_UnitTransferToTaskForce*, it is possible to swap a unit's side between blue, red, and green. When a unit changes sides, they lose all orders they may have had. To fix this issue, you can issue the units new orders in the same trigger that teleports them. As an example:

```ini
Action_UnitHeading=125
Action_UnitTelegraph=2
Action_UnitVelocityInKnots=10
Action_UnitWaypoints=-5.2,0,-7.4|-2.4,0,-7.82|-1.23,0,-5.67
```

There is more to explore with unit movement — you can randomize course and turns as well as spawns. More details can be found in the official *MissionFileInformation.ini*.

---

## Messages: Pop Up

The simplest way of conveying information to the player. A pop up message pauses the game and presents a message. Using *Action_Taskforce1_Message* as part of a Trigger, you can display messages to the player at various points in your mission.

The message itself is defined in the *Language_en* section of your .ini. As an example:

```ini
Inside your trigger:
Action_Taskforce1_Message=Taskforce1MissionEndMessage

Inside [Language_en]:
Taskforce1MissionEndMessage=<size=40><color=Lime>MISSION COMPLETE</color></size>|Well done, you have completed your objectives.\n\nThis operation is a success.|Exit Mission
```

A message has three parts: the title, the body, and the button. Each section is separated by a `|` character. You can use `<size>` and `<color>` tags in your messages. Accepted colors can be found in the .NET `System.Windows.Media.Colors` reference (learn.microsoft.com). You can also input any hex color using the following format:

```
<color={*}D2B48C>message</color>
```

Use `\n` for linebreaks. The game also supports using emojis. 🚢⚓

> **Warning:** Avoid using special characters such as `#` or `/` anywhere in your .ini. These characters are used to denote comments and if used inside a message or a Trigger name, may break your mission file.

---

## Messages: Intelligence

The intelligence system allows you to present the player with messages that show up in the Intelligence tab (in the same window as the Event Log). The benefit of this system is that the messages are delivered with time stamps and are persistent through the entire mission, allowing the player to look back at all the past messages. The downside is that this system is not well known and it can be easy to miss new messages, even with voice lines informing the player that a new message was received. Until this system becomes more popular, a good compromise would be to deliver the full details with a pop up message and a summary with an intel message.

Mechanically, intelligence messages are very similar to pop up messages. *Action_Taskforce1_Intel* goes inside a trigger and the intel message itself is defined in *Language_en*. As an example:

```ini
Inside your trigger:
Action_Taskforce1_Intel=StartIntel

Inside [Language_en]:
StartIntel=Primary Objective: Destroy the Weapons Complex
```

Voice Lines go great with the Intelligence feature, see section Voice Lines for more.

Note that XAML tags don't seem to work inside Intelligence Messages.

---

## Messages: Objectives

Objectives are another tool to convey messages to the player. Objectives will show up in the After Action Report at the end of the mission. This screen can also be accessed at any time by hitting Escape and then Exit. You are still able to return to the mission from the AAR screen.

Objectives have three parts: they must be defined, they must be given a message, and they must be actioned.

To define an Objective, you must create an entirely new section in your .ini. Example:

```ini
[Taskforce1_Objectives]
#ID=CompletedScore,FailedScore,StatusAtMissionEnd
ProtectYorktown=0,-10,Complete
DestroyTransports=10,-15,Fail
ProtectCivilians=0,-10,Complete
```

The *CompletedScore* and *FailedScore* play into the scoring system but the inner mechanics of that are a complete mystery (please get in touch if you know how scoring works). The *StatusAtMissionEnd* does not seem to work at the moment.

To define what shows up in the AAR for each objective, you must add a line inside *Language_en*. Example:

```ini
Inside [Language_en]:
Objective_ProtectYorktown=Main: The Yorktown must survive
Objective_DestroyTransports=Main: Identify and sink all enemy transports
Objective_ProtectCivilians=Main: Do not engage any civilian vessels
```

Finally, to action an objective you must add a line inside a Trigger. Example:

```ini
Inside your trigger:
Action_ObjectivesCompleted=DestroyTransports,ProtectYorktown
Action_ObjectivesFailed=ProtectYorktown
```

If you want to action multiple Objectives, use commas. Do not use multiple lines of *Action_ObjectiveCompleted/Failed* — the game will not recognize this.

You are able to create Hidden Objectives by adding *Hidden* to the end of the Objective definition. These Objectives will not show up in the AAR unless they have been Completed or Failed. Example:

```ini
DestroyAirbase=5,0,Fail,Hidden
```

---

## Voice Lines (Custom Audio)

Sea Power supports playing audio clips as part of a Trigger's actions. As an example:

```ini
Inside your trigger:
Action_Taskforce1_VoiceMessage=NewTaskReceived
```

Combining these voice messages with your messages can help create a more immersive mission as well as alert the player to a new message.

The most relevant ones for objectives and intel messages are: `MissionFail`, `MissionComplete`, `NewTaskReceived`, `NewIntelReceived`, `ObjectiveComplete`, `ObjectiveFailed`.

You can find the full list of messages in:

```
SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\audio\voiceover\voice.ini
```

There are two voices, one for NATO and one for WP. The voice is automatically chosen depending on the side of the units the player has (e.g. if you have a soviet airbase and a soviet ship you will get the WP voice; if you have mixed units it goes with the side of whatever your first unit is). Be aware that not all messages have their associated audio clips available yet, especially on the WP side.

You are also able to supply your own audio clips. You will need your own .wav as well as to create an updated copy of the voice.ini file. Place your .wav and the updated .ini in the appropriate folders (see Folder Structure section).

Inside voice.ini, define your .wav copying the format used for vanilla clips:

```ini
TestSound=audio/voiceover/us/3B/TestSound.wav,2
```

The comma and number following your file path determine the priority of your voice line if multiple audio clips are attempting to play at once. See the top of voice.ini to see which types of messages have what priority. To use your audio:

```ini
Inside your trigger:
Action_Taskforce1_VoiceMessage=TestSound
```

Thanks to Sinlos and Plasm@n for their help with this section.

---

## Scripted Attacks

Scripted Attacks are a powerful tool which allow you to force units to attack designated units at a specific time and place. From *MissionFileInformation.ini*:

```ini
//Attack=Taskforce2Vessel1,1,wp_ss-n-12,4,wp_1|Taskforce2Vessel1,10
#possible variants: Template:
#targetObject,timeOfAttack,ammunitionFileName,numberOfShots,waypointNumber|<next entry>
# targetObject: required, ALWAYS expected to be 1st entry
# timeOfAttack: optional, ALWAYS expected to be 2nd entry. In seconds from mission start or reaching waypoint (if specified).
# ammunitionFileName(optional), can be any of 3rd+ entry
# numberOfShots(optional), can be any of 3rd+ entry
# waypointNumber(optional), can be any of 3rd+ entry. Allows to start attack AFTER reaching specified waypoint. If waypoint do not exist - attack is canceled
```

The attack line goes inside a unit. As an example:

```ini
[NeutralAircraft1]
Type=usn_s-3a
SquadronReference=Default
LoadoutVariant=AntiShip
MissionType=NoMission
WeaponStatus=Tight
RadarsActive=True
CrewSkill=Trained
Stores=Full
Damage=None
RelativePositionInNM=-11.05,3000,-0.57
Telegraph=3
Heading=102
Waypoints=-7.1469,3000,-1.4137|-5.1559,3000,-3.4449|-1.9796,3000,-3.7868|-1.4767,3000,3.5938|-9.9432,3000,3.8553
Attack=Taskforce2Vessel1,1,usn_agm-84,1,wp_3
```

This attacks the designated target upon reaching way-point 3 with a single Harpoon.

This method works on any side against any target. You can use this to have green attack red, red attack blue, or even blue attack blue.

Keep in mind the unit must have vision of its target at the assigned attack time/location otherwise the attack will not work. This vision can either be from itself or relayed by other units on its team.

**Unrelated** to scripted attacks (but there was nowhere else to put it): guided missile submarines will not use their missiles to attack by default. If you want to enable this behavior, you must add:

```ini
Inside [Taskforce2Submarine1]:
AllowedTargetForMissiles=Taskforce1Vessel2,Taskforce1Vessel5
```

You must specify each valid target. Keep in mind this may result in all missiles launching, causing almost certain death for the player vessels. You can instead use scripted attacks to launch a few missiles at a time over a longer period of time.

---

## Civilian Routes (Scripted Unit Spawning)

Civilian Routes are another very powerful tool to use in your missions. Civilian Routes allow you to launch aircraft from airbases and ships and have them fly a predetermined route. This feature is oddly named because it can be used to launch any kind of aircraft for any team — it is not limited to civilian aircraft.

```ini
[CivilianRoute3]
StartTime=600
Taskforce=Taskforce2
SpawnFrom=Taskforce2LandUnit7
DespawnAt=Taskforce2LandUnit7
UnitType=Aircraft
AllowedUnits=wp_mig-25pd,usn_f-4j
AllowedNations=all
AllowedLoadouts=AirToAirLongRange,LongRangeIntercept
EnableWeaponsAtWaypoint=1
MaxUnits=5
SpawnInGroupsOf=2
SpawnInterval=300,400
Waypoints=-12.3005,3000,-8.0941|5.4689,3000,-3.1688|21.9825,3000,-11.1281|43.0775,3000,-38.7319
```

- **StartTime** — when does the first unit spawn, in seconds from mission start.
- **Taskforce** — this should set the side that the unit spawns on but this seems to be overridden by the side of the launching platform. i.e. a green airbase can only ever spawn green planes.
- **SpawnFrom, DespawnAt** — where the unit spawns from and where it tries to land at.
- **UnitType** — theoretically could be Vessel or even LandUnit but no luck getting those to work in testing.
- **AllowedUnits** — defines which units can spawn.
- **AllowedNations** — defines which countries are valid.
- **AllowedLoadouts** — defines which loadouts the aircraft spawn with. Use "all" for units that don't have loadouts.
- **EnableWeaponsAtWaypoint** — defines at which waypoint the unit starts to think for itself. Prior to weapons being enabled, the spawned unit will strictly follow the waypoints. Post enabling, the unit will follow the waypoints if it has no valid targets. Otherwise it will turn to engage. Keep in mind targeting info is shared across the team so another unit across the map could feed the spawned unit a valid target.
- **MaxUnits** — how many spawned units (not groups) in total can exist.
- **SpawnInGroupsOf** — how many units to spawn at once.
- **SpawnInterval** — when should the units be spawned. In this example, the first group of 2 will spawn at 600 seconds, the next at 900 seconds, and the final single unit (because the max limit is 5) at 1300 seconds. The SpawnInterval is a queue to spawn, not a check to spawn. This means that at 1300 seconds, only 1 fighter is spawned because the max allowed in the world is 5. But at 1350 seconds, if an existing fighter lands or is destroyed, the remaining fighter will immediately launch.
- **Waypoints** — the waypoints the spawned units should follow. The middle number is altitude in feet. The easiest way to get these numbers is to spawn a unit in the mission editor and give it the path you want your units to follow. Then copy the waypoints from the file and put it into your civilian route. It is recommended to have at least two waypoints to avoid odd pathing behavior with units.

Civilian Routes are placed outside of any other section in your .ini — e.g. you can place them at the bottom of the file and they'll work fine.

> **Note:** You must add a `NumberOfCivilianRoutes=1` field in the *[Mission]* section of your .ini. Adjust the number to match the number of routes you have.

It is best to pair Civilian Routes with Airbases with Custom Air Groups (see previous section). The spawning unit **must** have the requested units for the Civilian Route to work. Civilian Routes do not spawn units out of thin air. You can add `FlightDeckAIDisabled=True` inside your airbase's *[LandUnit]* to prevent it from trying to launch its own strikes.

**Other uses:**
- Should work for blue side but may get wonky if the player is also issuing commands.

**Not working:**
- Breakthrough offers civilian routes with no spawn and despawn locations, just waypoints — testing this had no success.
- Breakthrough also has ships spawning from ports, but this has not been able to be replicated. Not even sure if it works in the original mission or not.

---

## F10 Menu

*TBA*

---

## Briefings

Briefings provide the player with detailed information at the start of a mission. Briefings allow you to set the scene, give specifics, and provide context for the mission. Briefings are made up of a left pane and a right pane.

### Set Up

To create a briefing, you must add the relevant lines inside your mission.ini as well as set up the proper folder structure and briefing files in your mod folder.

```ini
Inside [Language_en]
MissionBriefingAssetsDirectory=missions/My Mod/briefings/My Mission 1 Briefing
MissionBriefingAssetsSearchPattern=*.jpg,*.png
MissionBriefingLeftPane=missions/My Mod Missions/briefings/My Mission 1 Briefing/mm1_left.xml
MissionBriefingRightPane=missions/My Mod Missions/briefings/My Mission 1 Briefing/mm1_right.xml
```

- **MissionBriefingAssetsDirectory** defines the directory where all the briefing assets are located for this mission.
- **MissionBriefingAssetsSearchPattern** defines what extra asset types to look for. Typically these are images you want to use in your briefing. Untested — other formats such as audio or video may be supported.
- **MissionBriefingLeftPane** defines the path for the left pane file.
- **MissionBriefingRightPane** defines the path for the right pane file.

To set up your folders, inside your `<mymod>/missions/<mymodmissions>` folder, create another folder. This folder will contain all of your briefing folders. Inside this newly created folder, you will need an `_info.ini` as well as a folder for each mission you want a briefing for. See the Folder Structure section for a visual depiction of this.

Your `_info.ini` should contain:

```ini
[General]
Hidden=True
```

This hides the top level briefing folder and prevents it from showing up in the scenario browser in game.

### Contents

Typically, the left pane of a briefing is where all your text goes and the right pane is used as a visual aid — a map or other graphic. The easiest way to get started is to copy an existing briefing from the base game. For example:

```
\SteamLibrary\steamapps\common\Sea Power\Sea Power_Data\StreamingAssets\original\missions\NATO\Trollfjorden_briefing
```

The right pane is simple — change out the image name with your image's name and update the image size to match your image. Make sure you've defined the file type correctly in your mission.ini. The left pane is slightly more complicated, but all you need to do is edit the text until you're happy with what you have. The panes are .xml files and the game supports BBCode formatting as well as XAML. XAML is very powerful and you can do almost anything you want if you know what you're doing. For an example, look at the right pane of Dong Hoi's briefing.

### Left Pane Format

The format followed in the left pane is that of an Operations Order. An Operations Order follows the SMEAC format, also known as a 5 paragraph order. SMEAC stands for Situation, Mission, Execution, Admin/Logistics, and Command and Control. Within Sea Power, Admin and C2 currently do not play a large role. Instead, you can replace Admin and C2 with OOB (Order of Battle) listings for both REDFOR and BLUFOR as a way to give your player some insight on what they're launching into (or deceive them with faulty intelligence on REDFOR assets).

The top header (FM, TO, INFO, SUBJ) is fluff to help immersion.

1. **Situation** — General overview of the current geopolitical situation, big picture of what your player is setting out to do in this mission.
2. **Mission** — 2.1 Medium picture view of what your player should go do during this scenario.
3. **Execution** — 3.1 Specific tasks or direction to your player, could be used to guide them at scenario start.
4. **Enemy OOB** — 4.1 Enemy ship 1, 4.2 Enemy ship 2
5. **Friendly OOB** — 5.1 Friendly ship 1, 5.2 Friendly ship 2
6. **Remarks** — 6.1 Extra info as a way of rounding out the reading for a player.

Adjust this format as needed to fit your mission. You do not need to include every section.

*An online tool to generate NATO symbols:* https://spatialillusions.com/unitgenerator/

Special thanks to iBlank for their help with writing this section of the guide.

---

## Custom Units

*TBA*

---

## Folder Structure & Uploading

*TBA*

**Quick and dirty:**

Your mod folder should be located in streamingassets. Inside your mod folder should reflect the same structure as inside streamingassets/original. Upload your `My Mod` folder.

The `_info.ini` inside your `My Mod` folder should have:

```ini
[Language_en]
Name=My Mod's Name
Description=A short description of what My Mod does.
```

This is what shows up inside the mod list in game.

```
streamingassets/
└── My Mod/
    ├── _info.ini
    └── missions/
        └── My Mod Missions/
            ├── briefings/
            │   ├── _info.ini
            │   └── My Mission 1 Briefing/
            │       ├── My Mission 1 Briefing Left.xml
            │       ├── My Mission 1 Briefing Right.xml
            │       └── My Mission 1 Briefing Map.png
            ├── My Mission 1.ini
            ├── My Mission 2.ini
            ├── My Mission 3.ini
            └── My Mission 4.ini
```

---

## Mission Design Tips

*TBA*

---

## Unimplemented Features

- Stores
- Damage
- Missions

---

*Guide content retrieved from Steam Community. Note: at the time of retrieval, this item was flagged as removed from the Steam Community for violating Content Guidelines and visible only to the guide's owner; the text above reflects the content that was accessible via search engine cache/fetch.*
