import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
import os
import threading
import queue

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PATTERNS_DIR = os.path.join(SCRIPT_DIR, 'patterns')

PATTERNS = [
    ("confetti",       "Random green sparkle scatter"),
    ("deepam",         "Deepam lamp effect"),
    ("falling_dots",   "Rainbow columns falling downward"),
    ("festival",       "Festival colour burst"),
    ("golden_confetti","Gold confetti sparkle"),
    ("golden_sweep",   "Gold sweep across panels"),
    ("heartbeat",      "Crimson→amber pulse wave across panels"),
    ("hor_lines",      "Green→white horizontal lines sweeping right"),
    ("horiz_chase",    "Horizontal chase lights"),
    ("kovil_glow",     "Warm white & forest green panels with gold cross-fade"),
    ("rainy",          "Green/white rainfall — alternating panel directions"),
    ("sparkle",        "Sparkle effect"),
    ("story",          "Scripted white/green panel wipe"),
    ("tetris",         "4×4 blocks falling and stacking"),
    ("waterfall",      "Waterfall effect"),
]

_DARK  = "#1e1e1e"
_MID   = "#2b2b2b"
_PANEL = "#252525"
_FG    = "#e0e0e0"
_GREEN = "#00cc44"
_DIM   = "#888888"


class MasterTolCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Master .tol Creator")
        self.root.resizable(True, True)
        self.root.configure(bg=_DARK)

        self.checks         = {}
        self.log_queue      = queue.Queue()
        self.running        = False
        self.current_proc   = None
        self._preview_procs = {}   # name -> Popen
        self._preview_btns  = {}   # name -> tk.Button

        self._build_ui()
        self._poll_log()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # header
        hdr = tk.Frame(self.root, bg=_DARK)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Kovil LED — Master .tol Creator",
                 font=("Segoe UI", 14, "bold"), fg=_GREEN, bg=_DARK
                 ).pack(padx=10, pady=6)

        # two-column body
        body = tk.Frame(self.root, bg=_DARK)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        body.columnconfigure(0, weight=0, minsize=300)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

    # ── left panel: pattern list with play buttons ────────────────────────

    def _build_left(self, parent):
        frame = tk.LabelFrame(parent, text=" Preview Patterns ",
                              font=("Segoe UI", 10), fg=_FG,
                              bg=_PANEL, labelanchor="n")
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0, bg=_PANEL)
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")

        inner = tk.Frame(canvas, bg=_PANEL)
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        inner.bind("<Configure>",
                   lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(win_id, width=e.width))

        # mouse-wheel scroll
        def _scroll(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _scroll)

        for name, desc in PATTERNS:
            row = tk.Frame(inner, bg=_PANEL)
            row.pack(fill="x", padx=6, pady=3)

            btn = tk.Button(
                row, text="▶", width=3,
                font=("Segoe UI", 10),
                bg="#1a5c2e", fg="white",
                activebackground="#007733",
                relief="flat", cursor="hand2",
                command=lambda n=name: self._toggle_preview(n)
            )
            btn.pack(side="right", padx=(6, 0))
            self._preview_btns[name] = btn

            tk.Label(row, text=name,
                     font=("Consolas", 9, "bold"),
                     fg=_FG, bg=_PANEL, width=15, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=desc,
                     font=("Segoe UI", 8), fg=_DIM, bg=_PANEL, anchor="w"
                     ).pack(side="left", fill="x", expand=True)

    # ── right panel: checkboxes + generate ───────────────────────────────

    def _build_right(self, parent):
        right = tk.Frame(parent, bg=_DARK)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        # checkbox section
        sel = tk.LabelFrame(right, text=" Select Patterns to Generate ",
                            font=("Segoe UI", 10), fg=_FG, bg=_MID, labelanchor="n")
        sel.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        bar = tk.Frame(sel, bg=_MID)
        bar.pack(anchor="w", padx=6, pady=(4, 0))
        tk.Button(bar, text="Select All",   command=self._select_all,
                  width=12, bg="#333", fg=_FG, relief="flat"
                  ).pack(side="left", padx=2)
        tk.Button(bar, text="Deselect All", command=self._deselect_all,
                  width=12, bg="#333", fg=_FG, relief="flat"
                  ).pack(side="left", padx=2)

        grid = tk.Frame(sel, bg=_MID)
        grid.pack(fill="both", padx=6, pady=5)

        cols = 2
        for i, (name, desc) in enumerate(PATTERNS):
            var = tk.BooleanVar(value=True)
            self.checks[name] = var
            r, c = divmod(i, cols)
            tk.Checkbutton(grid, text=name, variable=var,
                           anchor="w", width=18,
                           font=("Consolas", 9),
                           bg=_MID, fg=_FG,
                           selectcolor=_MID,
                           activebackground=_MID, activeforeground=_FG
                           ).grid(row=r, column=c * 2, sticky="w", padx=(4, 0))
            tk.Label(grid, text=f"— {desc}",
                     font=("Segoe UI", 8), fg=_DIM, bg=_MID, anchor="w"
                     ).grid(row=r, column=c * 2 + 1, sticky="w", padx=(0, 12))

        # action buttons
        btn_row = tk.Frame(right, bg=_DARK)
        btn_row.grid(row=1, column=0, sticky="ew", pady=4)

        self.run_tol_btn = tk.Button(
            btn_row, text="▶  Generate .tol",
            font=("Segoe UI", 11, "bold"),
            bg="#005522", fg="white", activebackground="#007733",
            relief="flat", cursor="hand2",
            command=self._start_tol, width=18
        )
        self.run_tol_btn.pack(side="left", padx=(0, 6))

        self.run_avi_btn = tk.Button(
            btn_row, text="▶  Generate .avi",
            font=("Segoe UI", 11, "bold"),
            bg="#00555a", fg="white", activebackground="#007a82",
            relief="flat", cursor="hand2",
            command=self._start_avi, width=18
        )
        self.run_avi_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(
            btn_row, text="■  Stop",
            font=("Segoe UI", 11),
            bg="#880000", fg="white", activebackground="#aa0000",
            relief="flat", cursor="hand2",
            command=self._stop_generation, width=10, state="disabled"
        )
        self.stop_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(btn_row, textvariable=self.status_var,
                 font=("Segoe UI", 9), fg=_DIM, bg=_DARK
                 ).pack(side="left", padx=12)

        # progress bar
        self.progress = ttk.Progressbar(right, mode="determinate")
        self.progress.grid(row=2, column=0, sticky="ew", pady=(0, 4))

        # log
        log_frame = tk.LabelFrame(right, text=" Output ",
                                  font=("Segoe UI", 10), fg=_FG, bg=_MID)
        log_frame.grid(row=3, column=0, sticky="nsew")

        self.log = scrolledtext.ScrolledText(
            log_frame, height=14, font=("Consolas", 9),
            bg="#111111", fg="#cccccc", insertbackground="white",
            state="disabled"
        )
        self.log.pack(fill="both", expand=True, padx=4, pady=4)
        self.log.tag_config("ok",   foreground="#00cc44")
        self.log.tag_config("err",  foreground="#ff4444")
        self.log.tag_config("info", foreground="#aaaaaa")
        self.log.tag_config("head", foreground="#ffcc00")

    # ── preview ──────────────────────────────────────────────────────────────

    def _toggle_preview(self, name):
        proc = self._preview_procs.get(name)
        if proc and proc.poll() is None:
            # clicking the stop button for the currently playing animation
            proc.terminate()
            self._preview_procs.pop(name, None)
            self._set_btn_play(name)
        else:
            # stop any other running previews first
            for other_name, other_proc in list(self._preview_procs.items()):
                if other_proc.poll() is None:
                    other_proc.terminate()
                self._preview_procs.pop(other_name, None)
                self._set_btn_play(other_name)

            script = os.path.join(PATTERNS_DIR, f"{name}.py")
            if not os.path.exists(script):
                return
            proc = subprocess.Popen([sys.executable, script], cwd=PATTERNS_DIR)
            self._preview_procs[name] = proc
            self._set_btn_stop(name)
            threading.Thread(target=self._watch_preview,
                             args=(name, proc), daemon=True).start()

    def _watch_preview(self, name, proc):
        proc.wait()
        self.root.after(0, lambda: self._preview_ended(name, proc))

    def _preview_ended(self, name, proc):
        if self._preview_procs.get(name) is proc:
            self._preview_procs.pop(name, None)
            self._set_btn_play(name)

    def _set_btn_play(self, name):
        btn = self._preview_btns.get(name)
        if btn:
            btn.config(text="▶", bg="#1a5c2e", activebackground="#007733")

    def _set_btn_stop(self, name):
        btn = self._preview_btns.get(name)
        if btn:
            btn.config(text="■", bg="#7a0000", activebackground="#aa0000")

    # ── helpers ──────────────────────────────────────────────────────────────

    def _select_all(self):
        for var in self.checks.values():
            var.set(True)

    def _deselect_all(self):
        for var in self.checks.values():
            var.set(False)

    def _log(self, text, tag="info"):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n", tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _poll_log(self):
        try:
            while True:
                msg, tag = self.log_queue.get_nowait()
                self._log(msg, tag)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_log)

    # ── generation ───────────────────────────────────────────────────────────

    def _start_tol(self):
        self._start_generation("--headless")

    def _start_avi(self):
        self._start_generation("--avi")

    def _start_generation(self, flag):
        selected = [name for name, var in self.checks.items() if var.get()]
        if not selected:
            self._log("No patterns selected.", "err")
            return

        self.running = True
        self.run_tol_btn.config(state="disabled")
        self.run_avi_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress["value"] = 0
        self.progress["maximum"] = len(selected)

        threading.Thread(target=self._run_patterns,
                         args=(selected, flag), daemon=True).start()

    def _stop_generation(self):
        self.running = False
        if self.current_proc and self.current_proc.poll() is None:
            self.current_proc.terminate()
            self.log_queue.put(("⚠  Generation stopped by user.", "err"))
        self._generation_done()

    def _run_patterns(self, selected, flag):
        python = sys.executable
        total  = len(selected)
        done   = 0
        failed = []
        ext    = ".tol" if flag == "--headless" else ".avi"

        self.log_queue.put((f"Starting generation of {total} pattern(s) [{ext}]…", "head"))

        for name in selected:
            if not self.running:
                break

            script = os.path.join(PATTERNS_DIR, f"{name}.py")
            if not os.path.exists(script):
                self.log_queue.put((f"  [SKIP] {name}.py not found", "err"))
                done += 1
                self.root.after(0, lambda d=done: self.progress.config(value=d))
                continue

            self.log_queue.put((f"\n▶ {name} …", "head"))
            self.root.after(0, lambda n=name: self.status_var.set(f"Generating: {n}"))

            try:
                proc = subprocess.Popen(
                    [python, script, flag],
                    cwd=PATTERNS_DIR,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                self.current_proc = proc

                for line in proc.stdout:
                    line = line.rstrip()
                    if not line:
                        continue
                    tag = "ok" if ("✅" in line or "Saved" in line or "Done" in line) else "info"
                    self.log_queue.put((f"   {line}", tag))

                proc.wait()
                if proc.returncode == 0:
                    self.log_queue.put((f"  ✅ {name}{ext} saved", "ok"))
                else:
                    self.log_queue.put((f"  ✗ {name} exited with code {proc.returncode}", "err"))
                    failed.append(name)

            except Exception as e:
                self.log_queue.put((f"  ✗ {name}: {e}", "err"))
                failed.append(name)

            done += 1
            self.root.after(0, lambda d=done: self.progress.config(value=d))

        self.log_queue.put(("\n─── Summary ───────────────────────", "head"))
        succeeded = done - len(failed) - (total - done if not self.running else 0)
        self.log_queue.put((f"  Generated : {succeeded}/{total}",
                            "ok" if succeeded == total else "info"))
        if failed:
            self.log_queue.put(("  Failed    : " + ", ".join(failed), "err"))
        if not self.running:
            self.log_queue.put(("  (stopped early)", "err"))

        self.root.after(0, self._generation_done)

    def _generation_done(self):
        self.running      = False
        self.current_proc = None
        self.run_tol_btn.config(state="normal")
        self.run_avi_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Done.")


def main():
    root = tk.Tk()
    root.minsize(980, 580)
    app = MasterTolCreator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
