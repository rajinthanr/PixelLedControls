# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nediyakadu Youngsters Sports Club** — LED animation system for a kovil event.

The physical installation is an **octagonal building (~10 ft tall, 30 ft wide)** with pixel LED strips hanging on **7 of the 8 sides** (front side open). Each side has **16 hanging strips × 50 LEDs = 800 LEDs**. Total: **7 × 800 = 5,600 LEDs**. Club colours are **white and green**.

Python scripts generate binary `.tol` animation files (and optionally `.avi` video previews) that are loaded into a **T-8000 WS2811 controller** via **LEDEdit 2014** (Windows software). The LED grid is modelled as **50 rows × 112 columns** (HEIGHT × WIDTH), where each column group of 16 represents one building side.

## Launcher

**`Tol creator/master_tol_creator.py`** is the main GUI. Run it to preview or batch-generate patterns:

```bash
python3 "Tol creator/master_tol_creator.py"
```

- Left panel: play buttons (▶/■) to preview individual patterns. Clicking ▶ on a new pattern automatically stops any currently playing one.
- Right panel: checkboxes to select patterns, then **Generate .tol** or **Generate .avi** to batch-produce output files.

## Running a Single Pattern

Pattern scripts live in `Tol creator/patterns/`. Run directly:

```bash
cd "Tol creator/patterns"
python3 falling_dots.py    # or any other pattern script
```

- Running opens a **preview-only** GUI — no file is written during playback.
- To save `.tol`: press **S** or click **"Save .tol"** → window closes, script re-runs headless and writes `Tol files/<name>.tol`.
- To save `.avi`: press **A** or click **"Save .avi"** → writes `Avi files/<name>.avi`.
- Stop without saving: press **q** or **Esc**, or click **(X)**.
- Window size is saved to `Tol creator/.window_config.json` on close and restored on next run (default 1400 × 640).

## Dependencies

```
opencv-python   (cv2)
numpy
```

Install: `pip3 install opencv-python --break-system-packages`

Qt font warnings (`QFontDatabase: Cannot find font directory`) are fixed by copying DejaVu fonts into `~/.local/lib/python3.12/site-packages/cv2/qt/fonts/`.

## Architecture

### `Tol creator/functions.py` — shared state, utilities, and visualiser

All pattern scripts do:
```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
```

**Importing this module is also initialisation** — it immediately:

1. Derives `OUTPUT_FILE` / `AVI_FILE` from `sys.argv[0]`
2. Detects `--headless` and `--avi` flags in `sys.argv`
3. **GUI mode**: opens the OpenCV preview window, registers mouse callback, restores window size
4. **Headless/AVI mode**: writes the `.tol` header + lead-in frames, or opens the AVI writer; no window opened
5. Registers an `atexit` handler that spawns the headless re-run when a save is triggered

#### Grid constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `HEIGHT` | 50 | LEDs per strip (rows) |
| `SIDES` | 7 | Building sides with lights |
| `STRIPS_PER_SIDE` | 16 | Strips per side (columns per panel) |
| `WIDTH` | 112 | `SIDES × STRIPS_PER_SIDE` (total columns) |
| `FPS` | 30 | Target frame rate |
| `DURATION` | 60 | Seconds of animation |
| `LEAD_FRAMES` | 0 | Black lead-in frames |
| `TAIL_FRAMES` | 30 | Black tail frames |
| `FRAME_COUNT` | 1830 | `FPS × DURATION + LEAD_FRAMES + TAIL_FRAMES` |

#### Key functions

- `save_frame()` — **headless**: appends `byte_array` to `.tol` as raw RGB bytes. **GUI**: no-op.
- `display_frame()` — **GUI**: renders the 7-panel visualiser, handles key/button/close. **Headless**: prints progress only.
- `black_frame()` — resets `byte_array` to all zeros and saves window config.
- `fade_pixels(byte_array, fade_value)` — subtracts `fade_value` from every RGB channel (floor 0). Used for motion trails.
- `fade_out_and_close()` — standard ending: fades `byte_array` to black over 30 frames, saves tail, destroys window. **Call this at the end of every pattern.**
- `hsv_to_rgb(h, s, v)` — HSV→RGB; `h` in `[0.0, 1.0]`.

#### Mutable shared state (list wrappers)

- `escape = [False]` — set `True` by `display_frame()` on quit or Save. Pattern loops check `escape[0]`.
- `_pending_save = [False]` — set `True` when Save .tol is triggered.
- `_pending_avi = [False]` — set `True` when Save .avi is triggered.

#### GUI details (`display_frame`)

- Renders 7 side panels side-by-side with dark dividers.
- Each panel labelled "Side 1"–"Side 7" in green above the panel.
- Dot size: radius 3 px, cell pitch 15 px — mimics physical LED spacing.
- **Button bar**: frame counter left, "Save .tol [S]" and "Save .avi [A]" buttons right.

### Pattern loop structure

**Particle-based patterns** use a busy-wait timing loop:

```python
SPEED = 40    # physics interval — lower = faster
FADE  = 15    # brightness cut per frame

while True and current_frame < FRAME_COUNT - TAIL_FRAMES:
    count += 1
    if count - pTloop < SPEED:
        if count - pre_time > (1000 / 30):
            current_frame += 1
            save_frame()
            display_frame()
            pre_time = count
            fade_pixels(byte_array, FADE)
        continue
    pTloop = count
    # --- physics: mutate byte_array here ---
    if escape[0]:
        break

fade_out_and_close()
```

**Deterministic patterns** (`story.py`, `panel_blinds.py`) use plain nested `for` loops with a `save_display()` helper that increments `current_frame` and calls `save_frame()` + `display_frame()` together.

### `.tol` binary format

| Bytes | Content |
|-------|---------|
| 0 | `0x00` marker |
| 1–3 | Frame count, big-endian 3 bytes |
| 4–5 | HEIGHT, big-endian 2 bytes |
| 6–7 | WIDTH, big-endian 2 bytes |
| 8–13 | `0x00 × 6` padding |
| 14+ | Frame data — `HEIGHT × WIDTH × 3` bytes per frame, row-major, raw RGB |

### Hardware context

- Controller: T-8000 WS2811, 8 ports. Only 7 used (front side open).
- LEDEdit 2014 (Windows) loads `.tol` files. Project files in `Exported/` are LEDEdit exports — not hand-edited.
- `Exported/Led1_ReadMe.txt` documents the port layout (800 LEDs per port).

## Pattern Scripts

All scripts are in `Tol creator/patterns/`.

| Script | Effect | Key parameters |
|--------|--------|----------------|
| `bouncing_balls.py` | 16 hue-shifting balls bouncing on a green/white 4×4 checkerboard | `BALL_RADIUS`, `N_BALLS`, `HUE_DRIFT` |
| `diamonds.py` | Expanding diamond rings from grid centre, each ring a random hue | `THICKNESS`, `GAP`, `N_HUES` |
| `falling_dots.py` | Dense 45° diagonal falling dots, each with a fixed random hue | `SPEED`, `FADE`, `PARTICLE_COUNT` |
| `heartbeat.py` | Multi-colour pulse waves radiating across panels | `BEAT_PERIOD`, `PANEL_DELAY` |
| `horiz_chase.py` | Wide hue-gradient pillars chasing horizontally, near-black background | `BAND_WIDTH`, `NUM_BANDS`, `HUE_DRIFT` |
| `panel_blinds.py` | Venetian-blind shutter close/open, alternating slat directions, random hues each cycle | `SLAT_COUNT`, `FRAMES_PER_COL`, `HOLD_FRAMES` |
| `panel_diamonds.py` | Independent expanding diamond rings per panel, staggered phases, random hues | `THICKNESS`, `GAP`, `N_HUES` |
| `sparkle.py` | Sparkle effect | — |
| `story.py` | Scripted white/green panel wipe — 7 panels, alternating directions | Hard-coded colour sequence |
| `tri_chase.py` | Three horizontal strips (top/middle/bottom) chasing in alternating directions | `BAND_WIDTH`, `NUM_BANDS` |
| `water_drops.py` | Per-panel solid hue background; one drop per panel grows and changes the hue on finish, staggered starts | `DROP_MAX_R`, `RING_WIDTH`, `GROW_SPEED` |
| `water_drops_dark.py` | Solid-hue panels with expanding dark ripple rings; each panel's hue drifts at its own rate | `MAX_DROPS`, `RING_WIDTH`, `panel_drift` |

## Adding a New Pattern

1. Create `Tol creator/patterns/mypattern.py`
2. Add the path insert and import:
   ```python
   import sys, os
   sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
   from functions import *
   ```
3. Define `SPEED` and `FADE` constants at the top
4. Implement the standard busy-wait loop (see above), guarded by `current_frame < FRAME_COUNT - TAIL_FRAMES`
5. End with `fade_out_and_close()`
6. Add an entry to the `PATTERNS` list in `Tol creator/master_tol_creator.py`
7. Run it → GUI opens for preview. Press **S** to save `.tol`, **A** for `.avi`.

**Do not** use the `keyboard` library — it requires root on Linux. Key detection is handled inside `display_frame()` via `cv2.waitKey`.
