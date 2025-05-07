import random
import cv2
import numpy as np
import time

HEIGHT = 50
WIDTH = 128

# Define some hex values (as integers or strings)
hex_values = [0x00,0x01,0x00,0x00,0x00,0x0a,0x00,0x0a,0x00,0x00,0x00,0x00,0x00,0x00]
hex_values[5] = HEIGHT
hex_values[7] = WIDTH # Set the width and height in the hex values


FPS = 30
DURATION = 30  # seconds
FRAME_COUNT = FPS * DURATION
DROP_COUNT = 100  # Increase the number of single-pixel raindrops

# Initialize drop positions (y-coordinates)
drops = [random.randint(-HEIGHT, 0) for _ in range(DROP_COUNT)]
x_positions = [random.randint(0, WIDTH - 1) for _ in range(DROP_COUNT)]

# Convert FRAME_COUNT to hex and split into 3 bytes
frame_count_hex = FRAME_COUNT.to_bytes(3, byteorder='big')

# Assign the split bytes to the 2nd, 3rd, and 4th positions in hex_values
hex_values[1] = frame_count_hex[0]
hex_values[2] = frame_count_hex[1]
hex_values[3] = frame_count_hex[2]

with open("output.tol", "wb") as f:
    for value in hex_values:
        f.write(bytes([value]))  # write each as a single byte

frames = []

for _ in range(FRAME_COUNT):
    # Create a black background image
    # Create a 2D byte array with dimensions HEIGHT x WIDTH
    byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for i in range(DROP_COUNT):
        y = drops[i]
        x = x_positions[i]

        # Draw the raindrop as a single pixel
        if 0 <= y < HEIGHT:
            if(x%2):
                color = [255, 255, 255]  # Blue raindrop
            else:
                color = [0, 255, 0]  # Blue raindrop
            byte_array[y][x] = color
            #draw.point((x, y), fill=color)

        # Move the raindrop down
        drops[i] += 1

        # If the raindrop goes beyond the bottom, reset it at a random position
        if drops[i] >= HEIGHT:
            drops[i] = random.randint(-20, 0)
            x_positions[i] = random.randint(0, WIDTH - 1)
        
    with open("output.tol", "ab") as f:
        for row in byte_array:
            for pixel in row:
                f.write(bytes(pixel))  # Write each pixel (RGB) as bytes
    
    rgb_array = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH , 3))
    frame = cv2.resize(rgb_array, (WIDTH * 10, HEIGHT * 5), interpolation=cv2.INTER_NEAREST)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frames.append(frame)

# Show frames at 30 FPS
delay = 1 / 30  # seconds per frame
print("🔁 Playing animation at 30 FPS. Press ESC to exit.")
for frame in frames:
    cv2.imshow("RGB Animation", frame)
    if cv2.waitKey(int(delay * 1000)) == 27:  # ESC to break
        break

cv2.destroyAllWindows()


# Write to custom file

print("✅ Hex values written to output.tol")
