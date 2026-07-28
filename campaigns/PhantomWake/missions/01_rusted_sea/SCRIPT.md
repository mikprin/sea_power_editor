### **MISSION 01: RUSTED WATERS**

**CLIENT:** REDACTED (Corporate Proxy)
**LOCATION:** Gulf of Guinea, West Africa.
**ASSETS AVAILABLE:** *Obsidian Orcas* Task Force (Player's custom fleet)

**SITUATION:**
Welcome to the ocean, Commander. The geopolitical map doesn't care about our new enterprise, which means we start at the bottom of the food chain. Our first contract is live.

We have been hired by a corporate proxy to escort the MV *Vagabond*, a civilian container ship, through the Gulf of Guinea. The client has paid a premium to keep this transit strictly off the books. Local authorities are not to be involved. The waters ahead are heavily congested with local fishing fleets, smugglers, and well-armed pirate skiffs.

**OBJECTIVES:**

1. Rendezvous with MV *Vagabond* and assume escort formation.
2. Escort the vessel safely to the designated international waters waypoint (NavPoint Alpha).
3. Ensure the survival of your Task Force.

**RULES OF ENGAGEMENT (ROE):**
Weigh your targets carefully. You are authorized to use lethal force ONLY to defend the client vessel or your own Task Force. Identify all radar contacts visually before engaging.

---

### 🗺️ Scenario Structure

**Phase 1: Rendezvous in the Fog**

* **Action:** The *Obsidian Orcas* Task Force spawns in the deployment zone. The weather is terrible—heavy fog and low visibility.
* **Atmosphere:** The radar is already picking up multiple faint, distant contacts (background commercial traffic on the horizon). The ocean feels alive and unpredictable. You must link up with the MV *Vagabond*.

**Phase 2: The Paranoia Zone**

* **Action:** As the convoy proceeds, it enters a highly congested coastal zone. Around 8 to 12 small surface contacts appear on the radar, crisscrossing the *Vagabond's* path.
* **The Trap:** Because of the fog, your targeting sensors cannot distinguish between innocent fishermen and threats. You must maneuver your Task Force to intercept and visually identify the closest boats.
* **Ambush:** Suddenly, three of the skiffs break away from the civilian cluster, throttle up to maximum speed, and make a run for the cargo ship. They are armed. You must neutralize them without hitting the surrounding neutral boats.

**Phase 3: The Ghost in the Machine (The Twist)**

* **Action:** Just as the pirates are dealt with, the *Vagabond* radios in a panic. Their navigational systems have gone completely blind.
* **The Threat:** Your own Task Force receives a sudden, massive spike in Electronic Warfare (EW) interference. A warning pops up: *Military-grade jamming detected.* (An unseen EW aircraft is operating high above the clouds).
* **Escalation:** The jamming is a smokescreen. Bursting through the fog at low altitude is an unidentified, heavily armed military transport helicopter. It ignores your warnings and heads straight for the *Vagabond*.

**Phase 4: Boarding Action (The Timer)**

* **Action:** The helicopter is carrying elite commandos aiming to secure the secret cargo in the *Vagabond's* hold.
* **The Climax:** If the helicopter manages to reach the airspace directly above the cargo ship, a 120-second timer begins. The commandos are fast-roping onto the deck. You have exactly two minutes to shoot the helicopter out of the sky before they breach the secure containers.

---

### ⚙️ Trigger Logic Plan (For the `.ini` file)

Here is the blueprint for how to wire this in the Sea Power Mission Editor:

**1. Ambient Clutter (Background Ships)**

* **Setup:** Place 4–5 large merchant vessels far away from the main engagement zone.
* **Action:** Assign them standard `Civilian Routes` so they wander aimlessly in the background, creating false radar tracks for the player to worry about.

**2. Start Escort**

* **Condition:** `Unit Enters Area` (Player Task Force comes within 2 nautical miles of MV *Vagabond*).
* **Action:** `Popup Message` — Captain of the *Vagabond* confirms visual and requests escort.
* **Action:** `Assign Waypoints` — *Vagabond* begins moving toward NavPoint Alpha.

**3. The Swarm (Paranoia Zone)**

* **Condition:** `Time Elapsed` (e.g., 5 minutes after escort starts).
* **Action:** Enable 8–12 small wooden boats around the convoy's path. Set their `Alliance` to `Neutral`.

**4. Pirate Ambush**

* **Condition:** `Distance to Unit` (*Vagabond* gets within 4 miles of the ambush group).
* **Action:** `Change Alliance` — Three specific fast skiffs change to `Hostile`.
* **Action:** `Popup Message` — "Warning: Multiple small craft accelerating on intercept course!"

**5. The Real Threat (EW & Commando Helo)**

* **Condition:** All pirate skiffs destroyed (`Unit Destroyed`) OR convoy reaches the halfway point.
* **Action:** `MissionWarningMessage` — *"WARNING: Severe broadband EW interference detected. Radar degraded. This is military-grade equipment."*
* **Action:** Enable/Spawn the hostile military helicopter on the edge of the map, ordering it to move directly to the *Vagabond's* coordinates.


**6. The Boarding Timer (Crucial Logic)**

* **Condition:** `Unit Enters Area` (Hostile Helicopter enters a tiny radius right on top of the MV *Vagabond*).
* **Action:** `Popup Message` — *"COMMANDOS ARE BOARDING! REPEAT, THEY ARE ON THE DECK!"*
* **Action:** `Start Timer` (Set for 200 seconds).

**7. Win / Lose Conditions**

* **Lose Condition 1 (Cargo Captured):** Timer expires. `Popup Message` — *"Cargo breached. Contract failed."* -> `End Mission (Defeat)`.
* **Lose Condition 2 (Ship Sunk):** MV *Vagabond* or Player Task Force is completely destroyed.
* **Helo Destroyed (Save):** If the hostile helicopter is destroyed (`Unit Destroyed`), stop the timer. `Popup Message` — *"Threat neutralized. The deck is clear."*
* **Win Condition:** MV *Vagabond* safely reaches NavPoint Alpha, and the hostile helicopter is destroyed. — *"Escort complete. Contract fulfilled."* -> `End Mission (Victory)`.