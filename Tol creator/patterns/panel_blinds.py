import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SLAT_COUNT     = 5
SLAT_H         = HEIGHT // SLAT_COUNT
FRAMES_PER_COL = 2
HOLD_FRAMES    = 25

current_frame = LEAD_FRAMES

panel_hues = [random.random() for _ in range(SIDES)]

# Two alternating groups — one stays lit while the other opens/closes
GROUP_A = [0, 2, 4, 6]   # 4 panels
GROUP_B = [1, 3, 5]      # 3 panels


def save_display():
    global current_frame
    if escape[0] or current_frame >= FRAME_COUNT - TAIL_FRAMES:
        return
    current_frame += 1
    save_frame()
    display_frame()


def slat_dir(slat, side):
    return (slat % 2 == 0) ^ (side % 2 == 1)


def shutter_close(sides):
    for col_step in range(STRIPS_PER_SIDE):
        if escape[0]:
            return
        for side in sides:
            cs = side * STRIPS_PER_SIDE
            r, g, b = hsv_to_rgb(panel_hues[side], 1.0, 1.0)
            color = [int(r * 255), int(g * 255), int(b * 255)]
            for slat in range(SLAT_COUNT):
                col = col_step if slat_dir(slat, side) else (STRIPS_PER_SIDE - 1 - col_step)
                y0  = slat * SLAT_H
                y1  = y0 + SLAT_H if slat < SLAT_COUNT - 1 else HEIGHT
                for y in range(y0, y1):
                    byte_array[y][cs + col] = color[:]
        for _ in range(FRAMES_PER_COL):
            save_display()


def shutter_open(sides):
    for col_step in range(STRIPS_PER_SIDE):
        if escape[0]:
            return
        for side in sides:
            cs = side * STRIPS_PER_SIDE
            for slat in range(SLAT_COUNT):
                col = (STRIPS_PER_SIDE - 1 - col_step) if slat_dir(slat, side) else col_step
                y0  = slat * SLAT_H
                y1  = y0 + SLAT_H if slat < SLAT_COUNT - 1 else HEIGHT
                for y in range(y0, y1):
                    byte_array[y][cs + col] = [0, 0, 0]
        for _ in range(FRAMES_PER_COL):
            save_display()


def hold(frames):
    for _ in range(frames):
        if escape[0]:
            return
        save_display()


# Start: fill all panels from black
for y in range(HEIGHT):
    for x in range(WIDTH):
        byte_array[y][x] = [0, 0, 0]

shutter_close(list(range(SIDES)))
hold(HOLD_FRAMES)

while not escape[0] and current_frame < FRAME_COUNT - TAIL_FRAMES:
    # Open group A — group B stays fully lit
    shutter_open(GROUP_A)
    hold(5)
    for s in GROUP_A:
        panel_hues[s] = random.random()
    shutter_close(GROUP_A)
    hold(HOLD_FRAMES)

    # Open group B — group A stays fully lit
    shutter_open(GROUP_B)
    hold(5)
    for s in GROUP_B:
        panel_hues[s] = random.random()
    shutter_close(GROUP_B)
    hold(HOLD_FRAMES)

fade_out_and_close()
