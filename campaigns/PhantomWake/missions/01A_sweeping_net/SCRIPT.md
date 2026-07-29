### **CONTRACT 01-A: OPERATION SWEEPING NET**

**CLIENT:** Regional Fishing Conglomerate
**LOCATION:** Somali Coastline, Horn of Africa
**TIME / WEATHER:** 14:00 Local, Clear Skies, Calm Seas

#### **1. In-Game Briefing (UI Text)**

**[ATLAS]:** "Listen up, Commander. If we want to upgrade this rusted fleet, we need steady capital. A regional fishing conglomerate is losing their harvest and their crews to a localized pirate ring. The local coast guard is either too underfunded or too corrupt to handle it, so they outsourced the problem to us.
They are paying a flat bounty to clear the sector. No political strings, no secret cargo. Just a straightforward sweep. Get in, identify the hostiles hiding among the fishing fleet, and send them to the bottom. Let’s make this quick and profitable."

**[ECHO]:** `RADAR TOPOGRAPHY: CLEAR. SEA STATE: 1. MULTIPLE SURFACE CONTACTS DETECTED IN THE COMBAT GRID. TACTICAL ANALYSIS: HOSTILE SKIFFS ARE MASKING THEIR SIGNATURES BY LOITERING NEAR CIVILIAN FISHING VESSELS. VISUAL IDENTIFICATION REQUIRED BEFORE WEAPONS RELEASE.`

#### **2. Mission Objectives**

* **Primary Objective:** Locate and destroy all Armed Pirate Skiffs.
* **Secondary Objective (ROE):** Ensure zero civilian casualties. Do not fire upon neutral fishing vessels.
* **Tactical Restriction:** Conserve heavy ordnance. The bounty payout will not cover the cost of a spent anti-ship missile. Rely on deck guns and close-quarters maneuvering.

---

#### **3. Editor & Trigger Logic Breakdown**

This mission relies on close-quarters maneuvering and target identification rather than long-range missile duels.

* **Deployment Phase:**
* The player spawns their Task Force using the designated deployment zone.
* The environment features scattered small islands or coastal shallows to restrict movement.


* **The Civilian Fleet (Neutrals):**
* **Action:** Spawn 6 to 8 static or slow-moving civilian fishing boats scattered randomly across the center of the map.
* **Condition:** `Alliance = Neutral`.
* These act as radar clutter and obstacles. The player must navigate around them to find the real targets.


* **The Pirates (Hostiles):**
* **Action:** Spawn 5 fast, lightly armed pirate skiffs (e.g., modified P4-class and basic motorboats (ir_fab_boghammar)).
* **Behavior:** They begin stationary, hiding right next to neutral fishing boats.
* **Trigger (Aggro):** `Distance to Unit`. When the player's Task Force approaches within 3 Nautical Miles, the pirate skiffs break cover, accelerate to maximum speed, and swarm the player's ships using unguided rockets or heavy machine guns.


* **End Conditions:**
* **Victory:** `Unit Destroyed` (All 5 Pirate Skiffs are sunk). Triggers a success message: `[ATLAS]: "Targets neutralized. The conglomerate just wired the funds. Good hunting, Commander."`
* **Defeat:** `Unit Destroyed` (Player's flagship is sunk) OR `Alliance Engagement Violation` (Player sinks a neutral fishing boat, leading to an immediate contract termination).