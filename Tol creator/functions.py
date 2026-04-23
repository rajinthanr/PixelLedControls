import atexit
import random
import cv2
import numpy as np
import time
import sys
import os
import json

_HEADLESS = '--headless' in sys.argv
_AVI_MODE = '--avi'      in sys.argv

_script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
_base_dir    = os.path.dirname(os.path.abspath(__file__))

_tol_dir = os.path.normpath(os.path.join(_base_dir, '..', 'Tol files'))
_avi_dir = os.path.normpath(os.path.join(_base_dir, '..', 'Avi files'))
OUTPUT_FILE = os.path.join(_tol_dir, _script_name + '.tol')
AVI_FILE    = os.path.join(_avi_dir,  _script_name + '.avi')

_WIN_NAME   = "RGB Animation"
_WIN_CONFIG = os.path.join(_base_dir, '.window_config.json')

def _load_win_config():
    if os.path.exists(_WIN_CONFIG):
        with open(_WIN_CONFIG) as f:
            return json.load(f)
    return None

def _save_win_config():
    if _HEADLESS or _AVI_MODE:
        return
    try:
        rect = cv2.getWindowImageRect(_WIN_NAME)
        if rect[2] > 0 and rect[3] > 0:
            with open(_WIN_CONFIG, 'w') as f:
                json.dump({'x': rect[0], 'y': rect[1], 'w': rect[2], 'h': rect[3]}, f)
    except Exception:
        pass

HEIGHT          = 50
SIDES           = 7
STRIPS_PER_SIDE = 16
WIDTH           = SIDES * STRIPS_PER_SIDE   # 112

FPS          = 30
DURATION     = 60
LEAD_FRAMES  = 0    # no black lead-in
TAIL_FRAMES  = 30   # 1 s black tail
FRAME_COUNT  = FPS * DURATION + LEAD_FRAMES + TAIL_FRAMES
DROP_COUNT   = 400

_DOT_R   = 3
_PX      = int(_DOT_R * 2 * 2.5)
_GAP     = 10
_LABEL_H = 24
_PANEL_W = STRIPS_PER_SIDE * _PX
_FRAME_W = SIDES * _PANEL_W + (SIDES - 1) * _GAP
_FRAME_H = HEIGHT * _PX + _LABEL_H
_BTN_H   = 40
_TOTAL_H = _FRAME_H + _BTN_H

# --- shared mutable state ---
escape         = [False]
_disp_count    = [0]
_pending_save  = [False]
_pending_avi   = [False]
_save_flash    = [0]
_avi_flash     = [0]
_save_requested = [False]
_avi_requested  = [False]
_avi_writer     = [None]

def _on_mouse(event, x, y, _flags, _param):
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    by0, by1 = _FRAME_H + 5, _TOTAL_H - 5
    if not (by0 <= y <= by1):
        return
    if _FRAME_W - 130 <= x <= _FRAME_W - 10:
        _save_requested[0] = True
    elif _FRAME_W - 270 <= x <= _FRAME_W - 140:
        _avi_requested[0] = True

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
        return
    with open(OUTPUT_FILE, "ab") as f:
        for row in byte_array:
            for pixel in row:
                f.write(bytes([int(min(255, max(0, p))) for p in pixel]))

def _render_anim_canvas():
    rgb_array   = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
    anim_canvas = np.zeros((_FRAME_H, _FRAME_W, 3), dtype=np.uint8)
    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        for y in range(HEIGHT):
            for x in range(STRIPS_PER_SIDE):
                color = rgb_array[y, side * STRIPS_PER_SIDE + x]
                if np.any(color):
                    cx = x_off + x * _PX + _PX // 2
                    cy = _LABEL_H + y * _PX + _PX // 2
                    cv2.circle(anim_canvas, (cx, cy), _DOT_R, color.tolist(), -1)
    anim_canvas = cv2.cvtColor(anim_canvas, cv2.COLOR_RGB2BGR)
    for side in range(SIDES):
        x_off = side * (_PANEL_W + _GAP)
        label = f"Side {side + 1}"
        (tw, _), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
        cv2.putText(anim_canvas, label,
                    (x_off + (_PANEL_W - tw) // 2, _LABEL_H - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 1, cv2.LINE_AA)
        if side < SIDES - 1:
            sep_x = x_off + _PANEL_W + _GAP // 2
            cv2.line(anim_canvas, (sep_x, 0), (sep_x, _FRAME_H), (50, 50, 50), 2)
    return anim_canvas

def display_frame():
    global pre_time
    pre_time = time.time()

    if _HEADLESS:
        _disp_count[0] += 1
        if _disp_count[0] % FPS == 0:
            print(f"  generating .tol: {_disp_count[0]} / {FRAME_COUNT}", end="\r", flush=True)
        return

    anim_canvas = _render_anim_canvas()
    _disp_count[0] += 1

    if _AVI_MODE:
        if _avi_writer[0] is not None:
            raw = np.array(byte_array, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
            _avi_writer[0].write(cv2.cvtColor(raw, cv2.COLOR_RGB2BGR))
        if _disp_count[0] % FPS == 0:
            print(f"  rendering .avi: {_disp_count[0]} / {FRAME_COUNT}", end="\r", flush=True)
        return

    # --- GUI mode ---
    canvas = np.zeros((_TOTAL_H, _FRAME_W, 3), dtype=np.uint8)
    canvas[:_FRAME_H] = anim_canvas

    # button bar background
    cv2.rectangle(canvas, (0, _FRAME_H), (_FRAME_W, _TOTAL_H), (28, 28, 28), -1)
    cv2.putText(canvas, f"Frame {_disp_count[0]} / {FRAME_COUNT}",
                (10, _FRAME_H + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 140, 140), 1, cv2.LINE_AA)

    # Save .avi button
    if _avi_flash[0] > 0:
        avi_col, avi_txt = (30, 140, 30), "Rendering..."
        _avi_flash[0] -= 1
    else:
        avi_col, avi_txt = (0, 130, 110), "Save .avi  [A]"
    cv2.rectangle(canvas, (_FRAME_W - 270, _FRAME_H + 5), (_FRAME_W - 140, _TOTAL_H - 5), avi_col, -1)
    (tw, _), _ = cv2.getTextSize(avi_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.putText(canvas, avi_txt,
                (_FRAME_W - 270 + (120 - tw) // 2, _FRAME_H + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    # Save .tol button
    if _save_flash[0] > 0:
        tol_col, tol_txt = (30, 140, 30), "Generating..."
        _save_flash[0] -= 1
    else:
        tol_col, tol_txt = (40, 100, 200), "Save .tol  [S]"
    cv2.rectangle(canvas, (_FRAME_W - 130, _FRAME_H + 5), (_FRAME_W - 10, _TOTAL_H - 5), tol_col, -1)
    (tw, _), _ = cv2.getTextSize(tol_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
    cv2.putText(canvas, tol_txt,
                (_FRAME_W - 130 + (120 - tw) // 2, _FRAME_H + 27),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    if _disp_count[0] % 60 == 0:
        _save_win_config()

    if _save_requested[0]:
        _save_requested[0] = False
        _pending_save[0]   = True
        _save_flash[0]     = FPS
        escape[0]          = True
    if _avi_requested[0]:
        _avi_requested[0] = False
        _pending_avi[0]   = True
        _avi_flash[0]     = FPS
        escape[0]         = True

    cv2.imshow(_WIN_NAME, canvas)
    key = cv2.waitKey(1) & 0xFF
    if key in (27, ord('q')):
        _save_win_config()
        escape[0] = True
    elif key == ord('s'):
        _pending_save[0] = True
        _save_flash[0]   = FPS
        escape[0]        = True
    elif key == ord('a'):
        _pending_avi[0] = True
        _avi_flash[0]   = FPS
        escape[0]       = True
    if cv2.getWindowProperty(_WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
        _save_win_config()
        escape[0] = True

def fade_out_and_close():
    black_frame()
    for _ in range(TAIL_FRAMES):
        save_frame()
        display_frame()
    cv2.destroyAllWindows()
    if _HEADLESS:
        print(f"\n✅  Saved → {OUTPUT_FILE}")

def black_frame():
    global byte_array
    _save_win_config()
    byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

# ---------- atexit ----------

def _on_exit():
    # Release AVI writer if in AVI render mode
    if _AVI_MODE:
        if _avi_writer[0] is not None:
            _avi_writer[0].release()
            print(f"\n✅  Saved → {AVI_FILE}")
        return
    if _HEADLESS:
        return
    # GUI mode: spawn requested render jobs
    import subprocess
    if _pending_save[0]:
        print(f"\n⚙️  Rendering '{_script_name}.tol' — please wait...")
        r = subprocess.run([sys.executable, sys.argv[0], '--headless'])
        print(f"✅  Saved → {OUTPUT_FILE}" if r.returncode == 0 else "❌  .tol render failed")
    if _pending_avi[0]:
        print(f"\n⚙️  Rendering '{_script_name}.avi' — please wait...")
        r = subprocess.run([sys.executable, sys.argv[0], '--avi'])
        print(f"✅  Saved → {AVI_FILE}" if r.returncode == 0 else "❌  .avi render failed")

atexit.register(_on_exit)

# ---------- init ----------

byte_array = [[[0 for _ in range(3)] for _ in range(WIDTH)] for _ in range(HEIGHT)]

if _HEADLESS:
    hdr = bytearray(14)
    hdr[1:4]  = FRAME_COUNT.to_bytes(3, 'big')
    hdr[4:6]  = HEIGHT.to_bytes(2, 'big')
    hdr[6:8]  = WIDTH.to_bytes(2, 'big')
    hdr[8:10]  = (10).to_bytes(2, 'big')
    hdr[10:12] = (10).to_bytes(2, 'big')
    hdr[12]    = 0x03
    hdr[13]    = 0x01
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(hdr)

elif _AVI_MODE:
    os.makedirs(_avi_dir, exist_ok=True)
    _fourcc = cv2.VideoWriter_fourcc(*'XVID')
    _avi_writer[0] = cv2.VideoWriter(AVI_FILE, _fourcc, FPS, (WIDTH, HEIGHT))

else:
    cv2.namedWindow(_WIN_NAME, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_FREERATIO)
    cv2.setMouseCallback(_WIN_NAME, _on_mouse)
    _cfg   = _load_win_config()
    _win_w = _cfg['w'] if _cfg else 1400
    _win_h = _cfg['h'] if _cfg else 640
    cv2.resizeWindow(_WIN_NAME, _win_w, _win_h)
    if _cfg and 'x' in _cfg and 'y' in _cfg:
        cv2.moveWindow(_WIN_NAME, _cfg['x'], _cfg['y'])
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
