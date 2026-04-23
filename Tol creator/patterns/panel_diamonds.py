import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED     = 80
THICKNESS = 5
GAP       = 2
PERIOD    = THICKNESS + GAP   # = 7
N_HUES    = 24

cy = HEIGHT // 2

# Each panel gets its own hue pool, offset evenly around the colour wheel
# so adjacent panels always look distinct
panel_hues = [
    [((random.random() + s / SIDES) % 1.0) for _ in range(N_HUES)]
    for s in range(SIDES)
]

# Stagger each panel's diamond phase so they're not all in sync
panel_offset = [s * PERIOD for s in range(SIDES)]

t = 0

while True and current_frame < FRAME_COUNT - TAIL_FRAMES:
    count += 1
    if count - pTloop < SPEED:
        if count - pre_time > (1000 / 30):
            current_frame += 1
            save_frame()
            display_frame()
            pre_time = count
        continue

    pTloop = count
    t += 1

    for y in range(HEIGHT):
        for x in range(WIDTH):
            side = x // STRIPS_PER_SIDE
            cx   = side * STRIPS_PER_SIDE + STRIPS_PER_SIDE // 2
            d    = abs(x - cx) + abs(y - cy)
            td   = (t + panel_offset[side]) - d
            if td >= 0 and td % PERIOD < THICKNESS:
                h = panel_hues[side][(td // PERIOD) % N_HUES]
                r, g, b = hsv_to_rgb(h, 1.0, 1.0)
                byte_array[y][x][0] = int(r * 255)
                byte_array[y][x][1] = int(g * 255)
                byte_array[y][x][2] = int(b * 255)
            else:
                byte_array[y][x][0] = 0
                byte_array[y][x][1] = 0
                byte_array[y][x][2] = 0

    if escape[0]:
        break

fade_out_and_close()
