import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED     = 80      # physics interval — controls grow speed
THICKNESS = 5       # lit pixels per diamond ring
GAP       = 2       # dark pixels between rings
PERIOD    = THICKNESS + GAP   # = 7
N_HUES    = 24      # pool size — nearby rings get distinct colours

cx = WIDTH  // 2   # 56
cy = HEIGHT // 2   # 25

# Pre-generate a fixed random hue for each ring index; ring k → hues[k % N_HUES]
hues = [random.random() for _ in range(N_HUES)]
t    = 0

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
            d  = abs(x - cx) + abs(y - cy)   # Manhattan distance = diamond metric
            td = t - d                         # how long ago this pixel's ring was spawned
            if td >= 0 and td % PERIOD < THICKNESS:
                h = hues[(td // PERIOD) % N_HUES]
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
