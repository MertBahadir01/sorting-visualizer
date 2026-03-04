# Sorting Visualizer

A real-time sorting algorithm visualiser built with Python and Tkinter. Watch algorithms sort data step by step, with live stats, a synth sound engine, and full playback controls.

---

## Features

- **7 sorting algorithms** — Bubble, Selection, Insertion, Merge, Quick, Heap, and Shell Sort
- **Live stats footer** — tracks Steps, Comparisons, Swaps, Elements, and elapsed Time
- **Sound engine** — 12 synthesised sound types, each pitched to the bar value being accessed
- **Volume and Pitch sliders** — tune the audio in real time while sorting
- **Speed slider** — from 5 ms/step (blazing fast) to 400 ms/step (slow motion)
- **Pause / Resume / Stop / Reset** — full playback control at any moment
- **Custom input** — type your own values (comma or space separated)
- **Colour-coded bars** — green (unsorted), amber (comparing), orange (swapping), dark green (sorted)

---

## Requirements

- Python 3.9 or newer
- No third-party Python packages required
- **For sound:** one of the following must be installed:
  - `pip install pygame` — recommended, lowest latency
  - [FFmpeg](https://ffmpeg.org/download.html) — `ffplay` is used automatically if found
  - macOS: `afplay` is built in
  - Windows: `winsound` is built in

---

## Installation

```bash
# Clone or unzip the project, then:
cd sorting-visualizer
python main.py
```

No build step. No virtual environment required.

---

## File Structure

```
main.py              — App entry point and state machine
visualizer.py        — Canvas rendering (bars, header, footer)
controls.py          — Control panel UI (sliders, buttons, dropdowns)
sorting_algorithms.py — All 7 algorithm generators
sound.py             — Synth engine and audio playback
utils.py             — Input validation and list generation
```

---

## Sound Types

| Name   | Character                        |
|--------|----------------------------------|
| Huup   | Upward chirp (default)           |
| Blip   | Short clean beep                 |
| Zap    | Downward laser sweep             |
| Bubble | FM bubble pop                    |
| Ping   | Bell with overtone ring          |
| Thud   | Deep percussive kick             |
| Glitch | Noisy digital crunch             |
| Retro  | NES-style square wave            |
| Pluck  | Karplus-Strong string            |
| Wobble | Tremolo sine wave                |
| Drip   | Water drop                       |
| Laser  | Sci-fi high-frequency zing       |

---

## License

MIT — free to use, modify, and distribute.
