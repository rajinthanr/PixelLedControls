"""TOL File Viewer — play .tol animation files with the 7-panel LED visualiser."""
import os
import time
import base64
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2

# ── Grid constants (match functions.py) ──────────────────────────────────────
HEIGHT          = 50
SIDES           = 7
STRIPS_PER_SIDE = 16
WIDTH           = SIDES * STRIPS_PER_SIDE   # 112

_DOT_R   = 3
_PX      = 15    # cell pitch px
_GAP     = 10    # gap between side panels px
_LABEL_H = 24    # label row height px

_PANEL_W = STRIPS_PER_SIDE * _PX                    # 240
_FULL_W  = SIDES * _PANEL_W + (SIDES - 1) * _GAP   # 1740
_FULL_H  = HEIGHT * _PX + _LABEL_H                  # 774

TOL_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Tol files')
)

# Pre-compute circular dot mask tiled to cover one panel ──────────────────────
_cell = np.zeros((_PX, _PX), dtype=bool)
_c    = _PX // 2
for _dy in range(_PX):
    for _dx in range(_PX):
        _cell[_dy, _dx] = (_dy - _c) ** 2 + (_dx - _c) ** 2 <= _DOT_R ** 2
_DOT_MASK = np.tile(_cell, (HEIGHT, STRIPS_PER_SIDE))  # (HEIGHT*_PX) × _PANEL_W


# ── .tol parser ───────────────────────────────────────────────────────────────
def load_tol(path):
    with open(path, 'rb') as f:
        data = f.read()
    n_frames = int.from_bytes(data[1:4], 'big')
    h        = int.from_bytes(data[4:6], 'big')
    w        = int.from_bytes(data[6:8], 'big')
    sz       = h * w * 3
    frames   = []
    for i in range(n_frames):
        off   = 14 + i * sz
        chunk = data[off:off + sz]
        if len(chunk) < sz:
            break
        frames.append(np.frombuffer(chunk, dtype=np.uint8).reshape(h, w, 3).copy())
    return frames


# ── Renderer ──────────────────────────────────────────────────────────────────
def render_frame(frame_rgb):
    """Convert a HEIGHT×WIDTH×3 RGB frame to a BGR visualiser image."""
    canvas = np.zeros((_FULL_H, _FULL_W, 3), dtype=np.uint8)
    for side in range(SIDES):
        x_off  = side * (_PANEL_W + _GAP)
        panel  = frame_rgb[:, side * STRIPS_PER_SIDE:(side + 1) * STRIPS_PER_SIDE]
        scaled = np.repeat(np.repeat(panel, _PX, axis=0), _PX, axis=1)
        scaled[~_DOT_MASK] = 0
        canvas[_LABEL_H:_LABEL_H + HEIGHT * _PX, x_off:x_off + _PANEL_W] = scaled

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
            cv2.line(canvas, (sep_x, 0), (sep_x, _FULL_H), (50, 50, 50), 2)
    return canvas  # BGR


def _bgr_to_photo(bgr, max_w, max_h):
    scale = min(max_w / _FULL_W, max_h / _FULL_H)
    nw    = max(1, int(_FULL_W * scale))
    nh    = max(1, int(_FULL_H * scale))
    out   = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode('.png', out, [cv2.IMWRITE_PNG_COMPRESSION, 0])
    return tk.PhotoImage(data=base64.b64encode(buf.tobytes()))


# ── App ───────────────────────────────────────────────────────────────────────
class TolViewer:
    FPS_MIN, FPS_MAX = 1, 60

    def __init__(self, root):
        self.root     = root
        self.root.title("TOL File Viewer")
        self.root.configure(bg='#1a1a1a')
        self.root.geometry('1400x680')
        self.root.minsize(600, 320)

        self._frames     = []
        self._cur        = 0
        self._playing    = False
        self._fps        = 30
        self._job        = None
        self._photo      = None   # prevent GC
        self._resize_job = None

        self._build_ui()
        self.root.after(120, self._refresh_files)

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        dark   = '#1a1a1a'
        bar    = '#252525'
        btn    = '#363636'
        fg     = '#e0e0e0'
        accent = '#2d6db5'

        # top bar
        top = tk.Frame(self.root, bg=bar, height=46)
        top.pack(fill='x')
        top.pack_propagate(False)

        tk.Label(top, text='Pattern:', bg=bar, fg=fg,
                 font=('TkDefaultFont', 10)).pack(side='left', padx=(12, 4), pady=12)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',
                        fieldbackground=btn, background=btn,
                        foreground=fg, selectbackground=btn, selectforeground=fg)
        style.map('TCombobox',
                  fieldbackground=[('readonly', btn)],
                  foreground=[('readonly', fg)])

        self._file_var = tk.StringVar()
        self._combo    = ttk.Combobox(top, textvariable=self._file_var,
                                       state='readonly', width=34,
                                       font=('TkDefaultFont', 10))
        self._combo.pack(side='left', padx=4)
        self._combo.bind('<<ComboboxSelected>>', lambda _: self._load_selected())

        tk.Button(top, text='↺', command=self._refresh_files,
                  bg=btn, fg=fg, relief='flat', padx=8,
                  font=('TkDefaultFont', 11), cursor='hand2',
                  activebackground='#484848', activeforeground=fg
                  ).pack(side='left', padx=(2, 0))

        self._status = tk.Label(top, text='Select a pattern', bg=bar, fg='#666',
                                 font=('TkDefaultFont', 9))
        self._status.pack(side='left', padx=12)

        # canvas
        self._canvas_frame = tk.Frame(self.root, bg=dark)
        self._canvas_frame.pack(fill='both', expand=True)

        self._img_label = tk.Label(self._canvas_frame, bg=dark)
        self._img_label.place(relx=0.5, rely=0.5, anchor='center')
        self._canvas_frame.bind('<Configure>', self._on_resize)

        # bottom bar
        bot = tk.Frame(self.root, bg=bar, height=50)
        bot.pack(fill='x')
        bot.pack_propagate(False)

        # playback buttons
        pb = tk.Frame(bot, bg=bar)
        pb.pack(side='left', padx=10, pady=8)

        def mk(parent, text, cmd, width=2, bg=btn, abg='#484848', **kw):
            return tk.Button(parent, text=text, command=cmd, width=width,
                             bg=bg, fg=fg, relief='flat', bd=0,
                             font=('TkDefaultFont', 14), cursor='hand2',
                             activebackground=abg, activeforeground=fg, **kw)

        mk(pb, '⏮', self._rewind).pack(side='left', padx=2)
        mk(pb, '⏪', self._step_back).pack(side='left', padx=2)
        self._play_btn = mk(pb, '▶', self._toggle_play, width=3,
                             bg=accent, abg='#3a7fca')
        self._play_btn.pack(side='left', padx=2)
        mk(pb, '⏩', self._step_fwd).pack(side='left', padx=2)

        # frame counter
        self._frame_lbl = tk.Label(bot, text='— / —', bg=bar, fg='#999',
                                    font=('TkDefaultFont', 10))
        self._frame_lbl.pack(side='left', padx=24)

        # FPS control
        fps_f = tk.Frame(bot, bg=bar)
        fps_f.pack(side='right', padx=12, pady=10)

        tk.Label(fps_f, text='FPS', bg=bar, fg=fg,
                 font=('TkDefaultFont', 10)).pack(side='left', padx=(0, 6))

        def fps_btn(text, cmd):
            return tk.Button(fps_f, text=text, command=cmd,
                             bg=btn, fg=fg, relief='flat', width=2, bd=0,
                             font=('TkDefaultFont', 12), cursor='hand2',
                             activebackground='#484848', activeforeground=fg)

        fps_btn('−', self._fps_down).pack(side='left', padx=1)
        self._fps_lbl = tk.Label(fps_f, text=str(self._fps), bg=btn, fg=fg,
                                  font=('TkDefaultFont', 10, 'bold'),
                                  width=4, anchor='center')
        self._fps_lbl.pack(side='left', padx=2)
        fps_btn('+', self._fps_up).pack(side='left', padx=1)

        # keyboard shortcuts
        self.root.bind('<space>',  lambda _: self._toggle_play())
        self.root.bind('<Left>',   lambda _: self._step_back())
        self.root.bind('<Right>',  lambda _: self._step_fwd())
        self.root.bind('<Home>',   lambda _: self._rewind())

    # ── Files ────────────────────────────────────────────────────────────────

    def _refresh_files(self):
        files = (sorted(f for f in os.listdir(TOL_DIR) if f.lower().endswith('.tol'))
                 if os.path.isdir(TOL_DIR) else [])
        self._combo['values'] = files
        if files and not self._file_var.get():
            self._file_var.set(files[0])
            self._load_selected()
        elif not files:
            self._status.config(
                text=f'No .tol files in {os.path.basename(TOL_DIR)}/', fg='#f88')

    def _load_selected(self):
        name = self._file_var.get()
        if not name:
            return
        self._stop()
        self._status.config(text='Loading…', fg='#aaa')
        self.root.update_idletasks()
        path = os.path.join(TOL_DIR, name)
        try:
            self._frames = load_tol(path)
            self._cur    = 0
            kb = os.path.getsize(path) // 1024
            self._status.config(
                text=f'{len(self._frames)} frames · {kb} KB', fg='#8bc34a')
            self._show_frame()
        except Exception as exc:
            self._status.config(text=f'Error: {exc}', fg='#f44336')
            self._frames = []

    # ── Playback ──────────────────────────────────────────────────────────────

    def _toggle_play(self):
        if not self._frames:
            return
        self._playing = not self._playing
        self._play_btn.config(text='⏸' if self._playing else '▶')
        if self._playing:
            self._tick()

    def _stop(self):
        self._playing = False
        self._play_btn.config(text='▶')
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None

    def _tick(self):
        if not self._playing or not self._frames:
            return
        t0           = time.perf_counter()
        self._cur    = (self._cur + 1) % len(self._frames)
        self._show_frame()
        elapsed      = (time.perf_counter() - t0) * 1000
        delay        = max(1, round(1000 / self._fps - elapsed))
        self._job    = self.root.after(delay, self._tick)

    def _rewind(self):
        self._stop()
        self._cur = 0
        self._show_frame()

    def _step_fwd(self):
        if not self._frames:
            return
        self._stop()
        self._cur = min(self._cur + 1, len(self._frames) - 1)
        self._show_frame()

    def _step_back(self):
        if not self._frames:
            return
        self._stop()
        self._cur = max(self._cur - 1, 0)
        self._show_frame()

    # ── FPS ───────────────────────────────────────────────────────────────────

    def _fps_up(self):
        self._fps = min(self.FPS_MAX, self._fps + 1)
        self._fps_lbl.config(text=str(self._fps))

    def _fps_down(self):
        self._fps = max(self.FPS_MIN, self._fps - 1)
        self._fps_lbl.config(text=str(self._fps))

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _on_resize(self, _event):
        if not self._frames:
            return
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(80, self._show_frame)

    def _show_frame(self):
        if not self._frames:
            return
        cw = max(200, self._canvas_frame.winfo_width())
        ch = max(100, self._canvas_frame.winfo_height())
        bgr         = render_frame(self._frames[self._cur])
        self._photo = _bgr_to_photo(bgr, cw, ch)
        self._img_label.config(image=self._photo)
        self._frame_lbl.config(
            text=f'Frame  {self._cur + 1:>4}  /  {len(self._frames)}')


if __name__ == '__main__':
    root = tk.Tk()
    TolViewer(root)
    root.mainloop()
