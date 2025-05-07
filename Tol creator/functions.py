import random
import cv2
import numpy as np
import time
import keyboard

HEIGHT = 50
WIDTH = 128

FPS = 30
DURATION = 30  # seconds
FRAME_COUNT = FPS * DURATION+30+30
#FRAME_COUNT = 5*(4*HEIGHT+HEIGHT*3)
DROP_COUNT = 100  # Increase the number of single-pixel raindrops



current_frame = 0
pre_time = 0
pTloop = 0
count = 0

def delay(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        pass

def fade_pixels(byte_array, fade_value):
            for y in range(len(byte_array)):
                for x in range(len(byte_array[y])):
                    for c in range(3):  # Iterate over RGB channels
                        byte_array[y][x][c] = max(0, byte_array[y][x][c] - fade_value)

def save_frame():
    with open("output.tol", "ab") as f:
        for row in byte_array:
            for pixel in row:
                f.write(bytes(pixel))  # Write each pixel (RGB) as bytes

def display_frame():
    global pre_time
    pre_time = time.time()
    px = 10
    rgb_array = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    frame = np.zeros((HEIGHT * px, WIDTH * px, 3), dtype=np.uint8)  # Create a black canvas

    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = rgb_array[y, x]
            if np.any(color):  # If the pixel is not black
                cv2.circle(frame, (x * px + 2, y * px + 2), 2, color.tolist(), -1)  # Draw a dot

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frames.append(frame)


    cv2.imshow("RGB Animation", frame)
    cv2.waitKey(1)

def black_frame():
    global byte_array
    byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Define some hex values 
hex_values = [0x00,0xff,0xff,0xff,0xaa,0xaa,0xbb,0xbb,0x00,0x00,0x00,0x00,0x00,0x00]
# 14 bits meta data [x|num of frames xxx|height xx|width xx|0x00|0x00|0x00|0x00|0x00|0x00]



# Initialize drop positions (y-coordinates)

# Convert FRAME_COUNT to hex and split into 3 bytes
frame_count_hex = FRAME_COUNT.to_bytes(3, byteorder='big')

# Assign the split bytes to the 2nd, 3rd, and 4th positions in hex_values
hex_values[1] = frame_count_hex[0]
hex_values[2] = frame_count_hex[1]
hex_values[3] = frame_count_hex[2]

frame_count_hex = HEIGHT.to_bytes(2, byteorder='big')
# Assign the split bytes to the 5th, 6th positions in hex_values
hex_values[4] = frame_count_hex[0]
hex_values[5] = frame_count_hex[1]

frame_count_hex = WIDTH.to_bytes(2, byteorder='big')
# Assign the split bytes to the 7th, 8th positions in hex_values
hex_values[6] = frame_count_hex[0]
hex_values[7] = frame_count_hex[1]


with open("output.tol", "wb") as f:
    for value in hex_values:
        f.write(bytes([value]))  # write each as a single byte

frames = []
byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]
with open("output.tol", "ab") as f:
        for i in range(30):
            for row in byte_array:
                for pixel in row:
                    f.write(bytes(pixel))  # Write each pixel (RGB) as bytes


def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB color space."""
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)  # Assume h is in [0, 1]
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q