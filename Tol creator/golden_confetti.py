from functions import *

# ── Warm golden confetti palette ─────────────────────────────────────────────
WARM_COLORS = [
    [255, 215,   0],   # Gold          #FFD700
    [255, 165,   0],   # Golden orange #FFA500
    [255, 140,   0],   # Amber         #FF8C00
    [255, 200,  50],   # Light gold
    [255, 255, 200],   # Warm white
    [255, 180,   0],   # Deep gold
]

PARTICLE_COUNT = 40
particles = [(random.randint(0, WIDTH - 1), random.randint(-HEIGHT, 0)) for _ in range(PARTICLE_COUNT)]

# Main loop
while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < 30:
        if count - pre_time > (1000 / 30):
            current_frame += 1

            save_frame()
            display_frame()

            pre_time = count
            fade_pixels(byte_array, 0.7)
        continue

    pTloop = count

    for i in range(PARTICLE_COUNT):
        x, y = particles[i]
        color = random.choice(WARM_COLORS)
        new_x = random.randint(0, WIDTH)
        new_y = random.randint(0, HEIGHT)
        
        # Ensure particles stay within bounds
        new_x = max(0, min(WIDTH - 1, new_x))
        new_y = max(0, min(HEIGHT - 1, new_y))
        
        for j in range(3):
            byte_array[new_y][new_x][j] = int(color[j] * 255)
            byte_array[new_y][new_x][j] = min(255, byte_array[new_y][new_x][j])

    if escape[0]:
        break

black_frame()  # Clear the screen
for i in range(30):
    save_frame()  # Save the last frame to the tol file

cv2.destroyAllWindows()

# Write to custom file

print("✅ Hex values written to output.tol")
