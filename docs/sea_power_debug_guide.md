# Sea Power: Campaign & Mission Debug Guide

In *Sea Power: Naval Combat in the Missile Age*, the developers have provided a very robust developer debug tool to help with testing, experimenting, and skipping ahead. It is an incredibly powerful asset when designing custom missions or testing campaigns. 

Here is how you can access and use the debug tools to test your campaign missions easily:

## 1. Opening the Debug Panel
To open the Debug Panel while in a mission, simply press **`F10`**. 

This panel will open up an overlay giving you god-like control over almost every aspect of the ongoing scenario. Since this is the exact same tool the developers use, the UI might feel a bit cluttered or intimidating at first, but it is exactly what you need.

## 2. Useful Testing Features in the F10 Menu
Once the panel is open, you can manipulate the battlefield to quickly verify your mission triggers and test the pacing without needing to play the scenario perfectly for two hours:

*   **Instantly Destroying Units (Auto-kill):** If you want to quickly test victory conditions or just clear out an enemy group, you can instantly destroy a unit. Select the target, go to the **General** tab of the F10 menu, and click **Arm > Kill**. 
*   **Teleporting / Moving Units:** If you need to test an engagement without waiting for ships to cross the ocean, you can move units rapidly. Open the pop-out side panel for moving units, and use your `Shift` and `Control` keys to modify the step distance. You can increase the step size up to 100 nautical miles per click, allowing you to effectively "teleport" units exactly where they need to be. Alternatively, you can use the spawn menu to "replace existing" at any arbitrary position.
*   **Inspecting the Damage Model:** If your custom mission feels too hard (or too easy), the debug tool lets you look "under the hood" at the damage model. You can pause the game, open the tool, and see exactly what internal systems have been disabled or why a ship hasn't sunk yet.
*   **Checking Surviving Units:** If your mission crashes or unexpectedly finishes, opening the debug tool lets you see exactly what AI units were left on the map and where they were pathing. 

## 3. Other Debug & Testing Hotkeys
Aside from the main F10 panel, there are a few standalone keybindings hardcoded into the debug features that might help you test mechanics:

*   **`Alpha 2`** (the 2 key on the number row): [Debug] Forces all ships to launch aircraft.
*   **`LeftShift + Backspace`:** [Debug] Reload Current Object (great if an asset glitches while testing).
*   **`Home / End`:** [Debug] Sub Ballast Up / Down.
*   **`Up / Down Arrow`:** [Debug] Sub Pitch Up / Down (while testing sub pathfinding/behavior).
*   **`R` / `L`:** [Debug] Reload Animations / Change Level of Detail (LOD). 

---
**💡 Quick tip for scenario creation:** Use the debug tool to reveal all enemy units (lifting the "fog of war") while running the scenario on maximum time compression. This will allow you to watch the AI navigate your waypoints and verify that your custom task forces operate exactly as you intended before you test the mission in a standard, restricted-view playthrough!
