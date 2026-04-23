import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions import *

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED         = 33    # physics interval (≈ 1 step per frame)
SPARKLE_COUNT = 22    # new sparkles spawned per physics step
SPARKLE_LIFE  = 12    # physics steps each sparkle lives before fading out
RAINBOW_SPEED = 0.0008  # how fast the hue shifts — higher = faster cycle
BG_BRIGHTNESS = 0.99    # background saturation (0=grey, 1=full colour)
# ─────────────────────────────────────────────────────────────────────────────

hue_offset = 0.0
sparkles = {}   # {(x, y): remaining_life}

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

    hue_offset = (hue_offset + RAINBOW_SPEED) % 1.0

    # Repaint background: hue shifts smoothly across x (column) and time
    for y in range(HEIGHT):
        for x in range(WIDTH):
            hue = (hue_offset + x / WIDTH * 0.8 + y / HEIGHT * 0.15) % 1.0
            r, g, b = hsv_to_rgb(hue, 0.85, BG_BRIGHTNESS)
            byte_array[y][x] = [int(r * 255), int(g * 255), int(b * 255)]

    # Spawn new sparkles at random positions
    for _ in range(SPARKLE_COUNT):
        sx = random.randint(0, WIDTH - 1)
        sy = random.randint(0, HEIGHT - 1)
        sparkles[(sx, sy)] = SPARKLE_LIFE

    # Draw and age all active sparkles
    dead = []
    for (sx, sy), life in sparkles.items():
        t = life / SPARKLE_LIFE          # 1.0 (fresh) → 0.0 (gone)
        brightness = int(255 * t)
        byte_array[sy][sx] = [brightness, brightness, brightness]
        sparkles[(sx, sy)] -= 1
        if sparkles[(sx, sy)] <= 0:
            dead.append((sx, sy))
    for k in dead:
        del sparkles[k]

    if escape[0]:
        break

fade_out_and_close()
