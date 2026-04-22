import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

# ── Palette ──────────────────────────────────────────────────────────────────
LEAF_GREEN    = [50,  210,  60]   # child-leaf green
GOLDEN_ORANGE = [255, 160,   0]   # golden orange
WHITE         = [255, 255, 255]
BLACK         = [0,   0,    0]

# ── Timing ───────────────────────────────────────────────────────────────────
FADE_STEPS  = 30   # frames per colour crossfade
HOLD        = 15   # pause frames between phases
SHORT_HOLD  = 6    # brief pause between per-side steps

ODD_SIDES  = [0, 2, 4, 6]   # 0-indexed (building sides 1, 3, 5, 7)
EVEN_SIDES = [1, 3, 5]      # 0-indexed (building sides 2, 4, 6)

# ── Helpers ───────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return [int(a[i] + (b[i] - a[i]) * t) for i in range(3)]

def set_row(side, row, color):
    """Paint one horizontal row of one panel."""
    if not (0 <= row < HEIGHT):
        return
    cs = side * STRIPS_PER_SIDE
    for x in range(cs, cs + STRIPS_PER_SIDE):
        byte_array[row][x] = list(color)

def set_side(side, color):
    """Fill an entire panel with a solid colour."""
    for row in range(HEIGHT):
        set_row(side, row, color)

def tick():
    if not escape[0]:
        display_frame()
        save_frame()

def hold(n=HOLD):
    for _ in range(n):
        tick()

def fade_side(side, src, dst, steps=FADE_STEPS):
    """Crossfade one panel from src to dst colour."""
    for s in range(steps):
        if escape[0]:
            return
        set_side(side, lerp(src, dst, s / (steps - 1)))
        tick()

def fill_from_edges(sides, color):
    """Top and bottom rows advance toward centre simultaneously."""
    for step in range(HEIGHT // 2 + 1):
        if escape[0]:
            return
        top    = step
        bottom = HEIGHT - 1 - step
        for side in sides:
            set_row(side, top, color)
            if bottom != top:
                set_row(side, bottom, color)
        tick()

def wipe_from_center(side, color):
    """Rows spread outward from the centre of one panel."""
    for step in range(HEIGHT // 2 + 1):
        if escape[0]:
            return
        top    = HEIGHT // 2 - step
        bottom = HEIGHT // 2 + step
        set_row(side, top, color)
        if bottom != top:
            set_row(side, bottom, color)
        tick()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Fill ALL sides from top & bottom with leaf green simultaneously
# ═══════════════════════════════════════════════════════════════════════════════
fill_from_edges(list(range(SIDES)), LEAF_GREEN)
hold()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Fade each side to golden orange, one by one (left → right)
# ═══════════════════════════════════════════════════════════════════════════════
for side in range(SIDES):
    if escape[0]:
        break
    fade_side(side, LEAF_GREEN, GOLDEN_ORANGE)
    hold(SHORT_HOLD)

hold()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — Each side: black wipe from centre outward, then fade up to white
# ═══════════════════════════════════════════════════════════════════════════════
for side in range(SIDES):
    if escape[0]:
        break
    wipe_from_center(side, BLACK)     # centre goes dark first, edges last
    fade_side(side, BLACK, WHITE)     # bloom back up to white
    hold(SHORT_HOLD)

hold()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — Odd sides: shutter-close to black (edges close inward like doors)
# ═══════════════════════════════════════════════════════════════════════════════
fill_from_edges(ODD_SIDES, BLACK)    # top + bottom advance toward centre
hold()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — Odd sides: shutter-open to leaf green (centre expands outward)
# ═══════════════════════════════════════════════════════════════════════════════
for side in ODD_SIDES:
    if escape[0]:
        break
    wipe_from_center(side, LEAF_GREEN)

hold()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — Same shutter sequence for even sides
# ═══════════════════════════════════════════════════════════════════════════════
fill_from_edges(EVEN_SIDES, BLACK)   # close
hold()

for side in EVEN_SIDES:
    if escape[0]:
        break
    wipe_from_center(side, LEAF_GREEN)   # open to green

hold()

fade_out_and_close()
