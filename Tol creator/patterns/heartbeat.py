import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

SPEED        = 120   # physics interval
FADE         = 8    # afterglow decay per frame
PULSE_STEP   = 1.5  # columns expanded per physics step
PULSE_THICK  = 5   # ring thickness in columns
BEAT_INTERVAL = 10  # physics steps between new beats

CENTER_X = WIDTH // 2
max_r    = WIDTH // 2 + PULSE_THICK

# pulses: [radius, (r, g, b)]
pulses     = []
beat_timer = 0

def _spawn():
    hue = random.random()
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    pulses.append([0.0, (int(r * 255), int(g * 255), int(b * 255))])

_spawn()   # start with one immediately

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

    beat_timer += 1
    if beat_timer >= BEAT_INTERVAL:
        beat_timer = 0
        _spawn()

    dead = []
    for i, (pulse_r, (br, bg, bb)) in enumerate(pulses):
        for x in range(WIDTH):
            dist    = abs(x - CENTER_X)
            overlap = pulse_r - dist

            if 0 < overlap <= PULSE_THICK:
                t = 1.0 - overlap / PULSE_THICK
                brightness = 1.0 - t * 0.5
                r = int(br * brightness)
                g = int(bg * brightness)
                b = int(bb * brightness)
                for y in range(HEIGHT):
                    byte_array[y][x][0] = min(255, byte_array[y][x][0] + r)
                    byte_array[y][x][1] = min(255, byte_array[y][x][1] + g)
                    byte_array[y][x][2] = min(255, byte_array[y][x][2] + b)

        pulses[i][0] += PULSE_STEP
        if pulses[i][0] > max_r:
            dead.append(i)

    for i in reversed(dead):
        pulses.pop(i)

    if escape[0]:
        break

fade_out_and_close()
