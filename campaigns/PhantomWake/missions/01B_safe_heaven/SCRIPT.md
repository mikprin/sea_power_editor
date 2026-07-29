OPTIONAL CONTRACT: SAFE HAVEN

CLIENT: Anonymous Corporate Executive
LOCATION: Coastal Waters, Horn of Africa (Nighttime)
ENVIRONMENT: Pitch black, calm seas.
ASSETS AVAILABLE: Small/Stealth vessels highly recommended.
1. Narrative Briefing

[ATLAS]: "Listen up, Commander. We have a lucrative side-contract. A high-net-worth individual’s luxury yacht, the Stargazer, suffered a 'convenient' total engine failure just inside territorial waters. The local Coast Guard is sweeping the area, and our client would rather not explain to them why he has three briefcases full of unmarked bearer bonds on board. Get in, pick him up, and get out."

[SIREN]: "The local authorities are on high alert. They have heavily armed patrol boats running search patterns with active surface radars and searchlights. If they paint you with their radar, they will intercept. If you shoot them, we become international criminals and lose the payout. Weapons tight, Commander."

[E.C.H.O.]: "RECOMMENDATION: DEACTIVATE ACTIVE SENSORS. RIG FOR SILENT RUNNING. KEEP TELEGRAPH BELOW 1/3 TO REDUCE WAKE AND ACOUSTIC SIGNATURE. RELY ON ESM (ELECTRONIC SUPPORT MEASURES) TO TRACK PATROL EMISSIONS."
2. Mission Flow & Phases

    Phase 1: The Silent Approach
    The player spawns roughly 8 nautical miles from the yacht. The yacht is stationary and emitting a faint distress beacon. The player must turn off their active radar immediately. Navigating by ESM only, they must chart a course that weaves between the patrol routes of 3-4 Coast Guard vessels.

    Phase 2: The Transfer
    Once the player reaches the yacht, they must drop speed to zero (Telegraph = 0) within 0.1 NM of the target. This triggers a ~2-minute timer (check the CLAUDE.md how to make timers) representing the VIP boarding. During this time, one of the Coast Guard patrol boats spawns off its standard route with radar ON and heads near the yacht's position to investigate. The player must hold their nerve and wait for the VIP.

    Phase 3: Slipping Away
    With the VIP secured, the player must exit the hot zone and reach the designated "Extraction NavPoint" at the edge of the map without being detected or returning fire.

3. Under-the-Hood: Editor Logic & Triggers

To build this in the Sea Power .ini files, use the following trigger structure:

    Trigger: Detection Failure (ROE Violation)

        Condition: Distance to Unit (Coast Guard boat gets within 2.5 NM of Player) OR Unit Detected (Player is fully identified by Coast Guard sensors).

        Action: Popup Message ("[ATLAS]: Damn it, they spotted us! Contract aborted, get us out of here!").

        Action: Coast Guard alliance changes to Hostile and they open fire.

        Action: Mission ends in Defeat.

    Trigger: Fire Discipline Failure

        Condition: Weapon Fired (Player fires any gun or missile). Can be just trigger to patrol boats, or any enemy unit dead.

        Action: Mission ends in Defeat (Client refuses to pay for an international incident).

    Trigger: Initiate VIP Transfer

        Condition: Unit Enters Area (Player is within 0.1 NM of the Stargazer yacht) AND Speed < 2 knots.

        Action: Popup Message ("[E.C.H.O.]: VIP SECURED ON DECK. TRANSFER IN PROGRESS. STANDBY FOR 120 SECONDS.").

        Action: Timer Start (120 seconds).

        Action: Assign Waypoint (Forces one Coast Guard boat to move towards the yacht's coordinates to create tension).

    Trigger: Transfer Complete

        Condition: Time Elapsed (~120 seconds after Transfer initiated).

        Action: Popup Message ("[ATLAS]: Package is secure. Start the engines, keep it quiet, and head for the extraction zone.").

        Action: Activate the Extraction NavPoint on the map.

    Trigger: Success

        Condition: Unit Enters Area (Player reaches the Extraction NavPoint) AND Player is not detected.

        Action: Mission ends in Victory.