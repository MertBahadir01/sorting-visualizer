"""
visualizer.py
Modern bar-chart canvas with gradient-like shading, glow accents,
a live stats overlay, and smooth per-step repaints.
"""
import tkinter as tk
import math

# ── Palette ──────────────────────────────────────────────────────────────────
BG          = "#0D0D0D"
GRID_LINE   = "#1A1A1A"

BAR_BASE    = "#00E676"   # vivid green
BAR_DARK    = "#00A152"   # darker green (bar body shade)
COMPARE     = "#FFD600"   # amber — being compared
SWAP        = "#FF6D00"   # hot orange — just swapped
SORTED      = "#1B5E20"   # deep forest — sorted region
SORTED_TOP  = "#43A047"   # lighter top for sorted bars

PIVOT       = "#E040FB"   # purple — pivot in quick/heap

TEXT_BRIGHT = "#F0F0F0"
TEXT_DIM    = "#505050"
TEXT_ACCENT = "#00E676"
TEXT_WARN   = "#FFD600"

LABEL_BG    = "#141414"

GAP_RATIO   = 0.12        # fraction of total width used for gaps


class Visualizer(tk.Canvas):
    """High-fidelity bar chart with live comparison/swap counters."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG, highlightthickness=0, **kwargs)
        self._data: list[int]  = []
        self._compare: list[int] = []
        self._swap: set        = set()
        self._sorted: set      = set()
        self._pivot: set       = set()
        self._algo_name        = ""
        self._algo_info        = ""
        self._steps            = 0
        self._comparisons      = 0
        self._swaps_count      = 0
        self._status           = "idle"   # idle | sorting | paused | done | stopped
        self._elapsed: float   = 0.0      # seconds tracked by main.py clock
        self.bind("<Configure>", lambda e: self._redraw())

    # ── Public API ───────────────────────────────────────────────────────────

    def set_algorithm(self, name: str, info: str = ""):
        self._algo_name = name
        self._algo_info = info

    def set_data(self, data: list[int]):
        self._data        = data[:]
        self._compare     = []
        self._swap        = set()
        self._sorted      = set()
        self._pivot       = set()
        self._steps       = 0
        self._comparisons = 0
        self._swaps_count = 0
        self._elapsed     = 0.0
        self._status      = "idle"
        self._redraw()

    def update_step(self, data, compare, swap, sorted_indices):
        self._data    = data[:]
        self._compare = list(compare)
        self._swap    = set(swap)
        self._sorted  = set(sorted_indices)
        self._steps  += 1
        if compare:
            self._comparisons += 1
        if swap:
            self._swaps_count += 1
        self._redraw()

    def set_elapsed(self, seconds: float):
        """Update the displayed elapsed time (called by main.py clock)."""
        self._elapsed = seconds
        self._redraw()

    def set_status(self, status: str):
        """status: idle | sorting | paused | done | stopped"""
        self._status = status
        if status == "done":
            self._sorted  = set(range(len(self._data)))
            self._compare = []
            self._swap    = set()
        self._redraw()

    # ── Drawing ──────────────────────────────────────────────────────────────

    def _redraw(self):
        self.delete("all")
        W = self.winfo_width()
        H = self.winfo_height()
        if W < 2 or H < 2:
            return

        HEADER_H = 56
        FOOTER_H = 38

        self._draw_header(W, HEADER_H)
        self._draw_bars(W, H, HEADER_H, FOOTER_H)
        self._draw_footer(W, H, FOOTER_H)

    def _draw_header(self, W, H):
        # Background strip
        self.create_rectangle(0, 0, W, H, fill=LABEL_BG, outline="")

        # Algorithm name (left-aligned)
        self.create_text(
            16, H // 2,
            text=self._algo_name or "—",
            fill=TEXT_ACCENT,
            font=("Courier", 17, "bold"),
            anchor="w",
        )

        # Status pill (right-aligned)
        status_cfg = {
            "idle":    ("#333333", TEXT_DIM,    "READY"),
            "sorting": ("#003300", TEXT_ACCENT, "SORTING"),
            "paused":  ("#332200", TEXT_WARN,   "PAUSED"),
            "done":    ("#003300", TEXT_ACCENT, "DONE ✓"),
            "stopped": ("#330000", "#FF5252",   "STOPPED"),
        }
        pill_bg, pill_fg, pill_txt = status_cfg.get(
            self._status, ("#222", TEXT_DIM, self._status.upper())
        )
        pw = 90
        px = W - pw - 12
        py = (H - 22) // 2
        self.create_rectangle(px, py, px + pw, py + 22,
                              fill=pill_bg, outline="", width=0)
        self.create_text(px + pw // 2, py + 11,
                         text=pill_txt, fill=pill_fg,
                         font=("Courier", 10, "bold"), anchor="center")

        # Complexity info (centre)
        if self._algo_info:
            self.create_text(
                W // 2, H // 2,
                text=self._algo_info,
                fill=TEXT_DIM,
                font=("Courier", 9),
                anchor="center",
            )

    def _draw_bars(self, W, H, header_h, footer_h):
        if not self._data:
            return

        x0 = 8
        y0 = header_h + 4
        x1 = W - 8
        y1 = H - footer_h - 4
        cw = x1 - x0
        ch = y1 - y0
        if cw <= 0 or ch <= 0:
            return

        # Subtle horizontal grid lines
        grid_steps = 4
        for g in range(1, grid_steps):
            gy = y0 + ch * g // grid_steps
            self.create_line(x0, gy, x1, gy, fill=GRID_LINE, width=1)

        n       = len(self._data)
        gap_tot = cw * GAP_RATIO
        gap     = gap_tot / (n + 1)
        bar_w   = (cw - gap_tot) / n
        max_val = max(self._data) if self._data else 1

        for i, val in enumerate(self._data):
            bx0 = x0 + gap * (i + 1) + bar_w * i
            bx1 = bx0 + bar_w
            bh  = max(2, (val / max_val) * ch)
            by0 = y1 - bh
            by1 = y1

            # Colour decision
            if i in self._swap:
                top_col, body_col = SWAP,     "#BF360C"
            elif i in self._compare:
                top_col, body_col = COMPARE,  "#F57F17"
            elif i in self._sorted:
                top_col, body_col = SORTED_TOP, SORTED
            else:
                top_col, body_col = BAR_BASE, BAR_DARK

            r = min(3, bar_w / 2.5)
            self._bar(bx0, by0, bx1, by1, r, top_col, body_col)

            # Value text when bars are wide enough
            if bar_w >= 16:
                fsize = max(6, min(11, int(bar_w * 0.5)))
                self.create_text(
                    (bx0 + bx1) / 2, by1 - 2,
                    text=str(val),
                    fill=TEXT_BRIGHT if i in self._swap or i in self._compare else TEXT_DIM,
                    font=("Courier", fsize, "bold"),
                    anchor="s",
                )

    def _draw_footer(self, W, H, FH):
        fy = H - FH
        self.create_rectangle(0, fy, W, H, fill=LABEL_BG, outline="")
        self.create_line(0, fy, W, fy, fill="#1E1E1E", width=1)

        # Format elapsed time
        e = self._elapsed
        if e >= 60:
            mins = int(e) // 60
            secs = e - mins * 60
            time_str = f"{mins}:{secs:05.2f}"
        else:
            time_str = f"{e:.3f} s"

        stats = [
            ("STEPS",       str(self._steps),       TEXT_BRIGHT),
            ("COMPARISONS", str(self._comparisons),  TEXT_WARN),
            ("SWAPS",       str(self._swaps_count),  "#FF6D00"),
            ("ELEMENTS",    str(len(self._data)),    TEXT_DIM),
            ("TIME",        time_str,                "#29B6F6"),
        ]
        col_w = W // len(stats)
        for k, (label, value, color) in enumerate(stats):
            cx = col_w * k + col_w // 2
            cy = fy + FH // 2
            self.create_text(cx, cy - 7,  text=label, fill=TEXT_DIM,
                             font=("Courier", 7, "bold"), anchor="center")
            self.create_text(cx, cy + 8,  text=value, fill=color,
                             font=("Courier", 12, "bold"), anchor="center")

        # Thin dividers
        for k in range(1, len(stats)):
            dx = col_w * k
            self.create_line(dx, fy + 4, dx, H - 4, fill="#222", width=1)

    def _bar(self, x0, y0, x1, y1, r, top_col, body_col):
        """Two-tone bar: rounded top cap in top_col, body in body_col."""
        cap_h = min(r * 2 + 2, (y1 - y0) * 0.4)
        # Body
        if y0 + cap_h < y1:
            self.create_rectangle(x0, y0 + cap_h, x1, y1,
                                  fill=body_col, outline="")
        # Top cap (rounded)
        self.create_polygon(
            x0 + r, y0,
            x1 - r, y0,
            x1,     y0 + r,
            x1,     y0 + cap_h,
            x0,     y0 + cap_h,
            x0,     y0 + r,
            smooth=True,
            fill=top_col, outline="",
        )
