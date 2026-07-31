OPTIONAL CONTRACT: SAFE HAVEN

CLIENT: Anonymous Corporate Executive
LOCATION: Coastal Waters, Mascarene Basin west of Mauritius (Nighttime)
ENVIRONMENT: Pitch black, calm seas.
ASSETS AVAILABLE: Small/Stealth vessels highly recommended.

1. Narrative Briefing

[ATLAS]: "Listen up, Commander. We have a lucrative side-contract. A high-net-worth individual chartered a boat out of Port Louis and suffered a 'convenient' total engine failure just inside territorial waters. The local Coast Guard is sweeping the area, and our client would rather not explain to them why he has three briefcases full of unmarked bearer bonds on board. Get in, pick him up, and get out. One complication - he did not charter a yacht. He chartered the scruffiest hull money could rent, a converted stern trawler called the Stargazer, precisely so nobody would look twice at her. There are working fishing boats all over that water tonight."

[SIREN]: "The local authorities are on high alert. They have heavily armed patrol boats running search patterns with active surface radars and searchlights. If they paint you with their radar, they will intercept. If you shoot them, we become international criminals and lose the payout. Weapons tight, Commander."

[E.C.H.O.]: "RECOMMENDATION: DEACTIVATE ACTIVE SENSORS. RIG FOR SILENT RUNNING. RELY ON ESM (ELECTRONIC SUPPORT MEASURES) TO TRACK PATROL EMISSIONS."

2. Mission Flow & Phases

    Phase 1: The Silent Approach
    The player spawns roughly 17 NM north-west of the search box. The trick in this mission is EMCON. Navigating by ESM only, they must weave through the marked radar barrier of the Coast Guard patrols.

    Phase 2: Identification
    The client's boat is not marked on the plot - only a 3 NM "last reported position" box is, and the water is full of civilian fishing traffic that looks the same. When the player gets a sensor contact on the trawler, her transponder resolves and an INTEL entry confirms that this hull is the VIP, plus the order to close on her.

    Phase 3: The Pickup - no timer
    The player closes to within 0.1 NM of the Stargazer. That is the whole task: the client and his cases come across the instant the ship is inside the transfer radius. There is no boarding countdown and no requirement to hold station. At that moment the Coast Guard alert element (two Osa I) spawns south-west with radar radiating, and a second barrier of lit sectors lights up across the southern withdrawal lane.

    Phase 4: Slipping Away
    With the VIP secured, the player must exit the hot zone and reach the "Extraction NavPoint" (NavPoint Sanctuary) without being painted or returning fire.

3. Under-the-Hood: Editor Logic & Triggers

Implemented in `01B_safe_heaven.ini` as 11 triggers:

    Trigger1  Start - briefing popup, intel, forecast.
    Trigger2  Entering the patrol belt - ESM warning popup.
    Trigger3  Painted by patrol radar (barrier 1, six ORed circles) - defeat.
    Trigger4  Caught by the alert sweep (barrier 2, four ORed circles) - defeat.
              Disabled=True, armed by Trigger11.
    Trigger5  Any Coast Guard vessel destroyed - defeat (fire discipline; there is
              no "weapon fired" condition in the engine).
    Trigger6  Client vessel destroyed - defeat.
    Trigger7  VIP CONFIRMED. Condition_Identified = UnitDetected on NeutralVessel1
              with _Taskforce=Neutral (same shape as 01A Trigger7), ORed with
              Condition_NearBox, a 3 NM circle on the trawler as a backstop in case
              the sensor condition does not resolve. Fires Taskforce1ContactMessage
              and ContactIntel: "this trawler is our VIP, close to 0.1 NM".
    Trigger8  PICKUP. Condition_Alongside = 0.1 NM circle on the trawler, drawn to
              the player (AreaDisplaySide=Blue, TransferAreaLabel). Fires the
              package-secure popup and AlertIntel, spawns the alert element
              (Action_SetEnabledStatus on Taskforce2Vessel3/4), enables Trigger9,
              sets 01BVIPAboard.
    Trigger9  Extraction circle reached - victory. Disabled=True until Trigger8.
    Trigger10 Task force wiped out - defeat.
    Trigger11 Same 0.1 NM condition as Trigger8, exists only to arm Trigger4
              (a comma list on Action_EnableTriggers is unverified in vanilla).

Removed on purpose:

    - The 120 s boarding timer. The engine has no relative timer (docs/CLAUDE.md
      section 2). Two stopwatch builds were tried and both are gone: an airliner,
      whose arrival area never resolved because aircraft do not satisfy a surface
      area check, and the alert element itself, which worked but read as an
      arbitrary wait from the bridge.
    - The "hold station / speed under 2 kt" requirement. There is no speed
      condition in the engine, so it had to be faked with a second area check, and
      it only existed to serve the timer.
    - The dawn deadline (hard mission end at 7200 s).
