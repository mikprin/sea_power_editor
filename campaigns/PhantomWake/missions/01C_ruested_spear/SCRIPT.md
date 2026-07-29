OPTIONAL MISSION: RUSTY SPEAR

CLIENT: Defecting Naval Officers (Local Regime)
LOCATION: Coastal Archipelago, Shallow Bay
REWARD: +1 Diesel-Electric Submarine (Project 641 "Foxtrot" or Project 877) added to Task Force roster.
I. Mission Briefing

[ATLAS]: "Commander, we have a unique opportunity to expand our capabilities. A faction of defecting officers from a local regime’s navy has reached out to us. They’ve hijacked their own aging diesel-electric submarine, but they are trapped. The local dictator has bottled them up in a shallow bay with a blockade of patrol boats. If we can punch a hole in that blockade and escort them to the deep-water drop-off, they’ve agreed to fly the Phantom Wake flag. We need that boat, Commander."

[ECHO]: BATHYMETRY ANALYSIS COMPLETE. BAY AVERAGE DEPTH: 40 METERS. THE TARGET VESSEL CANNOT DIVE TO A SAFE DEPTH WITHOUT CRASHING INTO THE SEABED. IT WILL BE FORCED TO TRANSIT ON THE SURFACE AT A MAXIMUM SPEED OF 12 KNOTS. TACTICAL ASSESSMENT: IT IS A SITTING DUCK.

[SIREN]: "The local regime is using cheap, fast patrol boats—mostly old P6 and Stenka classes. They don't have heavy anti-ship missiles, but a swarm of them with heavy machine guns and light torpedoes will easily tear that submarine’s pressure hull apart. Draw their fire, Commander."
II. Objectives

    Rendezvous: Break through the initial blockade line and establish physical visual contact with the defecting submarine.

    Escort: Protect the submarine as it navigates the shallow channel to the deep-water drop-off point (NavPoint Zulu).

    Survival: The submarine must not be destroyed.

III. Execution & Scenario Phases

Phase 1: Punching the Hole (The Blockade)

    Setup: The player's Task Force spawns outside the bay. The entrance to the bay is patrolled by a stationary picket line of 3-4 light enemy patrol boats (wp_pt_p6 or wp_pt_stenka).

    Action: The player must aggressively engage and destroy the blockade. Stealth is not an option here; the player needs to make noise to draw attention away from the submarine hiding deeper in the bay.

Phase 2: The Slow Crawl (The Escort)

    Setup: Once the blockade is cleared, the player approaches the submarine.

    Trigger (Unit Enters Area): When the player is within 2 nautical miles, the submarine powers up its diesel engines and begins moving at a painfully slow 10-12 knots along a pre-assigned waypoint path toward the open ocean.

    Action: As soon as the sub starts moving, enemy reinforcements are triggered. 2-3 waves of fast attack crafts spawn from the coastline and rush the convoy.

    Dialogue:

        [ECHO]: MULTIPLE FAST SURFACE CONTACTS INBOUND FROM THE COAST. SPEED: 35 KNOTS. INTERCEPT COURSE CALCULATED. THEY ARE IGNORING OUR FLAGSHIP AND TARGETING THE SUBMARINE.

        [ATLAS]: "Put your ship between them and the sub, Commander! If that pressure hull breaches, we lose our payday!"

Phase 3: The Drop-Off (Escape)

    Setup: The deep-water shelf is marked as a specific zone on the map (NavPoint Zulu).

    Action: The player must fend off the remaining boats until the submarine crosses into the zone.

    Trigger (Unit Enters Area): Once the sub reaches the deep water, it immediately executes a crash dive command, disappearing from the surface and enemy radar.

    Dialogue:

        [SIREN]: "The sub has reached the shelf. They are diving now. Sonar confirms they are passing 150 meters and rigged for silent running. Good job, Commander."

        [ATLAS]: "Contract fulfilled. Let's clean up the remaining trash and get out of here. We have a submarine to inspect."

IV. Mission Editor Logic (Under the Hood)

    Submarine Status: Set the defecting submarine's Alliance to Blue (Player), but ensure OverrideWeaponStatus=Hold so it doesn't waste its own torpedoes. Use a custom waypoint path that strictly follows the deep channel.

    Enemy Targeting: Use AI behavior overrides to ensure the spawned enemy patrol boats prioritize the submarine over the player's heavily armed corvette/destroyer. This forces the player into a protective, intercepting role rather than just kiting the enemy.

    Win Condition: Unit Enters Area (Submarine reaches NavPoint Zulu). Trigger an action that despawns the sub or forces a dive to maximum depth, followed by the Mission Success screen.