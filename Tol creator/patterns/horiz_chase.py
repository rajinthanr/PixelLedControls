import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

BAND_SPEED   = 1      # columns moved per physics step
BAND_WIDTH   = 12     # width of each lit band in columns
DARK_GAP     = 3      # dark columns between bands
NUM_BANDS    = 10      # simultaneous bands
SPEED        = 50     # physics interval
HUE_DRIFT    = 0.004  # hue shift per physics step per band

_DARK = [8, 8, 8]     # near-black background (3-pixel-equivalent dark colour)

# Evenly space bands; each band has its own hue
PERIOD   = BAND_WIDTH + DARK_GAP
band_x   = [i * (WIDTH // NUM_BANDS) for i in range(NUM_BANDS)]
band_hue = [i / NUM_BANDS for i in range(NUM_BANDS)]

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

    for b in range(NUM_BANDS):
        hue = band_hue[b]
        for w in range(BAND_WIDTH):
            col = (band_x[b] + w) % WIDTH
            # brightness peaks at the centre of the band, dims toward edges
            t      = w / (BAND_WIDTH - 1)           # 0.0 → 1.0 across band
            bright = 0.4 + 0.6 * (1.0 - abs(t - 0.5) * 2)  # 0.4 at edges, 1.0 at centre
            # leading edge (w==0) gets a sharp white-hot tip
            sat = 0.3 if w == 0 else 1.0
            r, g, bl = hsv_to_rgb(hue, sat, bright)
            pix = [int(r * 255), int(g * 255), int(bl * 255)]
            for y in range(HEIGHT):
                byte_array[y][col] = pix[:]

        band_x[b]   = (band_x[b]   + BAND_SPEED) % WIDTH
        band_hue[b] = (band_hue[b] + HUE_DRIFT)  % 1.0

    if escape[0]:
        break

fade_out_and_close()
