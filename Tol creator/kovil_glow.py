from functions import *

WARM_WHITE   = [255, 255, 240]   # #FFFFF0
FOREST_GREEN = [0,   200, 0  ]   # brighter green
GOLD         = [255, 215, 0  ]   # #FFD700

WARM_WHITE_DIM   = [55, 55, 52]
FOREST_GREEN_DIM = [0,  80,  0]

# Even panels: WARM_WHITE top-to-bottom; Odd panels: FOREST_GREEN bottom-to-top
PANEL_COLOR = [WARM_WHITE   if s % 2 == 0 else FOREST_GREEN     for s in range(SIDES)]
PANEL_DIM   = [WARM_WHITE_DIM if s % 2 == 0 else FOREST_GREEN_DIM for s in range(SIDES)]
FILL_DOWN   = [s % 2 == 0 for s in range(SIDES)]

ODD_SIDES  = [s for s in range(SIDES) if s % 2 == 1]
EVEN_SIDES = [s for s in range(SIDES) if s % 2 == 0]

current_frame = 30


def save_display():
    global current_frame
    if escape[0] or current_frame >= FRAME_COUNT - 30:
        return
    current_frame += 1
    save_frame()
    display_frame()


def fill_group(group):
    for row in range(HEIGHT):
        if escape[0]:
            return
        for side in group:
            cs = side * STRIPS_PER_SIDE
            y  = row if FILL_DOWN[side] else (HEIGHT - 1 - row)
            for x in range(cs, cs + STRIPS_PER_SIDE):
                byte_array[y][x] = list(PANEL_COLOR[side])
        save_display()


def gold_fade(group, steps=90):
    # First half: panel colour → gold; second half: gold → dim glow
    half = steps // 2
    for step in range(steps):
        if escape[0]:
            return
        t = (step + 1) / half
        if step < half:
            # panel colour → gold
            for side in group:
                cs    = side * STRIPS_PER_SIDE
                src   = PANEL_COLOR[side]
                color = [int(src[c] + (GOLD[c] - src[c]) * t) for c in range(3)]
                for y in range(HEIGHT):
                    for x in range(cs, cs + STRIPS_PER_SIDE):
                        byte_array[y][x] = color
        else:
            # gold → dim glow
            t2 = (step - half + 1) / half
            for side in group:
                cs    = side * STRIPS_PER_SIDE
                dim   = PANEL_DIM[side]
                color = [int(GOLD[c] + (dim[c] - GOLD[c]) * t2) for c in range(3)]
                for y in range(HEIGHT):
                    for x in range(cs, cs + STRIPS_PER_SIDE):
                        byte_array[y][x] = color
        save_display()


def hold(frames=20):
    for _ in range(frames):
        if escape[0]:
            return
        save_display()


# Initial fill: all 7 panels simultaneously, each in their own direction
fill_group(list(range(SIDES)))
hold(20)

while not escape[0] and current_frame < FRAME_COUNT - 30:
    # Fade through gold → dim for odd panels; even panels stay lit
    gold_fade(ODD_SIDES)
    hold(10)

    # Refill odd panels (bottom-to-top) while even panels remain visible
    fill_group(ODD_SIDES)
    hold(10)

    # Fade through gold → dim for even panels; odd panels stay lit
    gold_fade(EVEN_SIDES)
    hold(10)

    # Refill even panels (top-to-bottom) while odd panels remain visible
    fill_group(EVEN_SIDES)
    hold(10)


black_frame()
for i in range(30):
    save_frame()

cv2.destroyAllWindows()
print("✅ Hex values written to output.tol")
