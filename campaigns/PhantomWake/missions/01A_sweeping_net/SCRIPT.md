### **CONTRACT 01-A: OPERATION SWEEPING NET**

**CLIENT:** Regional Fishing Conglomerate
**LOCATION:** Pemba Channel, Tanzanian Coast, East Africa
**TIME / WEATHER:** 14:00 Local, 2 July 1985, Clear Skies, Sea State 1

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
* **Action:** 5 small civilian fishing boats (dhows, sampans, fishing boats) scattered across the search sector, with 2 deep-ocean freighters transiting at extreme range for background clutter.
* **Condition:** `Alliance = Neutral`, `AutomateRoute=True` for organic movement.
* These act as radar clutter and obstacles. The player must navigate around them to find the real targets.


* **The Pirates (Hostiles):**
* **Action:** 4 fast, lightly armed pirate skiffs (three wp_pt_p4 + one ir_pt_parvin) patrol the search sector on an authored northeast course at Telegraph 4.
* **Behavior:** They are hostile from mission start (`WeaponStatus=Free`), moving under their own orders — not hiding stationary.
* **Trigger (Aggro):** `UnitDetected` on any one skiff. When the player's sensors actually acquire the flotilla, a warning pops up. No scripted status change — they are already weapons-free and will engage at contact range.


* **End Conditions:**
* **Victory:** All 4 pirate skiffs destroyed. Triggers: `[ATLAS]: "Targets neutralized. The conglomerate just wired the funds. Good hunting, Commander."`
* **Defeat:** Player task force wiped out (no vessels remaining) OR one or more neutral fishing boats destroyed (immediate contract termination, no partial payment).

---

#### **4. Optional Subplot: Syndicate Surveillance Asset**

* **Hidden element:** An unidentified diesel submarine (Australian Oberon-class, Nation=Terrorists) loiters passively in the search sector.
* **Trigger (Detection):** When the player's sonar acquires the contact, an ECHO alert pops: unidentified acoustic signature, non-standard sensor fit, no transponder.
* **Optional Objective (Hidden):** Destroy the unidentified contact. Reward: 5 points, no penalty if ignored. Does NOT affect ProtectCivilians or the primary victory condition.
* **Significance:** Not part of the conglomerate's contract — a Syndicate spy asset, flagged for the record. Killing it is a bonus, not a requirement.