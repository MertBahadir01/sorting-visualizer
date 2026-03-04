"""
controls.py
Modern control panel: inputs, algorithm selector, speed, and action buttons.
Supports Start / Pause-Resume / Stop / Reset.
"""
import tkinter as tk
from tkinter import ttk
from sorting_algorithms import ALGORITHMS

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#111111"
BG2       = "#191919"
FG        = "#CCCCCC"
FG_DIM    = "#555555"
ACCENT    = "#00E676"
WARN      = "#FFD600"
DANGER    = "#FF5252"
STOP_CLR  = "#FF6D00"
ENTRY_BG  = "#1C1C1C"
BORDER    = "#2A2A2A"


def _entry(parent, default, width=7, label=""):
    frame = tk.Frame(parent, bg=BG)
    if label:
        tk.Label(frame, text=label.upper(), bg=BG, fg=FG_DIM,
                 font=("Courier", 8, "bold")).pack(anchor="w", pady=(0, 2))
    e = tk.Entry(
        frame, width=width,
        bg=ENTRY_BG, fg=FG, insertbackground=FG,
        relief="flat", highlightthickness=1,
        highlightbackground=BORDER, highlightcolor=ACCENT,
        font=("Courier", 11), justify="center",
    )
    e.insert(0, default)
    e.pack()
    return frame, e


def _btn(parent, text, cmd, bg, fg, hover_bg=None, **kw):
    b = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg,
        activebackground=hover_bg or bg,
        activeforeground=fg,
        font=("Courier", 11, "bold"),
        relief="flat", bd=0,
        padx=14, pady=8,
        cursor="hand2",
        **kw,
    )
    return b


class ControlsPanel(tk.Frame):
    def __init__(self, parent, on_start, on_stop, on_pause_resume, on_reset, on_algo_change=None, **kwargs):
        super().__init__(parent, bg=BG, **kwargs)
        self._on_start        = on_start
        self._on_stop         = on_stop
        self._on_pause_resume = on_pause_resume
        self._on_reset        = on_reset
        self._on_algo_change  = on_algo_change
        self._paused          = False
        self._build()

    def _build(self):
        # ── Outer padding frame ───────────────────────────────────────────────
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="x", padx=14, pady=10)

        # ── Row A: inputs ─────────────────────────────────────────────────────
        row_a = tk.Frame(outer, bg=BG)
        row_a.pack(fill="x", pady=(0, 8))

        f1, self.e_min   = _entry(row_a, "10",  label="Min")
        f2, self.e_max   = _entry(row_a, "200", label="Max")
        f3, self.e_count = _entry(row_a, "50",  label="Count")
        for f in (f1, f2, f3):
            f.pack(side="left", padx=(0, 16))

        # Algorithm dropdown
        algo_frame = tk.Frame(row_a, bg=BG)
        tk.Label(algo_frame, text="ALGORITHM", bg=BG, fg=FG_DIM,
                 font=("Courier", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.algo_var = tk.StringVar(value=list(ALGORITHMS.keys())[0])
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SV.TCombobox",
                         fieldbackground=ENTRY_BG, background=ENTRY_BG,
                         foreground=FG, selectbackground=ENTRY_BG,
                         selectforeground=ACCENT, arrowcolor=ACCENT,
                         bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                         padding=4)
        self.combo = ttk.Combobox(
            algo_frame, textvariable=self.algo_var,
            values=list(ALGORITHMS.keys()),
            state="readonly", width=16, style="SV.TCombobox",
            font=("Courier", 11),
        )
        self.combo.pack()
        if self._on_algo_change:
            self.combo.bind("<<ComboboxSelected>>", lambda e: self._on_algo_change(self.algo_var.get()))
        algo_frame.pack(side="left", padx=(0, 16))

        # Speed slider
        speed_frame = tk.Frame(row_a, bg=BG)
        self._speed_label = tk.Label(
            speed_frame, text="SPEED  80 ms", bg=BG, fg=FG_DIM,
            font=("Courier", 8, "bold"))
        self._speed_label.pack(anchor="w", pady=(0, 2))
        self.speed_var = tk.IntVar(value=80)
        self.speed_slider = tk.Scale(
            speed_frame, from_=5, to=400, orient="horizontal",
            variable=self.speed_var, length=150,
            showvalue=False,
            bg=BG, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground=ACCENT,
            sliderrelief="flat", bd=0,
            command=self._on_speed,
        )
        self.speed_slider.pack()
        speed_frame.pack(side="left", padx=(0, 8))

        # Volume slider
        vol_frame = tk.Frame(row_a, bg=BG)
        self._vol_label = tk.Label(
            vol_frame, text="VOLUME  70 %", bg=BG, fg=FG_DIM,
            font=("Courier", 8, "bold"))
        self._vol_label.pack(anchor="w", pady=(0, 2))
        self.volume_var = tk.IntVar(value=70)
        self.volume_slider = tk.Scale(
            vol_frame, from_=0, to=100, orient="horizontal",
            variable=self.volume_var, length=130,
            showvalue=False,
            bg=BG, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground="#29B6F6",
            sliderrelief="flat", bd=0,
            command=self._on_volume,
        )
        self.volume_slider.pack()
        vol_frame.pack(side="left", padx=(0, 8))

        # ── Row B: custom input + buttons ────────────────────────────────────
        row_b = tk.Frame(outer, bg=BG)
        row_b.pack(fill="x")

        # Custom values
        custom_frame = tk.Frame(row_b, bg=BG)
        tk.Label(custom_frame, text="CUSTOM VALUES  (comma or space separated)",
                 bg=BG, fg=FG_DIM, font=("Courier", 8, "bold")).pack(anchor="w", pady=(0, 2))
        self.e_custom = tk.Entry(
            custom_frame, width=28,
            bg=ENTRY_BG, fg=FG, insertbackground=FG,
            relief="flat", highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
            font=("Courier", 11),
        )
        self.e_custom.pack(anchor="w")
        custom_frame.pack(side="left", padx=(0, 20))

        # Sound type dropdown
        sound_frame = tk.Frame(row_b, bg=BG)
        tk.Label(sound_frame, text="SOUND TYPE", bg=BG, fg=FG_DIM,
                 font=("Courier", 8, "bold")).pack(anchor="w", pady=(0, 2))
        from sound import SOUND_TYPES
        self.sound_var = tk.StringVar(value="Huup")
        self.sound_combo = ttk.Combobox(
            sound_frame, textvariable=self.sound_var,
            values=list(SOUND_TYPES.keys()),
            state="readonly", width=9, style="SV.TCombobox",
            font=("Courier", 11),
        )
        self.sound_combo.pack()
        sound_frame.pack(side="left", padx=(0, 16))

        # Pitch slider
        pitch_frame = tk.Frame(row_b, bg=BG)
        self._pitch_label = tk.Label(
            pitch_frame, text="PITCH  1.0×", bg=BG, fg=FG_DIM,
            font=("Courier", 8, "bold"))
        self._pitch_label.pack(anchor="w", pady=(0, 2))
        self.pitch_var = tk.DoubleVar(value=1.0)
        self.pitch_slider = tk.Scale(
            pitch_frame, from_=0.25, to=4.0, resolution=0.05,
            orient="horizontal", variable=self.pitch_var, length=130,
            showvalue=False,
            bg=BG, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground="#CE93D8",
            sliderrelief="flat", bd=0,
            command=self._on_pitch,
        )
        self.pitch_slider.pack()
        pitch_frame.pack(side="left", padx=(0, 16))

        # Error label
        self.lbl_error = tk.Label(
            row_b, text="", bg=BG, fg=DANGER,
            font=("Courier", 9), justify="left")
        self.lbl_error.pack(side="left", expand=True, anchor="w")

        # ── Buttons (right-aligned) ────────────────────────────────────────
        btn_frame = tk.Frame(row_b, bg=BG)
        btn_frame.pack(side="right")

        self.btn_reset = _btn(btn_frame, "↺  RESET",  self._on_reset,
                               bg="#1E1E1E", fg=FG, hover_bg="#2A2A2A")
        self.btn_reset.pack(side="right", padx=(6, 0))

        self.btn_stop = _btn(btn_frame, "■  STOP", self._on_stop,
                              bg="#2A1000", fg=STOP_CLR, hover_bg="#3A1800")
        self.btn_stop.pack(side="right", padx=(6, 0))
        self.btn_stop.configure(state="disabled")

        self.btn_pause = _btn(btn_frame, "⏸  PAUSE", self._toggle_pause,
                               bg="#1A1A00", fg=WARN, hover_bg="#2A2A00")
        self.btn_pause.pack(side="right", padx=(6, 0))
        self.btn_pause.configure(state="disabled")

        self.btn_start = _btn(btn_frame, "▶  START", self._on_start,
                               bg="#003318", fg=ACCENT, hover_bg="#004D22")
        self.btn_start.pack(side="right", padx=(6, 0))

    # ── Callbacks ────────────────────────────────────────────────────────────

    def _on_speed(self, val):
        self._speed_label.configure(text=f"SPEED  {val} ms")

    def _on_volume(self, val):
        self._vol_label.configure(text=f"VOLUME  {val} %")

    def _on_pitch(self, val):
        self._pitch_label.configure(text=f"PITCH  {float(val):.2f}×")

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self.btn_pause.configure(text="▶  RESUME", bg="#003318", fg=ACCENT)
        else:
            self.btn_pause.configure(text="⏸  PAUSE",  bg="#1A1A00", fg=WARN)
        self._on_pause_resume(self._paused)

    # ── Public helpers ────────────────────────────────────────────────────────

    def get_values(self):
        return (
            self.e_min.get().strip(),
            self.e_max.get().strip(),
            self.e_count.get().strip(),
            self.algo_var.get(),
            self.speed_var.get(),
            self.e_custom.get().strip(),
            self.volume_var.get(),
        )

    def show_error(self, msg):
        self.lbl_error.configure(text=f"⚠  {msg}")

    def clear_error(self):
        self.lbl_error.configure(text="")

    def set_sorting(self, sorting: bool):
        """Lock/unlock controls when a sort starts or ends."""
        self._paused = False
        self.btn_pause.configure(text="⏸  PAUSE", bg="#1A1A00", fg=WARN)

        s_inputs = "disabled" if sorting else "normal"
        s_ro     = "disabled" if sorting else "readonly"

        for w in (self.e_min, self.e_max, self.e_count, self.e_custom):
            w.configure(state=s_inputs)
        self.combo.configure(state=s_ro)
        self.speed_slider.configure(state="normal")   # always live

        self.btn_start.configure(state="disabled" if sorting else "normal")
        self.btn_reset.configure(state="disabled" if sorting else "normal")
        self.btn_pause.configure(state="normal"   if sorting else "disabled")
        self.btn_stop.configure( state="normal"   if sorting else "disabled")
