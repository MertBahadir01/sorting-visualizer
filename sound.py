"""
sound.py  –  10 sound types, volume + pitch control for the sorting visualiser.

Sound types:
  1.  Huup       – upward chirp sine (original)
  2.  Blip       – short pure sine beep
  3.  Zap        – downward laser sweep
  4.  Bubble     – soft FM bubble pop
  5.  Ping       – clean bell-like ping with ring
  6.  Thud       – low percussive thud
  7.  Glitch     – noisy digital glitch burst
  8.  Retro      – NES-style square wave
  9.  Pluck      – Karplus-Strong string pluck
  10. Wobble     – tremolo sine wobble
  11. Drip       – water-drop sine drip
  12. Laser      – sci-fi high laser zing

Player priority: pygame → ffplay → afplay → winsound → silent
"""
import io, math, random, struct, subprocess, sys, threading, wave

SAMPLE_RATE = 22050

# ── Synth helpers ─────────────────────────────────────────────────────────────

def _pack(frames):
    return struct.pack(f"<{len(frames)}h", *[max(-32767, min(32767, int(x))) for x in frames])

def _make_wav(pcm: bytes) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE); w.writeframes(pcm)
    return buf.getvalue()

def _env(i, n, attack=0.08, decay=6.0, dur=1.0):
    t = i / SAMPLE_RATE
    return min(1.0, i / (n * attack)) * math.exp(-decay * t / dur)

# ── 12 sound generators  (freq, volume, pitch_mult) → bytes ──────────────────

def _huup(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.055); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        sweep = f * (1 + 0.25 * i / n)
        frames.append(vol * _env(i,n,0.08,6,.055) * math.sin(2*math.pi*sweep*t) * 32767)
    return _pack(frames)

def _blip(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.04); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        frames.append(vol * _env(i,n,0.05,8,.04) * math.sin(2*math.pi*f*t) * 32767)
    return _pack(frames)

def _zap(freq, vol, pm):
    f = freq * pm * 2.5; n = int(SAMPLE_RATE * 0.06); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        sweep = f * (1 - 0.85 * i / n)
        frames.append(vol * _env(i,n,0.03,7,.06) * math.sin(2*math.pi*sweep*t) * 32767)
    return _pack(frames)

def _bubble(freq, vol, pm):
    f = freq * pm * 0.7; n = int(SAMPLE_RATE * 0.07); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        mod = math.sin(2*math.pi*f*3*t) * 0.5
        carrier = math.sin(2*math.pi*f*(1+mod)*t)
        frames.append(vol * _env(i,n,0.1,5,.07) * carrier * 32767)
    return _pack(frames)

def _ping(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.18); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-4.0 * t)
        s = math.sin(2*math.pi*f*t) + 0.3*math.sin(2*math.pi*f*2.76*t)
        frames.append(vol * env * s * 0.6 * 32767)
    return _pack(frames)

def _thud(freq, vol, pm):
    f = max(40, freq * pm * 0.18); n = int(SAMPLE_RATE * 0.09); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        sweep = f * math.exp(-20 * t)
        env = math.exp(-12 * t)
        frames.append(vol * env * math.sin(2*math.pi*sweep*t) * 32767)
    return _pack(frames)

def _glitch(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.04); frames = []
    rng = random.Random(int(f))
    for i in range(n):
        t = i / SAMPLE_RATE
        noise = rng.uniform(-1, 1)
        tone  = math.sin(2*math.pi*f*t)
        env   = _env(i, n, 0.05, 9, .04)
        frames.append(vol * env * (tone * 0.5 + noise * 0.5) * 32767)
    return _pack(frames)

def _retro(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.055); frames = []
    period = SAMPLE_RATE / f if f > 0 else 1
    for i in range(n):
        sq = 1.0 if (i % max(1, int(period))) < (period / 2) else -1.0
        frames.append(vol * _env(i,n,0.05,5,.055) * sq * 32767)
    return _pack(frames)

def _pluck(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.20)
    buf_len = max(1, int(SAMPLE_RATE / f))
    buf = [random.uniform(-1, 1) for _ in range(buf_len)]
    frames = []
    for i in range(n):
        s = buf[i % buf_len]
        buf[i % buf_len] = (s + buf[(i+1) % buf_len]) * 0.498
        frames.append(vol * s * 32767 * math.exp(-1.5 * i / n))
    return _pack(frames)

def _wobble(freq, vol, pm):
    f = freq * pm; n = int(SAMPLE_RATE * 0.08); frames = []
    trem_rate = 18.0
    for i in range(n):
        t = i / SAMPLE_RATE
        trem = 0.5 + 0.5 * math.sin(2*math.pi*trem_rate*t)
        env  = _env(i, n, 0.1, 4, .08)
        frames.append(vol * env * trem * math.sin(2*math.pi*f*t) * 32767)
    return _pack(frames)

def _drip(freq, vol, pm):
    f = freq * pm * 1.4; n = int(SAMPLE_RATE * 0.065); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        sweep = f * (1 + 0.6 * math.exp(-30 * t))
        env   = math.exp(-9 * t) * min(1.0, i / (n * 0.06))
        frames.append(vol * env * math.sin(2*math.pi*sweep*t) * 32767)
    return _pack(frames)

def _laser(freq, vol, pm):
    f = freq * pm * 3.0; n = int(SAMPLE_RATE * 0.05); frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        sweep = f * (1 + 1.5 * (1 - i/n))
        env   = _env(i, n, 0.02, 10, .05)
        frames.append(vol * env * math.sin(2*math.pi*sweep*t) * 32767)
    return _pack(frames)


SOUND_TYPES = {
    "Huup":   _huup,
    "Blip":   _blip,
    "Zap":    _zap,
    "Bubble": _bubble,
    "Ping":   _ping,
    "Thud":   _thud,
    "Glitch": _glitch,
    "Retro":  _retro,
    "Pluck":  _pluck,
    "Wobble": _wobble,
    "Drip":   _drip,
    "Laser":  _laser,
}

# ── Player detection ──────────────────────────────────────────────────────────

def _has_cmd(cmd):
    try:
        subprocess.run([cmd, "-version"], capture_output=True, timeout=2)
        return True
    except Exception:
        return False

_pygame_mixer = None
def _init_pygame():
    global _pygame_mixer
    try:
        import pygame.mixer as mx
        mx.pre_init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=256)
        mx.init(); _pygame_mixer = mx; return True
    except Exception:
        return False

if _init_pygame():           _PLAYER = "pygame"
elif _has_cmd("ffplay"):     _PLAYER = "ffplay"
elif sys.platform=="darwin": _PLAYER = "afplay"
elif sys.platform=="win32":  _PLAYER = "winsound"
else:                        _PLAYER = "none"

print(f"[sound] player: {_PLAYER}")

# ── Per-player play ───────────────────────────────────────────────────────────

def _play_pygame(wav):
    try:
        import pygame.mixer as mx
        mx.Sound(buffer=bytearray(wav[44:])).play()
    except Exception: pass

def _play_ffplay(wav):
    try:
        p = subprocess.Popen(
            ["ffplay","-nodisp","-autoexit","-loglevel","quiet","-i","pipe:0"],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.stdin.write(wav); p.stdin.close(); p.wait()
    except Exception: pass

def _play_afplay(wav):
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav); tmp = f.name
        subprocess.Popen(["afplay", tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception: pass

def _play_winsound(wav):
    try:
        import winsound, tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav); tmp = f.name
        winsound.PlaySound(tmp, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception: pass

_DISPATCH = {
    "pygame":   _play_pygame,
    "ffplay":   _play_ffplay,
    "afplay":   _play_afplay,
    "winsound": _play_winsound,
    "none":     lambda _: None,
}

# ── Cache + public API ────────────────────────────────────────────────────────

_cache: dict = {}

def play_step(value: int, min_val: int, max_val: int,
              volume: float = 0.70,
              sound_type: str = "Huup",
              pitch_mult: float = 1.0):
    """Play a sound for one sorting step."""
    if _PLAYER == "none" or volume <= 0:
        return

    ratio = (value - min_val) / max(max_val - min_val, 1)
    # Base frequency range: 160–1400 Hz
    freq  = 160.0 + ratio * (1400.0 - 160.0)

    # Quantise for caching
    fkey = round(freq / 5) * 5
    vkey = round(volume * 10)
    pkey = round(pitch_mult * 4)
    ckey = (sound_type, fkey, vkey, pkey)

    if ckey not in _cache:
        gen = SOUND_TYPES.get(sound_type, _huup)
        pcm = gen(float(fkey), volume * 0.55, pitch_mult)
        _cache[ckey] = _make_wav(pcm)
        if len(_cache) > 600:
            del _cache[next(iter(_cache))]

    threading.Thread(
        target=_DISPATCH[_PLAYER], args=(_cache[ckey],), daemon=True
    ).start()
