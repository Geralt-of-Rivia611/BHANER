# bhaner Theme & Typography Customization Guide

`bhaner` lets operators project bold, auto-scaling live text overlays while keeping total control over typography, contrast outlines, colors, and punch effects without touching code.

---

## 1. Presets Overview

The controller provides 6 instant-access presets accessible via buttons or keyboard shortcuts:

* **P1 (Flame / Orange Stage - F1):** Optimized for warm/orange backdrops. High-lumen white text with dark brown perimeter depth shadow.
* **P2 (Ocean Punch - F2):** Designed to punch through saturated cyan/teal visual swirls using high-visibility brand orange.
* **P3 (Core Flare Shield - F3):** Includes a soft, semi-transparent radial blackout vignette to keep text readable directly over blinding white center-screen flares.
* **P4 (Cyber Cyan - F4):** Clean, modern aesthetic with cyan glow accents.
* **P5 (Minimal White - F5):** Raw, crisp high-lumen white with deep drop shadows.
* **P6 (Custom Slots - F6):** A dedicated user bank with **3 persistent slots (Slot A, Slot B, Slot C)** that remember your custom theme assignments across reboots.

---

## 2. Setting Up Custom Slots (Slot A / B / C)

You do not need to re-import or open files every time you run the app:

1. Click **Open Folder** in the controller toolbar to open the `themes/` directory.
2. Place your custom `.json` themes into `themes/` (and any custom `.ttf`/`.otf` font files into `themes/fonts/`).
3. Click **Reload** in the controller to scan for the new files.
4. Select a slot radio button (**Slot A**, **Slot B**, or **Slot C**).
5. Choose your desired theme from the **Assigned Theme** dropdown.
6. Click **Assign to Slot**.

Your choice is permanently saved in `bhaner_config.json`. You can now toggle between your custom looks during a live show simply by clicking **Slot A**, **Slot B**, or **Slot C**, or pressing **F6**.

---

## 3. Setting a Startup Default

To have `bhaner` automatically load a specific preset or custom slot every time it boots:
1. Select the preset (P1–P5) or your desired Custom Slot (Slot A/B/C).
2. Click **Set as Default**.
3. The status label will update (e.g., `[Default]: Custom (SLOT_A: festival_gold)`), and the app will boot into that style automatically.

---

## 4. Creating a Custom Theme JSON

Inside the `themes/` folder, you will find `custom_template.json`. To create a new theme:
1. Copy `custom_template.json` and rename it (e.g., `festival_neon.json`).
2. Open the file with **Notepad** or any text editor.
3. Edit the properties, save, and click **Reload** in the controller.

### Full JSON Schema

```json
{
  "id": "festival_neon",
  "name": "Festival Neon Gold",
  
  "font_family": "'Impact', sans-serif",
  "google_font_url": "",
  "font_file": "AkiraExpanded.otf",
  
  "text_transform": "uppercase",
  "letter_spacing": "2px",
  
  "text_color": "#FFD700",
  "text_shadow": "-4px -4px 0 #000, 4px -4px 0 #000, -4px 4px 0 #000, 4px 4px 0 #000, 0 0 35px #FFA500",
  
  "container_background": "transparent",
  
  "impact_zoom": {
    "scale": 1.2,
    "text_color": "#FFFFFF",
    "text_shadow": "0 0 40px #FFF, 0 0 70px #FFD700"
  }
}