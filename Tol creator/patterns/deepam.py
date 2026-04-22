import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
import math

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED       = 18    # physics interval — lower = faster, more organic flicker
FADE        = 14    # afterglow decay — lower = longer warm glow above receding flame
BASE_H      = 28    # centre flame height in pixels (out of 50)
WAVE_AMP    = 10    # how much each column's height varies in the cross-building wave
FLICKER_AMP = 4     # per-column random flicker (pixels)
SPARK_PROB  = 0.25  # probability a column throws a spark above the tip each step
# ─────────────────────────────────────────────────────────────────────────────
# Palette: Kovil Deepam — Amber base → Gold mid → Warm White tip + spark

# Per-column phase offsets create an organic, non-uniform flame wall
col_phase = [random.uniform(0, 2 * math.pi) for _ in range(WIDTH)]
time_t    = 0.0

while True and current_frame < FRAME_COUNT - 30:
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

    time_t += 0.04

    # Slow breath shared across all sides (makes the whole building inhale/exhale)
    breath = math.sin(time_t * 0.45) * 7

    for x in range(WIDTH):
        # Each column gets its own wave offset + random flicker
        wave    = math.sin(time_t * 1.3 + col_phase[x]) * WAVE_AMP
        flicker = random.uniform(-FLICKER_AMP, FLICKER_AMP)
        h = int(BASE_H + breath + wave + flicker)
        h = max(6, min(HEIGHT - 3, h))

        # Draw flame from bottom (y=HEIGHT-1) upward
        for y in range(HEIGHT):
            pos = HEIGHT - 1 - y   # 0 at bottom, HEIGHT-1 at top
            if pos > h:
                continue           # above flame — leave for fade to handle

            t = pos / h            # 0.0 = base, 1.0 = tip

            if t < 0.35:
                # Amber → Gold  (#FF8C00 → #FFD700)
                blend = t / 0.35
                r, g, b = 255, int(140 + 75 * blend), 0
            elif t < 0.72:
                # Gold → Warm Yellow  (#FFD700 → #FFFF80)
                blend = (t - 0.35) / 0.37
                r, g, b = 255, int(215 + 40 * blend), int(80 * blend)
            else:
                # Warm Yellow → Warm White  (#FFFF80 → #FFFFDC)
                blend = (t - 0.72) / 0.28
                r, g, b = 255, 255, int(80 + 140 * blend)

            byte_array[y][x] = [r, g, b]

        # Occasional gold spark flying above the tip
        if random.random() < SPARK_PROB:
            sy = HEIGHT - 1 - h - random.randint(1, 5)
            if 0 <= sy < HEIGHT:
                byte_array[sy][x] = [255, 200, 50]

    if escape[0]:
        break

fade_out_and_close()
