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
python3 hor_lines.py    # or rainy.py, confetti.py, tetris.py, falling_dots.py, story.py
```

- The `.tol` file is written directly to `Tol files/<scriptname>.tol` (e.g. `hor_lines.py` → `Tol files/hor_lines.tol`).
- An OpenCV preview window opens immediately (black, full-size) before the first frame renders.
- Stop early: press **q** or **Esc** in the preview window, or click the window's **close (X) button**.
- Window size is saved to `Tol creator/.window_config.json` on close and restored on next run.

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
2. Writes the 14-byte `.tol` header to that file
3. Writes 30 leading black frames
4. Opens the OpenCV preview window (restoring last-used size from `.window_config.json`)
5. Initialises all global mutable state

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

- `save_frame()` — appends `byte_array` to the `.tol` file as raw RGB bytes, each channel clamped to 0–255.
- `display_frame()` — renders the 7-panel visualiser, handles key/close detection, saves window size, prints progress once per second.
- `black_frame()` — resets `byte_array` to all zeros and saves window config.
- `fade_pixels(byte_array, fade_value)` — subtracts `fade_value` from every RGB channel (floor 0). Used for motion trails.
- `hsv_to_rgb(h, s, v)` — HSV→RGB; `h` is in `[0.0, 1.0]`.

#### Mutable shared state (list wrappers — updated in-place so `from … import *` sees changes)

- `escape = [False]` — set to `[True]` by `display_frame()` when Esc/q pressed or window closed. Pattern loops check `escape[0]`.
- `_disp_count = [0]` — frame counter inside `display_frame()`, used for progress printing every `FPS` frames.

#### Visualiser details (`display_frame`)

- Renders 7 side panels side-by-side, separated by dark dividers.
- Each panel labelled "Side 1"–"Side 7" in green (club colour) above the panel.
- Dot size: radius 3 px (diameter 6 px), cell pitch 15 px — gap between dots = 9 px = 1.5× dot diameter, mimicking physical LED spacing.
- Window flags: `WINDOW_GUI_NORMAL | WINDOW_FREERATIO` — no Qt toolbar/statusbar, image stretches to fill the window with no letterbox borders.
- Default window size: 1400 × 600 (wide landscape for 7 panels).

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

`story.py` is the exception: it uses plain nested `for` loops (no busy-wait) since each frame is deterministic, not particle-based.

### `.tol` binary format

| Bytes | Content |
|-------|---------|
| 0 | `0x00` marker |
| 1–3 | Frame count, big-endian 3 bytes |
| 4–5 | HEIGHT, big-endian 2 bytes |
| 6–7 | WIDTH, big-endian 2 bytes |
| 8–13 | `0x00 × 6` padding |
| 14+ | Frame data — `HEIGHT × WIDTH × 3` bytes per frame, row-major, raw RGB |

30 black frames prepended + 30 appended (fade-in/out on controller).

### Hardware context

- Controller: T-8000 WS2811, 8 ports. Only 7 ports used (front side open).
- LEDEdit 2014 (Windows) loads `.tol` files. Project files (`.pxb`, `.cxb`, `.gmm`, `.Lxb`) in `Exported/` are LEDEdit exports — not hand-edited.
- `Exported/Led1_ReadMe.txt` documents the port layout (800 LEDs per port).

## Pattern Scripts

| Script | Effect | Key parameters |
|--------|--------|---------------|
| `hor_lines.py` | Green→white horizontal lines sweeping right | `SPEED`, `FADE`, `PARTICLE_COUNT` |
| `rainy.py` | Green/white rainfall dripping down | `PARTICLE_COUNT`, fade = 25 |
| `confetti.py` | Random green sparkle scatter | `PARTICLE_COUNT`, fade = 0.7 |
| `falling_dots.py` | Rainbow columns falling downward | `PARTICLE_COUNT`, fade = 7 |
| `tetris.py` | Coloured Tetris blocks falling and stacking | `DROP_COUNT` |
| `story.py` | Scripted green/white/yellow panel wipe sequence | Hard-coded colour sequence |

## Adding a New Pattern

1. Create `Tol creator/mypattern.py`
2. `from functions import *` — handles all init, file writing, and window setup
3. Define `SPEED` and `FADE` constants at the top
4. Implement the standard loop structure shown above
5. End with:
   ```python
   black_frame()
   for i in range(30):
       save_frame()
   cv2.destroyAllWindows()
   print("✅ Done")
   ```
6. Run it — output goes directly to `Tol files/mypattern.tol`

**Do not** use the `keyboard` library — it requires root on Linux. Key detection is already handled inside `display_frame()` via `cv2.waitKey`.
