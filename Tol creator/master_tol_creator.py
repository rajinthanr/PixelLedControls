import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import sys
import os
import threading
import queue

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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


class MasterTolCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Master .tol Creator")
        self.root.resizable(True, True)

        self.checks = {}
        self.log_queue = queue.Queue()
        self.running = False
        self.current_proc = None

        self._build_ui()
        self._poll_log()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- header ---
        hdr = tk.Frame(self.root, bg="#1e1e1e")
        hdr.pack(fill="x")
        tk.Label(
            hdr, text="Kovil LED — Master .tol Creator",
            font=("Segoe UI", 14, "bold"), fg="#00cc44", bg="#1e1e1e"
        ).pack(**pad)

        # --- pattern selection ---
        sel_frame = tk.LabelFrame(self.root, text=" Select Patterns ", font=("Segoe UI", 10))
        sel_frame.pack(fill="both", expand=False, padx=10, pady=(0, 5))

        # select-all / deselect-all bar
        bar = tk.Frame(sel_frame)
        bar.pack(anchor="w", padx=5, pady=(4, 0))
        tk.Button(bar, text="Select All",   command=self._select_all,   width=12).pack(side="left", padx=2)
        tk.Button(bar, text="Deselect All", command=self._deselect_all, width=12).pack(side="left", padx=2)

        grid = tk.Frame(sel_frame)
        grid.pack(fill="both", padx=5, pady=5)

        cols = 3
        for i, (name, desc) in enumerate(PATTERNS):
            var = tk.BooleanVar(value=True)
            self.checks[name] = var
            row, col = divmod(i, cols)
            cb = tk.Checkbutton(
                grid, text=f"{name}",
                variable=var,
                anchor="w", width=18,
                font=("Consolas", 9)
            )
            cb.grid(row=row, column=col * 2, sticky="w", padx=(4, 0))
            tk.Label(
                grid, text=f"— {desc}",
                font=("Segoe UI", 8), fg="#555555", anchor="w"
            ).grid(row=row, column=col * 2 + 1, sticky="w", padx=(0, 12))

        # --- action buttons ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        self.run_btn = tk.Button(
            btn_frame, text="▶  Generate Selected",
            font=("Segoe UI", 11, "bold"),
            bg="#005522", fg="white", activebackground="#007733",
            command=self._start_generation, width=22
        )
        self.run_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = tk.Button(
            btn_frame, text="■  Stop",
            font=("Segoe UI", 11),
            bg="#880000", fg="white", activebackground="#aa0000",
            command=self._stop_generation, width=10, state="disabled"
        )
        self.stop_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(btn_frame, textvariable=self.status_var, font=("Segoe UI", 9), fg="#333333").pack(side="left", padx=12)

        # --- progress bar ---
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=(0, 4))

        # --- log output ---
        log_frame = tk.LabelFrame(self.root, text=" Output ", font=("Segoe UI", 10))
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log = scrolledtext.ScrolledText(
            log_frame, height=14, font=("Consolas", 9),
            bg="#111111", fg="#cccccc", insertbackground="white",
            state="disabled"
        )
        self.log.pack(fill="both", expand=True, padx=4, pady=4)

        self.log.tag_config("ok",    foreground="#00cc44")
        self.log.tag_config("err",   foreground="#ff4444")
        self.log.tag_config("info",  foreground="#aaaaaa")
        self.log.tag_config("head",  foreground="#ffcc00")

    # ------------------------------------------------------------------ helpers

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

    # ------------------------------------------------------------------ generation

    def _start_generation(self):
        selected = [name for name, var in self.checks.items() if var.get()]
        if not selected:
            self._log("No patterns selected.", "err")
            return

        self.running = True
        self.run_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress["value"] = 0
        self.progress["maximum"] = len(selected)

        thread = threading.Thread(target=self._run_patterns, args=(selected,), daemon=True)
        thread.start()

    def _stop_generation(self):
        self.running = False
        if self.current_proc and self.current_proc.poll() is None:
            self.current_proc.terminate()
            self.log_queue.put(("⚠  Generation stopped by user.", "err"))
        self._generation_done()

    def _run_patterns(self, selected):
        python = sys.executable
        total = len(selected)
        done = 0
        failed = []

        self.log_queue.put((f"Starting generation of {total} pattern(s)…", "head"))

        for name in selected:
            if not self.running:
                break

            script = os.path.join(SCRIPT_DIR, f"{name}.py")
            if not os.path.exists(script):
                self.log_queue.put((f"  [SKIP] {name}.py not found", "err"))
                done += 1
                self.root.after(0, lambda d=done: self.progress.config(value=d))
                continue

            self.log_queue.put((f"\n▶ {name} …", "head"))
            self.root.after(0, lambda n=name: self.status_var.set(f"Generating: {n}"))

            try:
                proc = subprocess.Popen(
                    [python, script, "--headless"],
                    cwd=SCRIPT_DIR,
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
                    self.log_queue.put((f"  ✅ {name}.tol saved", "ok"))
                else:
                    self.log_queue.put((f"  ✗ {name} exited with code {proc.returncode}", "err"))
                    failed.append(name)

            except Exception as e:
                self.log_queue.put((f"  ✗ {name}: {e}", "err"))
                failed.append(name)

            done += 1
            self.root.after(0, lambda d=done: self.progress.config(value=d))

        # summary
        self.log_queue.put(("\n─── Summary ───────────────────────", "head"))
        succeeded = done - len(failed) - (total - done if not self.running else 0)
        self.log_queue.put((f"  Generated : {succeeded}/{total}", "ok" if succeeded == total else "info"))
        if failed:
            self.log_queue.put(("  Failed    : " + ", ".join(failed), "err"))
        if not self.running:
            self.log_queue.put(("  (stopped early)", "err"))

        self.root.after(0, self._generation_done)

    def _generation_done(self):
        self.running = False
        self.current_proc = None
        self.run_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Done.")


def main():
    root = tk.Tk()
    root.minsize(860, 560)
    app = MasterTolCreator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
