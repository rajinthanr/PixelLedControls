import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
import math

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED      = 25     # physics interval — lower = more updates per second
FADE       = 10     # afterglow decay per frame — lower = longer golden trail
BEAM_W     = 9      # beam half-width in pixels (beam spans 2×BEAM_W rows)
SWEEP_FREQ = 0.038  # sine oscillation speed — lower = slower, more majestic sweep
# ─────────────────────────────────────────────────────────────────────────────
# Each side's beam sweeps top↔bottom with a π offset for alternating sides,
# creating an accordion / chevron wave across the building.
#
# Colour gradient (centre → edge of beam):
#   Warm White [255, 255, 200]  →  Gold [255, 180, 0]  →  Amber trail (via fade)

sweep_t = 0.0

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

    sweep_t += SWEEP_FREQ

    for side in range(SIDES):
        # Even sides: normal phase  (beam descends first)
        # Odd  sides: π-shifted     (beam ascends first) → accordion effect
        phase  = sweep_t + (math.pi if side % 2 == 1 else 0)
        beam_y = (HEIGHT - 1) / 2.0 * (1 + math.sin(phase))   # 0 … HEIGHT-1

        col_start = side * STRIPS_PER_SIDE

        for x in range(col_start, col_start + STRIPS_PER_SIDE):
            for y in range(HEIGHT):
                dist = abs(y - beam_y)
                if dist >= BEAM_W:
                    continue

                t       = dist / BEAM_W                               # 0 centre → 1 edge
                falloff = math.exp(-(dist ** 2) / (2 * (BEAM_W / 3.0) ** 2))

                # Warm white core fading to gold toward the beam edge
                r = int(255 * falloff)
                g = int((255 - 75 * t) * falloff)    # 255 at centre → 180 at edge
                b = int(200 * (1 - t)  * falloff)    # 200 at centre →   0 at edge

                byte_array[y][x][0] = min(255, byte_array[y][x][0] + r)
                byte_array[y][x][1] = min(255, byte_array[y][x][1] + g)
                byte_array[y][x][2] = min(255, byte_array[y][x][2] + b)

    if escape[0]:
        break

fade_out_and_close()
