
MISSION 01: RUSTED WATERS

CLIENT: REDACTED (Corporate Proxy)
LOCATION: Gulf of Guinea, West Africa.
ASSETS AVAILABLE: ---

SITUATION:
Welcome to the ocean, Commander. The geopolitical map doesn't care about our new enterprise, which means we start at the bottom of the food chain. Our first contract is live.

We have been hired by a corporate proxy to escort the MV Vagabond, a civilian container ship, through the Gulf of Guinea. The client has paid a premium to keep this transit strictly off the books. Local authorities are not to be involved. The waters ahead are heavily congested with local fishing fleets, smugglers, and well-armed pirate skiffs.

OBJECTIVES:

    Rendezvous with MV Vagabond and assume escort formation.

    Escort the vessel safely to the designated international waters waypoint (NavPoint Alpha).

    Ensure the survival of your Task Force.

RULES OF ENGAGEMENT (ROE):
Weigh your targets carefully. You are authorized to use lethal force ONLY to defend the client vessel or your own ship.

Commander's Note: We are operating on a razor-thin budget. Do not waste million-dollar guided missiles on wooden speedboats. Use your deck gun and conserve your heavy stores for when we actually need them. Identify all radar contacts visually before engaging. If you sink local fishermen, the penalty fees will bankrupt us before this PMC even gets off the ground.


SCRIPT:

Here is the expanded and updated mission scenario in English, incorporating a denser radar environment with more boats and distant background contacts to heighten the tension.

### 🗺️ Scenario Outline: Mission 01 - "Rusted Waters"

**Phase 1: Rendezvous in the Smog**

* **The Setup:** The player deploys their single, budget-constrained task force in the Gulf of Guinea. The weather is poor—heavy coastal fog and rain limit visual range.
* **The Action:** The player must navigate to the rendezvous coordinates to meet the client's container ship, MV *Vagabond*.
* **The Atmosphere:** The radar is cluttered. Far on the horizon, the player picks up intermittent, massive surface contacts (distant supertankers) and high-altitude commercial flights. They pose no threat, but they create a chaotic electronic environment where it is hard to isolate real dangers.

**Phase 2: The Crowded Gulf**

* **The Action:** Once the escort formation is established, the convoy enters a narrow transit corridor. The radar suddenly lights up with a large cluster of small surface contacts (8–12 boats).
* **The Problem:** These are local fishing dhows and merchant skiffs. They are moving erratically, crossing the convoy's path. The player must use searchlights or close the distance for visual identification. Firing a missile blindly into this crowd is a severe ROE violation.

**Phase 3: The Swarm**

* **The Ambush:** The paranoia pays off. Four of the "fishing boats" suddenly accelerate to 35+ knots, breaking away from the neutral pack and converging on the *Vagabond* from multiple vectors.
* **The Combat:** The player must skillfully maneuver their task force to intercept the speedboats, relying on the main deck gun and close-in weapon systems (CIWS) to neutralize the threat without accidentally sinking the surrounding civilian vessels.

**Phase 4: The Twist**

* **The Revelation:** The pirate threat is neutralized, but the *Vagabond* suddenly reports total GPS and radar failure. They are being jammed by military-grade Electronic Warfare (EW).
* **The Real Threat:** A new, highly distinct contact breaches the fog. It is a modern fast-attack missile craft (or a heavily armed PMC gunship helicopter), broadcasting an active fire-control radar. They demand the *Vagabond* halt for immediate boarding. The player realizes the cargo is not fertilizer, and they are hopelessly outgunned. The objective shifts from a slow escort to a desperate retreat.

---

### ⚙️ Trigger Logic Plan (For the `.ini` File)

Here is how you can structure the backend logic in the Mission Editor to make this scenario work:

* **Trigger 1: Initiate Escort**
* **Condition:** `Unit Enters Area` (Player task force comes within 2 nautical miles of MV *Vagabond*).
* **Action:** `Popup Message` (Captain of the *Vagabond* confirms visual contact and begins moving).
* **Action:** `Assign Waypoints` (The *Vagabond* begins its route to NavPoint Alpha).


* **Trigger 2: Ambient Background Traffic**
* **Condition:** `Mission Start` or `Time Elapsed` (0 minutes).
* **Action:** Spawn 2-3 large civilian tankers moving slowly on the edges of the map (15+ miles away) and a civilian airliner flying high above, maintaining a constant, distant radar distraction.


* **Trigger 3: The Local Fleet (Neutrals)**
* **Condition:** `Unit Enters Area` (*Vagabond* reaches the midway point of the transit corridor).
* **Action:** Spawn a large group (8-12) of small surface vessels ahead of the convoy.
* **Action:** Set `Alliance = Neutral` for all spawned skiffs.


* **Trigger 4: The Pirate Swarm**
* **Condition:** `Distance to Unit` (*Vagabond* closes within 4 miles of the neutral cluster).
* **Action:** `Change Alliance` (Four specific skiffs instantly switch to `Hostile`).
* **Action:** `Popup Message` (*"Warning: Multiple high-speed contacts breaking formation! Weapons free on hostile skiffs!"*).


* **Trigger 5: The Twist (Military Escalation)**
* **Condition:** `Unit Destroyed` (All 4 pirate skiffs sunk) OR `Unit Enters Area` (Convoy is 5 miles from the exit zone).
* **Action:** Spawn a modern Missile Boat or Attack Helicopter on the edge of radar range, moving aggressively toward the player.
* **Action:** `MissionWarningMessage` (Custom UI Popup: *"WARNING: Military-grade targeting radar detected. That is not a pirate vessel. We are outgunned, pop smoke and break contact!"*).


* **Trigger 6: Resolution**
* **Defeat:** `Unit Destroyed` (MV *Vagabond* or the Player's Task Force is sunk).
* **Victory:** `Unit Enters Area` (Both the *Vagabond* and the Player's Task Force reach the exit zone at `NavPoint Alpha`).


