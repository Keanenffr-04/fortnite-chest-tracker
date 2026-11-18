import wave

from app.core.sound import DOWN_NOTES, UP_NOTES, SoundPlayer, make_tone_wav


def peak_and_len(path):
    with wave.open(str(path), "rb") as w:
        raw = w.readframes(w.getnframes())
        n = w.getnframes()
        assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 44100
    import struct
    vals = struct.unpack("<%dh" % n, raw)
    return max(abs(v) for v in vals), n


def test_wav_is_valid_and_right_length(tmp_path):
    make_tone_wav(tmp_path / "a.wav", UP_NOTES, 0.5)
    peak, n = peak_and_len(tmp_path / "a.wav")
    expected = sum(int(44100 * ms / 1000) for _, ms in UP_NOTES)
    assert n == expected and 0 < peak < 32767


def test_volume_scales_amplitude_and_zero_is_silent(tmp_path):
    make_tone_wav(tmp_path / "q.wav", UP_NOTES, 0.25)
    make_tone_wav(tmp_path / "l.wav", UP_NOTES, 1.0)
    make_tone_wav(tmp_path / "z.wav", UP_NOTES, 0.0)
    q, _ = peak_and_len(tmp_path / "q.wav"); l, _ = peak_and_len(tmp_path / "l.wav"); z, _ = peak_and_len(tmp_path / "z.wav")
    assert q < l and abs(l / q - 4) < 0.3 and z == 0


def test_player_plays_when_enabled(tmp_path):
    played = []
    sp = SoundPlayer(tmp_path, True, 0.5, player=played.append)
    assert sp.play_up() and sp.play_down()
    assert [p.name for p in played] == ["chest_up.wav", "chest_down.wav"]
    assert all(p.exists() for p in played)


def test_player_silent_when_disabled_or_no_backend(tmp_path):
    played = []
    sp = SoundPlayer(tmp_path, False, 0.5, player=played.append)
    assert not sp.play_up() and played == []
    assert not SoundPlayer(tmp_path, True, 0.5, player=None).play_up()


def test_sound_failure_never_raises(tmp_path):
    def boom(_):
        raise OSError("no audio device")
    assert SoundPlayer(tmp_path, True, 0.5, player=boom).play_up() is False


def test_update_volume_rewrites_files(tmp_path):
    sp = SoundPlayer(tmp_path, True, 0.2, player=None)
    before, _ = peak_and_len(tmp_path / "chest_up.wav")
    sp.update(True, 0.8)
    after, _ = peak_and_len(tmp_path / "chest_up.wav")
    assert after > before
