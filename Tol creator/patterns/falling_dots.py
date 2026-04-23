import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED          = 80
FADE           = 2
PARTICLE_COUNT = WIDTH * 3  # 3 staggered particles per column = very dense

# Each particle: [x, y, hue]  — hue is fixed per particle for a mixed look
particles = [
    [
        i % WIDTH,
        (i // WIDTH) * (HEIGHT // 3) + random.randint(0, HEIGHT // 3 - 1),
        random.random(),   # random hue in [0.0, 1.0]
    ]
    for i in range(PARTICLE_COUNT)
]

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

    for p in particles:
        x, y, hue = p

        color = hsv_to_rgb(hue, 1.0, 1.0)
        byte_array[y][x][0] = int(color[0] * 255)
        byte_array[y][x][1] = int(color[1] * 255)
        byte_array[y][x][2] = int(color[2] * 255)

        # 45-degree fall: one step right, one step down
        p[0] = (x + 1) % WIDTH
        p[1] = (y + 1) % HEIGHT

    if escape[0]:
        break

fade_out_and_close()
