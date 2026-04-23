import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
import math

SPEED         = 40       # physics interval
MAX_DROPS     = 20       # max simultaneous drop rings across all panels
DROP_INTERVAL = 16       # physics steps between spawns
DROP_MAX_R    = 80       # radius at which a ring fades out
RING_WIDTH    = 5      # thickness of the dark ring band
GROW_SPEED    = 0.3     # radius pixels added per physics step
# Each panel has its own drift speed — spread from slow to fast so they diverge
panel_hues  = [i / SIDES for i in range(SIDES)]
panel_drift = [0.003 + i * 0.0015 for i in range(SIDES)]

drops      = []   # [cx, cy, radius, panel_index]
drop_timer = 0

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

    # Slowly drift every panel's hue independently
    for s in range(SIDES):
        panel_hues[s] = (panel_hues[s] + panel_drift[s]) % 1.0

    drop_timer += 1

    # Spawn a new drop in a random panel at a random position
    if drop_timer >= DROP_INTERVAL and len(drops) < MAX_DROPS:
        drop_timer = 0
        panel = random.randint(0, SIDES - 1)
        cx = panel * STRIPS_PER_SIDE + random.randint(2, STRIPS_PER_SIDE - 3)
        cy = random.randint(2, HEIGHT - 3)
        drops.append([cx, cy, 0.0, panel])

    # Paint each panel with its solid hue background
    for s in range(SIDES):
        r, g, b = hsv_to_rgb(panel_hues[s], 1.0, 1.0)
        pr, pg, pb = int(r * 255), int(g * 255), int(b * 255)
        x0 = s * STRIPS_PER_SIDE
        for y in range(HEIGHT):
            for x in range(x0, x0 + STRIPS_PER_SIDE):
                byte_array[y][x] = [pr, pg, pb]

    # Grow and render each expanding ring
    dead = []
    for i, (cx, cy, radius, panel) in enumerate(drops):
        drops[i][2] += GROW_SPEED
        radius = drops[i][2]
        if radius > DROP_MAX_R:
            dead.append(i)
            continue

        # Ring fades as it expands
        intensity = 1.0 - (radius / DROP_MAX_R) ** 0.7

        x_min = panel * STRIPS_PER_SIDE
        x_max = x_min + STRIPS_PER_SIDE
        ir = int(radius) + 2

        for dy in range(-ir, ir + 1):
            for dx in range(-ir, ir + 1):
                dist = math.sqrt(dx * dx + dy * dy)
                ring_inner = max(0.0, radius - RING_WIDTH)
                if dist < ring_inner - 0.5 or dist > radius + 0.5:
                    continue
                px = cx + dx
                py = (cy + dy) % HEIGHT
                if px < x_min or px >= x_max:
                    continue
                # Bell curve: peaks in the middle of the ring band, 0 at edges
                t = (dist - ring_inner) / (radius - ring_inner + 0.001)
                bell = 1.0 - abs(2.0 * t - 1.0)
                alpha = max(0.0, bell) * intensity * 0.95
                byte_array[py][px] = [
                    int(byte_array[py][px][0] * (1.0 - alpha)),
                    int(byte_array[py][px][1] * (1.0 - alpha)),
                    int(byte_array[py][px][2] * (1.0 - alpha)),
                ]

    for i in reversed(dead):
        drops.pop(i)

    if escape[0]:
        break

fade_out_and_close()
