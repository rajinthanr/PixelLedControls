import random
import cv2
import numpy as np
import time
import sys
import os
import json

_script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
_tol_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..', 'Tol files'))
OUTPUT_FILE = os.path.join(_tol_dir, _script_name + '.tol')

_WIN_NAME = "RGB Animation"
_WIN_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.window_config.json')

def _load_win_config():
    if os.path.exists(_WIN_CONFIG):
        with open(_WIN_CONFIG) as f:
            return json.load(f)
    return None

def _save_win_config():
    try:
        rect = cv2.getWindowImageRect(_WIN_NAME)
        if rect[2] > 0 and rect[3] > 0:
            with open(_WIN_CONFIG, 'w') as f:
                json.dump({'w': rect[2], 'h': rect[3]}, f)
    except Exception:
        pass

HEIGHT      = 50    # LEDs per strip
SIDES       = 7     # sides of the building (8-sided, front open)
STRIPS_PER_SIDE = 16
WIDTH       = SIDES * STRIPS_PER_SIDE  # 112 total columns

FPS = 30
DURATION = 30  # seconds
FRAME_COUNT = FPS * DURATION + 30 + 30
DROP_COUNT = 400

# --- display constants ---
# dot diameter d=6, gap between dots = 1.5×d = 9 → cell pitch = 2.5×d = 15
_DOT_R   = 3                               # dot radius in pixels
_PX      = int(_DOT_R * 2 * 2.5)          # cell pitch = 15px
_GAP     = 10                              # gap between side panels
_LABEL_H = 24                              # header height for side labels
_PANEL_W = STRIPS_PER_SIDE * _PX          # width of one panel in pixels
_FRAME_W = SIDES * _PANEL_W + (SIDES - 1) * _GAP
_FRAME_H = HEIGHT * _PX + _LABEL_H



escape = [False]  # mutable so all scripts share the same object after import
_disp_count = [0]  # counts display_frame() calls for progress printing

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
    with open(OUTPUT_FILE, "ab") as f:
        for row in byte_array:
            for pixel in row:
                pixel = [int(min(255, max(0, pix))) for pix in pixel ]  # Ensure pixel values are capped at 255
                f.write(bytes(pixel))  # Write each pixel (RGB) as bytes

def display_frame():
    global pre_time
    pre_time = time.time()

    rgb_array = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    frame = np.zeros((_FRAME_H, _FRAME_W, 3), dtype=np.uint8)

    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        for y in range(HEIGHT):
            for x in range(STRIPS_PER_SIDE):
                color = rgb_array[y, side * STRIPS_PER_SIDE + x]
                if np.any(color):
                    cx = x_off + x * _PX + _PX // 2
                    cy = _LABEL_H + y * _PX + _PX // 2
                    cv2.circle(frame, (cx, cy), _DOT_R, color.tolist(), -1)

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        # green label centred above each panel
        label = f"Side {side + 1}"
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(frame, label, (x_off + (_PANEL_W - tw) // 2, _LABEL_H - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1, cv2.LINE_AA)
        # dark separator line between panels
        if side < SIDES - 1:
            sep_x = x_off + _PANEL_W + _GAP // 2
            cv2.line(frame, (sep_x, 0), (sep_x, _FRAME_H), (50, 50, 50), 2)

    frames.append(frame)

    _disp_count[0] += 1
    if _disp_count[0] % FPS == 0:
        print(f"Frame: {_disp_count[0]} / {FRAME_COUNT}   ", end="\r", flush=True)

    cv2.imshow(_WIN_NAME, frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        _save_win_config()
        escape[0] = True
    if cv2.getWindowProperty(_WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
        _save_win_config()
        escape[0] = True

def black_frame():
    global byte_array
    _save_win_config()
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


with open(OUTPUT_FILE, "wb") as f:
    for value in hex_values:
        f.write(bytes([value]))  # write each as a single byte

frames = []
byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

cv2.namedWindow(_WIN_NAME, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_FREERATIO)
_cfg = _load_win_config()
_win_w = _cfg['w'] if _cfg else 1400
_win_h = _cfg['h'] if _cfg else 600
cv2.resizeWindow(_WIN_NAME, _win_w, _win_h)
cv2.imshow(_WIN_NAME, np.zeros((_FRAME_H, _FRAME_W, 3), dtype=np.uint8))
cv2.waitKey(1)

with open(OUTPUT_FILE, "ab") as f:
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