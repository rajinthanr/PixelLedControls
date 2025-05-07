from functions import *

escape = False
def exit_program():
    global escape
    escape = True
    print("Exiting program...")

keyboard.add_hotkey('esc', exit_program)

# Define Tetris block shapes

# Define Tetris block shapes and their corresponding colors
# Define confetti colors

# Initialize confetti particles
PARTICLE_COUNT = 100  # Number of confetti particles
particles = [(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT)) for _ in range(PARTICLE_COUNT)]
particle_hues = [random.randint(0, 360) for _ in range(PARTICLE_COUNT)]  # Store hues for particles

# Main loop
while True and current_frame < FRAME_COUNT - 30:
    count += 1
    if count - pTloop < 30:
        if count - pre_time > (1000 / 30):
            current_frame += 1

            save_frame()  # Save the current frame to the tol file
            display_frame()  # Display the current frame on window

            print("Frame: ", current_frame, " / ", FRAME_COUNT, end="\r")
            pre_time = count
            fade_pixels(byte_array, 2)
        continue

    pTloop = count

    for i in range(PARTICLE_COUNT):
        x, y = particles[i]
        hue = count / 100 + random.randint(0, 50) + y*4
        color = hsv_to_rgb(hue / 360.0, 1.0, 1.0)  # Assuming hsv_to_rgb is defined elsewhere

        # Update particle position for left-to-right sweeping motion
        new_x = (x + 1) % WIDTH  # Move right, wrap around at the screen edge
        new_y = y #+ random.randint(-1, 1)  # Slightly vary vertical position

        # Ensure particles stay within bounds
        new_y = max(0, min(HEIGHT - 1, new_y))

        particles[i] = (new_x, new_y)  # Update particle position

        for j in range(3):
            if byte_array[new_y][new_x][j] == 0:
                byte_array[new_y][new_x][j] = int(color[j] * 255)

    if escape:
        break

black_frame()  # Clear the screen
for i in range(30):
    save_frame()  # Save the last frame to the tol file

cv2.destroyAllWindows()

# Write to custom file

print("✅ Hex values written to output.tol")
