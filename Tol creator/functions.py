import atexit
import random
import cv2
import numpy as np
import time
import sys
import os
import json

_HEADLESS = '--headless' in sys.argv

_script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
_tol_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), '..', 'Tol files'))
OUTPUT_FILE = os.path.join(_tol_dir, _script_name + '.tol')

_WIN_NAME   = "RGB Animation"
_WIN_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.window_config.json')

def _load_win_config():
    if os.path.exists(_WIN_CONFIG):
        with open(_WIN_CONFIG) as f:
            return json.load(f)
    return None

def _save_win_config():
    if _HEADLESS:
        return
    try:
        rect = cv2.getWindowImageRect(_WIN_NAME)
        if rect[2] > 0 and rect[3] > 0:
            with open(_WIN_CONFIG, 'w') as f:
                json.dump({'w': rect[2], 'h': rect[3]}, f)
    except Exception:
        pass

HEIGHT          = 50
SIDES           = 7
STRIPS_PER_SIDE = 16
WIDTH           = SIDES * STRIPS_PER_SIDE   # 112

FPS         = 30
DURATION    = 30
FRAME_COUNT = FPS * DURATION + 30 + 30
DROP_COUNT  = 400

_DOT_R   = 3
_PX      = int(_DOT_R * 2 * 2.5)           # cell pitch 15 px
_GAP     = 10
_LABEL_H = 24
_PANEL_W = STRIPS_PER_SIDE * _PX
_FRAME_W = SIDES * _PANEL_W + (SIDES - 1) * _GAP
_FRAME_H = HEIGHT * _PX + _LABEL_H
_BTN_H   = 40
_TOTAL_H = _FRAME_H + _BTN_H

# --- shared mutable state ---
escape        = [False]
_disp_count   = [0]
_pending_save = [False]    # set True when user clicks Save — atexit spawns headless run
_save_flash   = [0]        # countdown for button feedback
_write_count  = [0]        # counts save_frame() calls; used for fade-in scaling

_save_requested = [False]  # internal: button click detected this frame

def _on_mouse(event, x, y, _flags, _param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if (_FRAME_W - 130 <= x <= _FRAME_W - 10 and
                _FRAME_H + 5 <= y <= _TOTAL_H - 5):
            _save_requested[0] = True

current_frame = 0
pre_time      = 0
pTloop        = 0
count         = 0

def delay(seconds):
    start = time.time()
    while time.time() - start < seconds:
        pass

def fade_pixels(byte_array, fade_value):
    for y in range(len(byte_array)):
        for x in range(len(byte_array[y])):
            for c in range(3):
                byte_array[y][x][c] = max(0, byte_array[y][x][c] - fade_value)

# ---------- frame I/O ----------

def save_frame():
    if not _HEADLESS:
        return   # preview only — headless re-run does the real write
    _write_count[0] += 1
    # linear fade-in over the first 30 frames written
    scale = min(1.0, _write_count[0] / 30)
    with open(OUTPUT_FILE, "ab") as f:
        for row in byte_array:
            for pixel in row:
                f.write(bytes([int(min(255, max(0, p)) * scale) for p in pixel]))

def display_frame():
    global pre_time
    pre_time = time.time()

    if _HEADLESS:
        _disp_count[0] += 1
        if _disp_count[0] % FPS == 0:
            print(f"  generating: {_disp_count[0]} / {FRAME_COUNT}", end="\r", flush=True)
        return

    rgb_array = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    canvas    = np.zeros((_TOTAL_H, _FRAME_W, 3), dtype=np.uint8)

    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        for y in range(HEIGHT):
            for x in range(STRIPS_PER_SIDE):
                color = rgb_array[y, side * STRIPS_PER_SIDE + x]
                if np.any(color):
                    cx = x_off + x * _PX + _PX // 2
                    cy = _LABEL_H + y * _PX + _PX // 2
                    cv2.circle(canvas, (cx, cy), _DOT_R, color.tolist(), -1)

    canvas = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)

    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        label = f"Side {side + 1}"
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(canvas, label,
                    (x_off + (_PANEL_W - tw) // 2, _LABEL_H - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1, cv2.LINE_AA)
        if side < SIDES - 1:
            sep_x = x_off + _PANEL_W + _GAP // 2
            cv2.line(canvas, (sep_x, 0), (sep_x, _FRAME_H), (50, 50, 50), 2)

    # button bar
    cv2.rectangle(canvas, (0, _FRAME_H), (_FRAME_W, _TOTAL_H), (28, 28, 28), -1)
    cv2.putText(canvas, f"Frame {_disp_count[0]} / {FRAME_COUNT}",
                (10, _FRAME_H + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 140, 140), 1, cv2.LINE_AA)

    if _save_flash[0] > 0:
        btn_col  = (30, 140, 30)
        btn_text = "Generating..."
        _save_flash[0] -= 1
    else:
        btn_col  = (40, 100, 200)
        btn_text = "Save .tol  [S]"

    cv2.rectangle(canvas,
                  (_FRAME_W - 130, _FRAME_H + 5),
                  (_FRAME_W - 10,  _TOTAL_H  - 5),
                  btn_col, -1)
    (tw, _), _ = cv2.getTextSize(btn_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.putText(canvas, btn_text,
                (_FRAME_W - 130 + (120 - tw) // 2, _FRAME_H + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    _disp_count[0] += 1

    if _save_requested[0]:
        _save_requested[0] = False
        _pending_save[0]   = True
        _save_flash[0]     = FPS
        escape[0]          = True   # stop animation; atexit will spawn headless run

    cv2.imshow(_WIN_NAME, canvas)
    key = cv2.waitKey(1) & 0xFF
    if key in (27, ord('q')):
        _save_win_config()
        escape[0] = True
    elif key == ord('s'):
        _pending_save[0] = True
        _save_flash[0]   = FPS
        escape[0]        = True
    if cv2.getWindowProperty(_WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
        _save_win_config()
        escape[0] = True

def fade_out_and_close():
    """30-frame gradual fade to black, then close window. Call at the end of every pattern."""
    import copy as _copy
    _last = _copy.deepcopy(byte_array)
    for _step in range(30):
        _t = 1.0 - (_step + 1) / 30
        for _y in range(HEIGHT):
            for _x in range(WIDTH):
                byte_array[_y][_x] = [int(_last[_y][_x][_c] * _t) for _c in range(3)]
        save_frame()
        display_frame()
    black_frame()
    cv2.destroyAllWindows()
    if _HEADLESS:
        print(f"✅ Saved → {OUTPUT_FILE}")

def black_frame():
    global byte_array
    _save_win_config()
    byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

# ---------- atexit: headless re-run ----------

def _on_exit():
    if not _pending_save[0] or _HEADLESS:
        return
    import subprocess
    print(f"\n⚙️  Rendering '{_script_name}.tol' — please wait...")
    result = subprocess.run([sys.executable, sys.argv[0], '--headless'])
    if result.returncode == 0:
        print(f"✅  Saved → {OUTPUT_FILE}")
    else:
        print("❌  Render failed")

atexit.register(_on_exit)

# ---------- init ----------

byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

if _HEADLESS:
    # write .tol header + 30 lead-in black frames up front
    hdr = bytearray(14)
    hdr[1:4]  = FRAME_COUNT.to_bytes(3, 'big')
    hdr[4:6]  = HEIGHT.to_bytes(2, 'big')
    hdr[6:8]  = WIDTH.to_bytes(2, 'big')
    hdr[8:10]  = (10).to_bytes(2, 'big')   # frame delay ms — matches LEDEdit sample files
    hdr[10:12] = (10).to_bytes(2, 'big')   # duplicate of bytes 8-9
    hdr[12]    = 0x03                       # RGB colour channels
    hdr[13]    = 0x01                       # loop mode
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(hdr)
    _black_row = bytes(WIDTH * 3)
    with open(OUTPUT_FILE, 'ab') as f:
        for _ in range(30):
            for _ in range(HEIGHT):
                f.write(_black_row)
else:
    cv2.namedWindow(_WIN_NAME, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_FREERATIO)
    cv2.setMouseCallback(_WIN_NAME, _on_mouse)
    _cfg   = _load_win_config()
    _win_w = _cfg['w'] if _cfg else 1400
    _win_h = _cfg['h'] if _cfg else 640
    cv2.resizeWindow(_WIN_NAME, _win_w, _win_h)
    cv2.imshow(_WIN_NAME, np.zeros((_TOTAL_H, _FRAME_W, 3), dtype=np.uint8))
    cv2.waitKey(1)

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0: return v, t, p
    if i == 1: return q, v, p
    if i == 2: return p, v, t
    if i == 3: return p, q, v
    if i == 4: return t, p, v
    if i == 5: return v, p, q
