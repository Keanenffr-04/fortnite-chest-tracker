"""Notification sounds. Generates tiny WAV files itself (no asset files to ship) and plays them
with winsound on Windows. On other systems playing is a silent no-op.

The detector (later version) will call the same play_up() when it counts a chest.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

RATE = 44100
UP_NOTES = [(659.3, 70), (880.0, 110)]      # E5 -> A5, rising = "counted"
DOWN_NOTES = [(587.3, 70), (440.0, 110)]    # D5 -> A4, falling = "removed"


def make_tone_wav(path, notes, volume: float = 0.5) -> None:
    """Write a short mono 16-bit WAV: each note is (frequency_hz, duration_ms) with a soft fade."""
    volume = min(1.0, max(0.0, volume))
    frames = bytearray()
    for freq, ms in notes:
        n = int(RATE * ms / 1000)
        fade = max(1, int(RATE * 0.008))
        for i in range(n):
            env = min(1.0, i / fade, (n - i) / fade)
            v = math.sin(2 * math.pi * freq * i / RATE) * env * volume * 0.9
            frames += struct.pack("<h", int(v * 32767))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(frames))


def _winsound_player():
    try:
        import winsound
    except ImportError:
        return None
    return lambda path: winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC)


class SoundPlayer:
    def __init__(self, directory, enabled: bool = True, volume: float = 0.5, player="auto"):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.enabled = enabled
        self.volume = volume
        self._player = _winsound_player() if player == "auto" else player
        self._write_files()

    def _write_files(self) -> None:
        make_tone_wav(self.dir / "chest_up.wav", UP_NOTES, self.volume)
        make_tone_wav(self.dir / "chest_down.wav", DOWN_NOTES, self.volume)

    def update(self, enabled: bool, volume: float) -> None:
        self.enabled = enabled
        if abs(volume - self.volume) > 1e-9:
            self.volume = volume
            self._write_files()

    def _play(self, name: str) -> bool:
        if not self.enabled or self._player is None:
            return False
        try:
            self._player(self.dir / name)
            return True
        except Exception:
            return False  # never let a sound problem break counting

    def play_up(self) -> bool:
        return self._play("chest_up.wav")

    def play_down(self) -> bool:
        return self._play("chest_down.wav")
