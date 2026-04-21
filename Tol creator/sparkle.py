from functions import *
import math

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED         = 33    # physics interval (≈ 1 step per frame)
SPARKLE_COUNT = 22    # new sparkles spawned per physics step
SPARKLE_LIFE  = 12    # physics steps each sparkle lives before fading out
BREATH_SPEED  = 0.05  # breathing frequency — higher = faster pulse
# ─────────────────────────────────────────────────────────────────────────────
# Palette: Kovil Glow — Deep Forest Green base, Pure White sparkles

breath_phase = 0.0
sparkles = {}   # {(x, y): remaining_life}

while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < SPEED:
        if count - pre_time > (1000 / 30):
            current_frame += 1
            save_frame()
            display_frame()
            pre_time = count
        continue
    pTloop = count

    breath_phase += BREATH_SPEED
    base_g = int(80 + 100 * (0.5 + 0.5 * math.sin(breath_phase)))  # oscillates 40–100

    # Repaint breathing green background
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = [0, base_g, 0]

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
        byte_array[sy][sx] = [brightness, max(base_g, brightness), brightness]
        sparkles[(sx, sy)] -= 1
        if sparkles[(sx, sy)] <= 0:
            dead.append((sx, sy))
    for k in dead:
        del sparkles[k]

    if escape[0]:
        break

black_frame()
for i in range(30):
    save_frame()
cv2.destroyAllWindows()
print("✅ Done — Tol files/sparkle.tol")
