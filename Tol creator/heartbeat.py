from functions import *

# ── Tweak these values ───────────────────────────────────────────────────────
SPEED       = 33    # physics interval (≈ 1 step per frame)
FADE        = 8     # brightness cut per frame — controls green afterglow length
PULSE_STEP  = 1.5   # columns the ring expands per physics step
PULSE_THICK = 10    # ring thickness in columns
# ─────────────────────────────────────────────────────────────────────────────
# Palette: Kovil Glow — White leading edge fading to Green, then dark
# Origin: center of Side 4 (middle of the 7-sided building)

CENTER_X = WIDTH // 2   # column 56 — center of Side 4

pulse_r = 0.0
max_r   = WIDTH // 2 + PULSE_THICK   # past the outermost column

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

    for x in range(WIDTH):
        dist    = abs(x - CENTER_X)
        overlap = pulse_r - dist        # > 0 once the ring has passed this column

        if 0 < overlap <= PULSE_THICK:
            # t=0 → leading bright-white edge, t=1 → trailing green edge
            t = 1.0 - overlap / PULSE_THICK
            r = int(255 * (1 - t))
            g = int(100 * (1 - t) + 220 * t)
            b = int(255 * (1 - t))
            for y in range(HEIGHT):
                byte_array[y][x][0] = min(255, byte_array[y][x][0] + r)
                byte_array[y][x][1] = min(255, byte_array[y][x][1] + g)
                byte_array[y][x][2] = min(255, byte_array[y][x][2] + b)

    pulse_r += PULSE_STEP
    if pulse_r > max_r:
        pulse_r = 0.0   # restart the heartbeat

    if escape[0]:
        break

black_frame()
for i in range(30):
    save_frame()
cv2.destroyAllWindows()
print("✅ Done — Tol files/heartbeat.tol")
