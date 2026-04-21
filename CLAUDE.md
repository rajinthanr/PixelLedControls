# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nediyakadu Youngsters Sports Club** — LED animation system for a kovil event.

The physical installation is an **octagonal building (~10 ft tall, 30 ft wide)** with pixel LED strips hanging on **7 of the 8 sides** (front side open). Each side has **16 hanging strips × 50 LEDs = 800 LEDs**. Total: **7 × 800 = 5,600 LEDs**. Club colours are **white and green**.

Python scripts generate binary `.tol` animation files that are loaded into a **T-8000 WS2811 controller** via **LEDEdit 2014** (Windows software). The LED grid is modelled as **50 rows × 112 columns** (HEIGHT × WIDTH), where each column group of 16 represents one building side.

## Running a Pattern

Each pattern is a standalone Python script in `Tol creator/`. Run directly — VS Code Code Runner (play button) works fine:

```bash
cd "Tol creator"
python3 rainy.py    # or any other pattern script
```

- Running a script opens a **preview-only** GUI — no `.tol` file is written during playback.
- To save: press **S** or click the **"Save .tol"** button in the GUI bar. The GUI closes, then the script re-runs automatically in headless mode and writes the file to `Tol files/<scriptname>.tol`.
- Stop without saving: press **q** or **Esc**, or click the window's close **(X)** button.
- Window size is saved to `Tol creator/.window_config.json` on close and restored on next run (default 1400 × 640).

## Dependencies

```
opencv-python   (cv2)
numpy
```

Install with `pip3 install opencv-python --break-system-packages`. The `keyboard` library was removed — key detection is done through the OpenCV window instead.

Qt font warnings (`QFontDatabase: Cannot find font directory`) are fixed by copying DejaVu fonts into `~/.local/lib/python3.12/site-packages/cv2/qt/fonts/`.

## Architecture

### `functions.py` — shared state, utilities, and visualiser

All pattern scripts do `from functions import *`. **Importing this module is also initialisation** — it immediately:

1. Derives `OUTPUT_FILE` from `sys.argv[0]`: `../Tol files/<scriptname>.tol`
2. Detects `--headless` flag in `sys.argv` (set `_HEADLESS = True`)
3. **GUI mode**: opens the OpenCV preview window, registers mouse callback, restores window size
4. **Headless mode**: writes the 14-byte `.tol` header and 30 lead-in black frames directly to file; no window opened
5. Registers an `atexit` handler that spawns the headless re-run when `_pending_save[0]` is set

#### Grid constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `HEIGHT` | 50 | LEDs per strip (rows) |
| `SIDES` | 7 | Building sides with lights |
| `STRIPS_PER_SIDE` | 16 | Strips per side (columns per panel) |
| `WIDTH` | 112 | `SIDES × STRIPS_PER_SIDE` (total columns) |
| `FPS` | 30 | Target frame rate |
| `DURATION` | 30 | Seconds of animation |
| `FRAME_COUNT` | 960 | `FPS × DURATION + 60` (includes 30 lead + 30 tail black frames) |

#### Key functions

- `save_frame()` — **headless mode**: appends `byte_array` to the `.tol` file as raw RGB bytes. **GUI mode**: no-op (preview only).
- `display_frame()` — **GUI mode**: renders the 7-panel visualiser, handles key/button/close detection, saves window size. **Headless mode**: prints progress only, no display.
- `black_frame()` — resets `byte_array` to all zeros and saves window config.
- `fade_pixels(byte_array, fade_value)` — subtracts `fade_value` from every RGB channel (floor 0). Used for motion trails.
- `hsv_to_rgb(h, s, v)` — HSV→RGB; `h` is in `[0.0, 1.0]`.

#### Mutable shared state (list wrappers — updated in-place so `from … import *` sees changes)

- `escape = [False]` — set `[True]` by `display_frame()` on Esc/q/close or when Save is triggered. Pattern loops check `escape[0]`.
- `_pending_save = [False]` — set `[True]` when Save button/key is used. The `atexit` handler checks this and spawns the headless re-run.
- `_disp_count = [0]` — frame counter inside `display_frame()`.

#### GUI details (`display_frame`)

- Renders 7 side panels side-by-side, separated by dark dividers.
- Each panel labelled "Side 1"–"Side 7" in green (club colour) above the panel.
- Dot size: radius 3 px (diameter 6 px), cell pitch 15 px — gap between dots = 9 px = 1.5× dot diameter, mimicking physical LED spacing.
- Window flags: `WINDOW_GUI_NORMAL | WINDOW_FREERATIO` — no Qt toolbar/statusbar, image stretches to fill the window.
- Default window size: 1400 × 640. Last-used size restored from `.window_config.json`.
- **Button bar** (40 px below panels): frame counter on the left, blue "Save .tol [S]" button on the right. Turns green "Generating..." when triggered.

#### Save flow

1. User presses **S** or clicks the button → `_pending_save[0] = True`, `escape[0] = True`
2. Animation loop exits, script runs its cleanup (`black_frame()`, tail `save_frame()` calls, `cv2.destroyAllWindows()`)
3. `atexit` fires → spawns `python3 <script>.py --headless`
4. Headless run regenerates every frame from scratch and writes the `.tol` file
5. Terminal prints `✅ Saved → Tol files/<name>.tol`

### Pattern loop structure

Every particle-based pattern uses this busy-wait timing pattern:

```python
SPEED = 40    # physics interval — lower = faster
FADE  = 15    # brightness cut per frame

while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < SPEED:          # throttle: only run physics every SPEED ticks
        if count - pre_time > (1000 / 30):  # emit a frame at ~30 fps
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
```

`SPEED` and `FADE` are the primary tuning knobs — expose them as named constants at the top of each script.

`story.py` and `kovil_glow.py` are exceptions: they use plain nested `for` loops (no busy-wait) since each frame is deterministic, not particle-based.

### `.tol` binary format

| Bytes | Content |
|-------|---------|
| 0 | `0x00` marker |
| 1–3 | Frame count, big-endian 3 bytes |
| 4–5 | HEIGHT, big-endian 2 bytes |
| 6–7 | WIDTH, big-endian 2 bytes |
| 8–13 | `0x00 × 6` padding |
| 14+ | Frame data — `HEIGHT × WIDTH × 3` bytes per frame, row-major, raw RGB |

30 black frames prepended + 30 appended (fade-in/out on controller). The tail frames should be a gradual fade to black (not an instant cut) to avoid a brightness flash on the hardware when the animation loops.

### Hardware context

- Controller: T-8000 WS2811, 8 ports. Only 7 ports used (front side open).
- LEDEdit 2014 (Windows) loads `.tol` files. Project files (`.pxb`, `.cxb`, `.gmm`, `.Lxb`) in `Exported/` are LEDEdit exports — not hand-edited.
- `Exported/Led1_ReadMe.txt` documents the port layout (800 LEDs per port).

## Pattern Scripts

| Script | Effect | Key parameters |
|--------|--------|---------------|
| `hor_lines.py` | Green→white horizontal lines sweeping right | `SPEED`, `FADE`, `PARTICLE_COUNT` |
| `rainy.py` | Green/white rainfall — even panels fall down, odd panels fall up | `PARTICLE_COUNT`, fade = 25 |
| `confetti.py` | Random green sparkle scatter | `PARTICLE_COUNT`, fade = 0.7 |
| `falling_dots.py` | Rainbow columns falling downward | `PARTICLE_COUNT`, fade = 7 |
| `tetris.py` | 4×4 green/white/gold blocks falling and stacking per grid column | `MAX_ACTIVE` |
| `story.py` | Scripted white/green panel wipe — 7 panels, alternating directions | Hard-coded colour sequence |
| `kovil_glow.py` | Warm white & forest green panels with gold cross-fade transitions | `BEAT_PERIOD`, `PANEL_DELAY` |
| `heartbeat.py` | Crimson→amber pulse wave travelling across 7 panels | `BEAT_PERIOD`, `PANEL_DELAY`, `MIN_BRIGHT` |

## Adding a New Pattern

1. Create `Tol creator/mypattern.py`
2. `from functions import *` — handles all init, window setup, and headless detection
3. Define `SPEED` and `FADE` constants at the top
4. Implement the standard loop structure shown above
5. End with a gradual fade-to-black over the tail frames:
   ```python
   import copy as _copy
   _last = _copy.deepcopy(byte_array)
   for _step in range(30):
       _t = 1.0 - (_step + 1) / 30
       for _y in range(HEIGHT):
           for _x in range(WIDTH):
               byte_array[_y][_x] = [int(_last[_y][_x][_c] * _t) for _c in range(3)]
       save_frame()
   black_frame()
   cv2.destroyAllWindows()
   print("✅ Done")
   ```
6. Run it → GUI opens for preview. Press **S** to save `Tol files/mypattern.tol`.

**Do not** use the `keyboard` library — it requires root on Linux. Key detection is already handled inside `display_frame()` via `cv2.waitKey`.
