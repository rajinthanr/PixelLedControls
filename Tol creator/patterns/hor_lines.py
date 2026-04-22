from functions import *

# ── Tweak these two values ───────────────────────────────────────────────────
SPEED      = 80   # physics updates per frame — lower = faster movement
FADE       = 15   # brightness subtracted each frame (0–255) — higher = shorter trail
# ─────────────────────────────────────────────────────────────────────────────

PARTICLE_COUNT = 500
particles = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT)) for _ in range(PARTICLE_COUNT)]

# Main loop
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
        x, y = particles[i]
        hue = 120  # Fixed hue for green
        saturation = 1.0 - (y*2 / HEIGHT)%1  # Gradually decrease saturation from green to white
        color = hsv_to_rgb(hue / 360.0, saturation, 1.0)  # Assuming hsv_to_rgb is defined elsewhere

        # Update particle position for left-to-right sweeping motion
        new_x = (x + 1) % WIDTH  # Move right, wrap around at the screen edge
        new_y = y #+ random.randint(-1, 1)  # Slightly vary vertical position

        # Ensure particles stay within bounds
        new_y = max(0, min(HEIGHT - 1, new_y))
        if new_x >= WIDTH:
            new_x = 0

        particles[i] = (new_x, new_y)  # Update particle position

        for j in range(3):
            byte_array[new_y][new_x][j] = int(color[j] * 255)

    if escape[0]:
        break

fade_out_and_close()
