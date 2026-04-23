import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
import numpy as np

SPEED = 30  # physics interval — lower = faster pattern movement

# Static coordinate grids (computed once)
_xs = np.arange(WIDTH,  dtype=np.float32)
_ys = np.arange(HEIGHT, dtype=np.float32)
_X, _Y = np.meshgrid(_xs, _ys)
_D = np.sqrt((_X - WIDTH / 2) ** 2 + (_Y - HEIGHT / 2) ** 2)

t          = 0.0
hue_offset = 0.0

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

    t          += 0.07
    hue_offset  = (hue_offset + 0.0015) % 1.0

    # Four overlapping sine waves — horizontal, vertical, diagonal, radial
    v = (np.sin(_X / 9.0  + t) +
         np.sin(_Y / 6.0  + t * 0.85) +
         np.sin((_X + _Y) / 11.0 - t * 0.70) +
         np.sin(_D / 7.0  - t * 1.10))   # shape (HEIGHT, WIDTH), range ≈ -4..4

    # Map plasma value → hue in [0, 1], then rotate palette over time
    hue = (v * 0.125 + 0.5 + hue_offset) % 1.0

    # Vectorised HSV → RGB (saturation=1, value=1 — always full brightness)
    h6 = hue * 6.0
    hi = h6.astype(np.int32) % 6
    f  = (h6 - np.floor(h6)).astype(np.float32)
    q  = 1.0 - f

    R = np.select([hi==0, hi==1, hi==2, hi==3, hi==4, hi==5], [1, q, 0, 0, f, 1])
    G = np.select([hi==0, hi==1, hi==2, hi==3, hi==4, hi==5], [f, 1, 1, q, 0, 0])
    B = np.select([hi==0, hi==1, hi==2, hi==3, hi==4, hi==5], [0, 0, f, 1, 1, q])

    rgb = (np.stack([R, G, B], axis=2) * 255).astype(np.uint8)

    for y in range(HEIGHT):
        byte_array[y] = rgb[y].tolist()

    if escape[0]:
        break

fade_out_and_close()
