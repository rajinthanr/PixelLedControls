from functions import *

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED         = 25    # physics interval — lower = faster drops
FADE          = 18    # brightness cut per frame — higher = shorter trail
PARTICLE_COUNT = 180  # number of simultaneous drops
DROP_SPEED    = 0.5   # pixels the drop falls each physics step
TRAIL_LEN     = 12    # green trail length above the head (pixels)
# ─────────────────────────────────────────────────────────────────────────────
# Palette: Nediyakadu Pride — Bright White head, Emerald Green trail

drops       = [random.uniform(-HEIGHT, 0) for _ in range(PARTICLE_COUNT)]
x_positions = [random.randint(0, WIDTH - 1) for _ in range(PARTICLE_COUNT)]

while True and current_frame < FRAME_COUNT - 30:
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

    for i in range(PARTICLE_COUNT):
        y = int(drops[i])
        x = x_positions[i]

        # Bright white head at the leading edge of the falling drop
        if 0 <= y < HEIGHT:
            byte_array[y][x] = [255, 255, 255]

        # Emerald green trail fading upward (where the drop came from)
        for t in range(1, TRAIL_LEN + 1):
            ty = y - t
            if 0 <= ty < HEIGHT:
                g = int(220 * (1 - t / TRAIL_LEN))
                byte_array[ty][x][1] = min(255, byte_array[ty][x][1] + g)

        drops[i] += DROP_SPEED
        if drops[i] >= HEIGHT and current_frame < FRAME_COUNT - 120:
            drops[i] = random.uniform(-HEIGHT // 2, 0)
            x_positions[i] = random.randint(0, WIDTH - 1)

    if escape[0]:
        break

black_frame()
for i in range(30):
    save_frame()
cv2.destroyAllWindows()
print("✅ Done — Tol files/waterfall.tol")
