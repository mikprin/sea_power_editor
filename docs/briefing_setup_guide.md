# Briefing Setup Guide

Learn how to properly add a briefing to your Scenario in the Mission Editor.

## Adding Briefing Text

1. Type out your briefing in a separate text editor (Notepad, etc.). This allows you to easily modify and preview the text before adding it to the game.

2. Navigate to:
   ```
   SteamLibrary/Steamapps/common/Sea Power/Sea Power_Data/Streaming Assets/user/missions/
   ```
   Create a new folder named `Mission_Example_Briefing` (replace "Mission_Example" with your mission name). Keep the `_briefing` suffix. The `.ini` file for your mission stays outside this folder.

3. Open the Mission Editor and go to the **Mission Briefing** tab. Click **Pick Assets Folder** and select the `Mission_Example_Briefing` folder you just created. Enable the **Expert Mode** checkboxes for both Left and Right Panes.

4. Copy your briefing text into the **Left Pane** with Expert Mode enabled, then click **Update Left Pane**.

5. The text won't display correctly yet—XAML formatting is required.

6. In your text editor, wrap your briefing with `<TextBlock>` tags:
   ```xml
   <TextBlock>
   Your briefing text here
   </TextBlock>
   ```
   
   To insert line breaks, add `<LineBreak/>` at the desired locations:
   ```xml
   <TextBlock>
   First paragraph.
   <LineBreak/>
   Second paragraph.
   </TextBlock>
   ```
   
   **Note:** All lines between `<TextBlock>` and `</TextBlock>` should be indented consistently (like a sandwich).

7. Copy the formatted XAML text back into the **Left Pane**, then click **Update Left Pane** to preview. Adjust line breaks as needed.

8. Save the mission in the Mission Editor.

## Adding Briefing Image

1. Navigate to your `_briefing` folder:
   ```
   SteamLibrary/Steamapps/Common/Sea Power/Sea Power_Data/StreamingAssets/user/missions/Mission_Example_Briefing
   ```

2. Place your briefing image in this folder. Supported formats: `.bmp`, `.png`, `.jpg`. Use an online converter if your image is in a different format.

3. In the Mission Editor's **Right Pane**, add:
   ```xml
   <Image Source="{Binding Assets[FILENAME]}" />
   ```
   
   Replace `FILENAME` with the exact name of your image file. Click **Update Right Pane** to preview.

4. Edit your mission `.ini` file (located in `SteamLibrary/Steamapps/Common/Sea Power/Sea Power_Data/StreamingAssets/user/missions/`). Add the following lines below your scenario description:
   ```ini
   MissionBriefingAssetsDirectory=missions/Mission_Example_Briefing/briefingimage_briefing
   MissionBriefingAssetsSearchPattern=*.png,*.jpg,*.bmp
   MissionBriefingLeftPane=missions/Mission_Example_Briefing/LeftPane_en.xml
   MissionBriefingRightPane=missions/Mission_Example_Briefing/RightPane_en.xml
   ```
   
   Replace `Mission_Example_Briefing` with your folder name and `briefingimage_briefing` with your actual image filename. Save the `.ini` file. If you move the briefing folder later, update these paths.

5. Return to the Mission Editor and click **Update Right Pane**. Your image should now appear. If it doesn't, verify:
   - The XAML code matches your image filename exactly
   - Your image is in a supported format (`.bmp`, `.png`, or `.jpg`)

## Support

For help, check the comments. Thanks to TheHappyYachter from Trassic Games for the code guidance. 