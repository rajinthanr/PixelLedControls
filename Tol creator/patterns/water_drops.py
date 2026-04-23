import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED      = 40
DROP_MAX_R = 50
RING_WIDTH = 3
GROW_SPEED = 0.6

panel_hues = [i / SIDES for i in range(SIDES)]


def new_drop(p, start_r=0.0):
    cx      = p * STRIPS_PER_SIDE + random.randint(1, STRIPS_PER_SIDE - 2)
    cy      = random.randint(1, HEIGHT - 2)
    new_hue = (panel_hues[p] + random.uniform(0.18, 0.45) * random.choice([-1, 1])) % 1.0
    return [cx, cy, start_r, new_hue]


# stagger initial radius so each panel starts at a different point in its cycle
drops = [new_drop(p, start_r=p * (DROP_MAX_R / SIDES)) for p in range(SIDES)]

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

    for p in range(SIDES):
        x0 = p * STRIPS_PER_SIDE
        x1 = x0 + STRIPS_PER_SIDE
        cx, cy, radius, new_hue = drops[p]

        # solid panel background
        r, g, b = hsv_to_rgb(panel_hues[p], 1.0, 1.0)
        col = [int(r * 255), int(g * 255), int(b * 255)]
        for y in range(HEIGHT):
            for x in range(x0, x1):
                byte_array[y][x] = col[:]

        r2     = int(radius)
        inner  = max(0, r2 - RING_WIDTH)
        inner2 = inner * inner
        outer2 = (r2 + 1) * (r2 + 1)

        # inner fill — new hue
        nr, ng, nb = hsv_to_rgb(new_hue, 1.0, 1.0)
        nc = [int(nr * 255), int(ng * 255), int(nb * 255)]
        for dy in range(-inner, inner + 1):
            for dx in range(-inner, inner + 1):
                if dx * dx + dy * dy <= inner2:
                    px, py = cx + dx, cy + dy
                    if x0 <= px < x1 and 0 <= py < HEIGHT:
                        byte_array[py][px] = nc[:]

        # solid dark ring
        for dy in range(-r2 - 1, r2 + 2):
            for dx in range(-r2 - 1, r2 + 2):
                d2 = dx * dx + dy * dy
                if inner2 < d2 <= outer2:
                    px, py = cx + dx, cy + dy
                    if x0 <= px < x1 and 0 <= py < HEIGHT:
                        byte_array[py][px] = [0, 0, 0]

        # grow after drawing so the last frame always renders before reset
        radius += GROW_SPEED
        if radius > DROP_MAX_R:
            panel_hues[p] = new_hue
            drops[p] = new_drop(p)
        else:
            drops[p][2] = radius

    if escape[0]:
        break

fade_out_and_close()
