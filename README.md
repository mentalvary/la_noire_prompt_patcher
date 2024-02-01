# L.A. Noire prompt patcher

Change the L.A. Noire Truth/Doubt/Lie prompts.

## Usage

1. Download latest `la_noire_prompt_patcher.exe` from [releases page](https://github.com/mentalvary/la_noire_prompt_patcher/releases)
2. Copy the exe to the `final\pc` folder of your L.A. Noire game installation
    * For example on Steam: `C:\Program Files\Steam\steamapps\common\L.A.Noire\final\pc`
3. Double-click the exe to run it.
4. A console window will pop up and ask you for text to replace the Truth/Doubt/Lie prompts. You can use any ASCII text, but no Unicode (non-english characters, emojis, etc.).
    * Example output:
    
        ```shell
        Type a new text for each of the following:
        Truth -> Good cop
        Doubt -> Bad cop
        Lie -> Accuse
        ```
5. After entering all the new prompts, the patcher will finish.
6. Start the game.

## In case of problems

To reset the patch, find the automatically created backup `out.wad.pc.bak` in the `final\pc` folder and rename it back to `out.wad.pc` (you'll have to delete the existing `out.wad.pc` first).
