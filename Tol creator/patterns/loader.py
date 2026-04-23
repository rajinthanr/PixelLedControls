import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *
import math

GREEN = [0, 255, 0]
RED   = [255, 0, 0]
CYAN  = [0, 255, 255]

current_frame = LEAD_FRAMES


def save_display():
    global current_frame
    if escape[0] or current_frame >= FRAME_COUNT - TAIL_FRAMES:
        return
    current_frame += 1
    save_frame()
    display_frame()


def done():
    return escape[0] or current_frame >= FRAME_COUNT - TAIL_FRAMES


def fill_all(color):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = color[:]


def paint_panel(s, color):
    x0 = s * STRIPS_PER_SIDE
    for y in range(HEIGHT):
        for x in range(x0, x0 + STRIPS_PER_SIDE):
            byte_array[y][x] = color[:]


def hold(n):
    for _ in range(n):
        if done():
            return
        save_display()


# ─────────────────────────────────────────────────────────────────────────────

while not done():

    # ── Phase 1: All bright green (2 s) ──────────────────────────────────────
    fill_all(GREEN)
    hold(60)
    if done():
        break

    # ── Phase 2: Panels corrupt to red one by one ─────────────────────────────
    def corrupt_panel(s):
        x0 = s * STRIPS_PER_SIDE
        # Row-level glitch: entire rows flip between green/red, escalating ratio
        for red_prob in [0.15, 0.15, 0.40, 0.40, 0.65, 0.65, 0.88, 0.88]:
            if done():
                return
            for y in range(HEIGHT):
                col = RED if random.random() < red_prob else GREEN
                for x in range(x0, x0 + STRIPS_PER_SIDE):
                    byte_array[y][x] = col[:]
            save_display()
        paint_panel(s, RED)
        hold(6)

    order = list(range(SIDES))
    random.shuffle(order)
    for s in order:
        if done():
            break
        corrupt_panel(s)
    hold(20)
    if done():
        break

    # ── Phase 3: Green fights gravity for 8 s, eventually loses ──────────────
    PHASE3        = 240      # 8 s at 30 fps
    GRAVITY       = 0.22
    PUSH_INTERVAL = 20       # frames between upward pushes
    MAX_REACH     = HEIGHT * 0.95   # green nearly reaches top at peak

    levels = [0.0] * SIDES
    vels   = [0.0] * SIDES

    for frame in range(PHASE3):
        if done():
            break
        t_norm = frame / PHASE3
        decay  = (1.0 - t_norm) ** 1.2   # pushes get weaker as time goes on

        # Upward push — fighting the red corruption
        # Push force chosen so peak reach is 50–90% of height at start
        if frame % PUSH_INTERVAL == 0:
            for s in range(SIDES):
                vels[s] += random.uniform(4.5, 6.5) * decay

        # Physics update
        for s in range(SIDES):
            vels[s]   -= GRAVITY
            levels[s] += vels[s]
            if levels[s] < 0:
                levels[s] = 0.0
                vels[s]   = 0.0
            elif levels[s] > MAX_REACH:
                levels[s] = MAX_REACH
                vels[s]   = -abs(vels[s]) * 0.20   # bounce back down

        # Render: bottom `level` rows green, rest red — different heights per panel
        for s in range(SIDES):
            lv = int(levels[s])
            x0 = s * STRIPS_PER_SIDE
            for y in range(HEIGHT):
                col = GREEN if y >= HEIGHT - lv else RED
                for x in range(x0, x0 + STRIPS_PER_SIDE):
                    byte_array[y][x] = col[:]
        save_display()

    # Gravity wins — all red
    fill_all(RED)
    hold(20)
    if done():
        break

    # ── Phase 4: Cyan invades from top-right corner, panel by panel ───────────
    PHASE4  = 105
    max_d   = math.sqrt((STRIPS_PER_SIDE - 1) ** 2 + (HEIGHT - 1) ** 2)

    # Right panels start first; slight random offset between each
    p_start = [max(0, (SIDES - 1 - s) * 11 + random.randint(-2, 4))
               for s in range(SIDES)]
    remaining = PHASE4 - max(p_start) - 4
    p_speed   = max_d / max(remaining, 1)

    for frame in range(PHASE4):
        if done():
            break
        for s in range(SIDES):
            if frame < p_start[s]:
                continue
            wave = (frame - p_start[s]) * p_speed
            x0  = s * STRIPS_PER_SIDE
            cx  = x0 + STRIPS_PER_SIDE - 1   # top-right x of this panel
            for y in range(HEIGHT):
                for x in range(x0, x0 + STRIPS_PER_SIDE):
                    if math.sqrt((x - cx) ** 2 + y ** 2) <= wave:
                        byte_array[y][x] = CYAN[:]
        save_display()

    fill_all(CYAN)
    hold(10)
    if done():
        break

    # ── Phase 5: Green floods from bottom — different rates per panel ─────────
    PHASE5   = 95
    f_start  = [random.randint(0, 18) for _ in range(SIDES)]
    f_dur    = 60   # frames for a panel to fill fully

    for frame in range(PHASE5):
        if done():
            break
        for s in range(SIDES):
            if frame < f_start[s]:
                continue
            lv = int(HEIGHT * min(1.0, (frame - f_start[s]) / f_dur))
            x0 = s * STRIPS_PER_SIDE
            for y in range(HEIGHT - lv, HEIGHT):
                for x in range(x0, x0 + STRIPS_PER_SIDE):
                    byte_array[y][x] = GREEN[:]
        save_display()

    fill_all(GREEN)

    # ── Phase 6: Hold 3 s then loop ───────────────────────────────────────────
    hold(90)

fade_out_and_close()
