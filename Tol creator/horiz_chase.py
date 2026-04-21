from functions import *

# ── Tweak these values ───────────────────────────────────────────────────────
BAND_SPEED  = 1     # columns the band moves per physics step — higher = faster
BAND_WIDTH  = 4    # width of each white band in columns
NUM_BANDS   = 8     # number of simultaneous sweeping bands
SPEED       = 50    # physics interval (≈ 1 step per frame)
# ─────────────────────────────────────────────────────────────────────────────
# Palette: Kovil Glow — Forest Green bg, Warm White bands, Gold leading edge
BG    = [0,   150,  0]    # Deep Forest Green #006400
WHITE = [255, 255, 240]   # Warm White #FFFFF0
GOLD  = [255, 215,  0]    # Gold leading edge #FFD700

# Space bands evenly across the grid
band_x = [i * (WIDTH // NUM_BANDS) for i in range(NUM_BANDS)]

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

    # Repaint full scene each physics step (no fading needed)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            byte_array[y][x] = list(BG)

    for b in range(NUM_BANDS):
        for w in range(BAND_WIDTH):
            col = (band_x[b] + w) % WIDTH
            color = GOLD if w == 0 else WHITE   # gold on leading pixel
            for y in range(HEIGHT):
                byte_array[y][col] = list(color)
        band_x[b] = (band_x[b] + BAND_SPEED) % WIDTH

    if escape[0]:
        break

black_frame()
for i in range(30):
    save_frame()
cv2.destroyAllWindows()
print("✅ Done — Tol files/horiz_chase.tol")
