import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

BAND_SPEED  = 1
BAND_WIDTH  = 12
DARK_GAP    = 3
NUM_BANDS   = 10
SPEED       = 50
HUE_DRIFT   = 0.004

_DARK = [8, 8, 8]

# Divide HEIGHT into three equal horizontal strips
STRIP_H = HEIGHT // 3          # ~16 rows each
STRIPS = [
    (0,           STRIP_H,       +1,  0.00),   # top    — moves right, red hues
    (STRIP_H,     STRIP_H * 2,   -1,  0.33),   # middle — moves left,  green hues
    (STRIP_H * 2, HEIGHT,        +1,  0.66),   # bottom — moves right, blue hues
]

# Each strip has its own set of bands
band_x   = [[i * (WIDTH // NUM_BANDS) for i in range(NUM_BANDS)] for _ in STRIPS]
band_hue = [[(base + i / NUM_BANDS) % 1.0 for i in range(NUM_BANDS)] for _, _, _, base in STRIPS]

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

    # Dark background
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = _DARK[:]

    for s, (y0, y1, direction, _) in enumerate(STRIPS):
        for b in range(NUM_BANDS):
            hue = band_hue[s][b]
            for w in range(BAND_WIDTH):
                col = (band_x[s][b] + w) % WIDTH
                t      = w / (BAND_WIDTH - 1)
                bright = 0.4 + 0.6 * (1.0 - abs(t - 0.5) * 2)
                sat    = 0.3 if w == 0 else 1.0
                r, g, bl = hsv_to_rgb(hue, sat, bright)
                pix = [int(r * 255), int(g * 255), int(bl * 255)]
                for y in range(y0, y1):
                    byte_array[y][col] = pix[:]

            band_x[s][b]   = (band_x[s][b]   + direction * BAND_SPEED) % WIDTH
            band_hue[s][b] = (band_hue[s][b] + HUE_DRIFT) % 1.0

    if escape[0]:
        break

fade_out_and_close()
