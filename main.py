"""
main.py
Sorting Visualizer — modern rebuild.
Features: Start / Pause-Resume / Stop / Reset, live stats, 7 algorithms.
"""
import tkinter as tk
import time
from visualizer import Visualizer
from controls import ControlsPanel
from sorting_algorithms import ALGORITHMS, ALGO_INFO
from utils import generate_random_list, parse_custom_input, validate_inputs
from sound import play_step

APP_BG   = "#0D0D0D"
DIV_CLR  = "#1E1E1E"


class SortingVisualizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sorting Visualizer")
        self.configure(bg=APP_BG)
        self.minsize(740, 540)
        self.geometry("1080x720")

        self._generator = None
        self._after_id  = None
        self._sorting   = False
        self._paused    = False
        self._data: list[int] = []

        # ── Timer state ──────────────────────────────────────────────────────
        self._time_start:   float = 0.0   # perf_counter when last resumed
        self._time_elapsed: float = 0.0   # accumulated seconds (excluding pauses)
        self._timer_id = None             # after() handle for the clock tick

        self._build_ui()
        self._reset()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.viz = Visualizer(self)
        self.viz.pack(fill="both", expand=True)

        tk.Frame(self, bg=DIV_CLR, height=1).pack(fill="x")

        self.controls = ControlsPanel(
            self,
            on_start        = self._start,
            on_stop         = self._stop,
            on_pause_resume = self._pause_resume,
            on_reset        = self._reset,
            on_algo_change  = self._algo_changed,
        )
        self.controls.pack(fill="x", side="bottom")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _current_algo(self):
        return self.controls.algo_var.get()

    def _algo_changed(self, name):
        self.viz.set_algorithm(name, ALGO_INFO.get(name, ""))

    # ── Actions ───────────────────────────────────────────────────────────────

    def _reset(self):
        self._cancel_timer()
        self._clock_reset()
        self._sorting = False
        self._paused  = False

        mn_s, mx_s, cnt_s, algo, _, custom_s, _vol = self.controls.get_values()
        ok, err, mn, mx, cnt = validate_inputs(mn_s, mx_s, cnt_s)
        if not ok:
            self.controls.show_error(err)
            return
        self.controls.clear_error()

        if custom_s:
            data = parse_custom_input(custom_s, mn, mx)
            if data is None:
                self.controls.show_error("Custom input invalid or out of range.")
                return
        else:
            data = generate_random_list(cnt, mn, mx)

        self._data = data
        self.viz.set_algorithm(algo, ALGO_INFO.get(algo, ""))
        self.viz.set_data(data)
        self.controls.set_sorting(False)

    def _start(self):
        if self._sorting:
            return
        mn_s, mx_s, cnt_s, algo, speed, custom_s, _vol = self.controls.get_values()
        ok, err, mn, mx, cnt = validate_inputs(mn_s, mx_s, cnt_s)
        if not ok:
            self.controls.show_error(err)
            return
        self.controls.clear_error()

        self.viz.set_algorithm(algo, ALGO_INFO.get(algo, ""))
        self.viz.set_data(self._data)   # reset visual counters

        sort_fn = ALGORITHMS[algo]
        self._generator = sort_fn(self._data[:])
        self._sorting   = True
        self._paused    = False

        self.controls.set_sorting(True)
        self.viz.set_status("sorting")
        self._clock_reset()
        self._clock_start()
        self._tick()

    def _stop(self):
        self._cancel_timer()
        self._clock_pause()          # freeze the displayed time
        self._sorting = False
        self._paused  = False
        self._generator = None
        self.controls.set_sorting(False)
        self.viz.set_status("stopped")

    def _pause_resume(self, is_paused: bool):
        self._paused = is_paused
        if not is_paused and self._sorting:
            self.viz.set_status("sorting")
            self._clock_start()      # resume the clock
            self._tick()
        elif is_paused:
            self.viz.set_status("paused")
            self._clock_pause()      # freeze the clock

    def _tick(self):
        if not self._sorting or self._paused:
            return
        speed = self.controls.speed_var.get()
        try:
            arr, compare, swap, sorted_idx = next(self._generator)
            self._data = arr
            self.viz.update_step(arr, compare, swap, sorted_idx)
            # Play a 'huup' chirp pitched to the value being accessed
            if arr:
                ref_idx = (list(compare) + list(swap) + [0])[0]
                vol   = self.controls.volume_var.get() / 100.0
                stype = self.controls.sound_var.get()
                pitch = self.controls.pitch_var.get()
                play_step(arr[ref_idx], min(arr), max(arr), vol, stype, pitch)
            self._after_id = self.after(speed, self._tick)
        except StopIteration:
            self._finish()

    def _finish(self):
        self._sorting   = False
        self._generator = None
        self._after_id  = None
        self._clock_pause()          # stop the clock at final time
        self.controls.set_sorting(False)
        self.viz.set_status("done")

    def _cancel_timer(self):
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    # ── Clock helpers ─────────────────────────────────────────────────────────

    def _clock_start(self):
        """Begin (or resume) counting elapsed time and ticking the display."""
        self._time_start = time.perf_counter()
        self._clock_tick()

    def _clock_pause(self):
        """Accumulate elapsed time so far and stop the display tick."""
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._time_elapsed += time.perf_counter() - self._time_start

    def _clock_reset(self):
        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._time_elapsed = 0.0
        self._time_start   = 0.0
        self.viz.set_elapsed(0.0)

    def _clock_tick(self):
        """Refresh the footer time display ~every 50 ms while running."""
        live = self._time_elapsed + (time.perf_counter() - self._time_start)
        self.viz.set_elapsed(live)
        self._timer_id = self.after(50, self._clock_tick)


if __name__ == "__main__":
    app = SortingVisualizerApp()
    app.mainloop()
