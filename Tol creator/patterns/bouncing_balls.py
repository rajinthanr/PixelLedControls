import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED       = 80
BALL_RADIUS = 4
BOX_SIZE    = 4    # checkerboard square size in pixels
N_BALLS     = 16
HUE_DRIFT   = 0.0015   # hue shift per physics step

_GREEN = [0, 255, 20]
_WHITE = [210, 210, 210]

# Pre-compute filled-circle offsets for drawing
_OFFSETS = [
    (dx, dy)
    for dy in range(-BALL_RADIUS, BALL_RADIUS + 1)
    for dx in range(-BALL_RADIUS, BALL_RADIUS + 1)
    if dx * dx + dy * dy <= BALL_RADIUS * BALL_RADIUS
]

# Each ball: [px, py, vx, vy, hue]
# Initial hues spread evenly so all 16 are immediately distinct
balls = [
    [
        random.uniform(BALL_RADIUS, WIDTH  - BALL_RADIUS - 1),
        random.uniform(BALL_RADIUS, HEIGHT - BALL_RADIUS - 1),
        random.choice([-1, 1]) * random.uniform(0.5, 1.0),
        random.choice([-1, 1]) * random.uniform(0.5, 1.0),
        i / N_BALLS,
    ]
    for i in range(N_BALLS)
]

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

    # ── checkerboard background ─────────────────────────────────────────────
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = _GREEN[:] if (x // BOX_SIZE + y // BOX_SIZE) % 2 == 0 else _WHITE[:]

    # ── update and draw balls ───────────────────────────────────────────────
    for b in balls:
        px, py, vx, vy, hue = b

        px += vx
        py += vy

        if px - BALL_RADIUS < 0:
            px = float(BALL_RADIUS);  vx =  abs(vx)
        elif px + BALL_RADIUS >= WIDTH:
            px = WIDTH  - BALL_RADIUS - 1.0;  vx = -abs(vx)
        if py - BALL_RADIUS < 0:
            py = float(BALL_RADIUS);  vy =  abs(vy)
        elif py + BALL_RADIUS >= HEIGHT:
            py = HEIGHT - BALL_RADIUS - 1.0;  vy = -abs(vy)

        hue = (hue + HUE_DRIFT) % 1.0
        b[0], b[1], b[2], b[3], b[4] = px, py, vx, vy, hue

        # filled circle with a brighter centre highlight
        cr, cg, cb = hsv_to_rgb(hue, 1.0, 1.0)
        bx0, by0 = int(px), int(py)
        for dx, dy in _OFFSETS:
            bx = bx0 + dx
            by = by0 + dy
            if 0 <= bx < WIDTH and 0 <= by < HEIGHT:
                # distance-based brightness: centre = 1.0, edge = 0.6
                dist = math.sqrt(dx * dx + dy * dy)
                bright = 1.0 - 0.4 * (dist / BALL_RADIUS)
                byte_array[by][bx] = [
                    int(cr * bright * 255),
                    int(cg * bright * 255),
                    int(cb * bright * 255),
                ]

    if escape[0]:
        break

fade_out_and_close()
