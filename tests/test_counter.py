from app.core.counter import ChestCounter


def make(sens=0.8, cd=1.5):
    t = [0.0]
    return ChestCounter(sens, cd, clock=lambda: t[0]), t


def test_counts_one_per_detection():
    c, t = make()
    assert c.register_detection(0.9)
    assert c.match_count == 1 and c.session_count == 1


def test_duplicate_within_cooldown_rejected():
    c, t = make()
    c.register_detection(0.9); t[0] = 1.0
    assert not c.register_detection(0.99)
    assert c.match_count == 1


def test_counts_again_after_cooldown():
    c, t = make()
    c.register_detection(0.9); t[0] = 1.6
    assert c.register_detection(0.9)
    assert c.match_count == 2


def test_low_confidence_rejected():
    c, t = make()
    assert not c.register_detection(0.5)
    assert c.match_count == 0


def test_manual_adjust_and_no_negative():
    c, t = make()
    c.manual_adjust(-1)
    assert c.match_count == 0
    c.manual_adjust(1); c.manual_adjust(1); c.manual_adjust(-1)
    assert c.match_count == 1


def test_new_match_resets_match_but_keeps_session():
    c, t = make()
    c.register_detection(0.9); t[0] = 5
    c.register_detection(0.9)
    s = c.new_match()
    assert s["chests"] == 2 and len(s["events"]) == 2
    assert c.match_count == 0 and c.session_count == 2


def test_cooldown_cleared_on_new_match():
    c, t = make()
    c.register_detection(0.9)
    c.new_match()
    assert c.register_detection(0.9)
