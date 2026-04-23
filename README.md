# Kovil LED Animations

LED animation system for the **Nediyakadu Youngsters Sports Club** kovil event.

Generates `.tol` binary files loaded into a **T-8000 WS2811 LED controller** via LEDEdit 2014, and optionally `.avi` video previews.

## Physical Setup

- Octagonal building (~10 ft tall, 30 ft wide)
- **7 sides** fitted with LED strips (front side open)
- Each side: **16 strips × 50 LEDs = 800 LEDs**
- Total: **5,600 LEDs**
- Club colours: **white and green**

## Requirements

Python 3 with:

```bash
pip3 install opencv-python --break-system-packages
```

## Quick Start

### Launch the GUI (recommended)

```bash
python3 "Tol creator/master_tol_creator.py"
```

The GUI has two sections:

**Left — Preview Patterns**
Click ▶ next to any pattern to open a live preview window. Click ■ to stop it. Clicking ▶ on a different pattern automatically stops the current one.

**Right — Generate Files**
Tick the patterns you want, then click:
- **Generate .tol** — writes `Tol files/<name>.tol` for each selected pattern
- **Generate .avi** — writes `Avi files/<name>.avi` video previews

### Run a single pattern directly

```bash
cd "Tol creator/patterns"
python3 falling_dots.py
```

| Key | Action |
|-----|--------|
| **S** | Save `.tol` file and close |
| **A** | Save `.avi` file and close |
| **Q** or **Esc** | Quit without saving |
| **(X)** button | Quit without saving |

## Output Files

| Folder | Contents |
|--------|----------|
| `Tol files/` | `.tol` binary animations — load into LEDEdit 2014 |
| `Avi files/` | `.avi` video previews |

Both folders are in `.gitignore` — output files are not committed to the repo.

## Patterns

| Pattern | Description |
|---------|-------------|
| `bouncing_balls` | 16 coloured balls bouncing on a green/white checkerboard |
| `diamonds` | Expanding diamond rings from the grid centre, each ring a random hue |
| `falling_dots` | Dense diagonal dots falling at 45°, each a different random hue |
| `heartbeat` | Pulse waves radiating across all 7 panels |
| `horiz_chase` | Wide colour pillars chasing horizontally across a dark background |
| `panel_blinds` | Venetian-blind shutter effect — slats open and close in alternating directions with random colours |
| `panel_diamonds` | Independent expanding diamond rings on each of the 7 panels |
| `sparkle` | Sparkle effect |
| `story` | Scripted white/green wipe across panels |
| `tri_chase` | Three horizontal strips chasing in opposite directions |
| `water_drops` | Solid-colour panels; a drop expands and changes the panel colour when it finishes |
| `water_drops_dark` | Solid panels with dark expanding ripple rings; panel hues slowly drift independently |

## Loading onto the Controller

1. Copy the generated `.tol` file to a USB drive
2. Open LEDEdit 2014 on Windows
3. Import the `.tol` file and sync to the T-8000 controller

See `Exported/Led1_ReadMe.txt` for the port wiring layout (800 LEDs per port, 7 ports used).

## Project Structure

```
Tol creator/
  functions.py          # shared grid state, renderer, save logic
  master_tol_creator.py # launcher GUI
  patterns/             # all animation scripts
Tol files/              # generated .tol output (gitignored)
Avi files/              # generated .avi output (gitignored)
Exported/               # LEDEdit project files
```
