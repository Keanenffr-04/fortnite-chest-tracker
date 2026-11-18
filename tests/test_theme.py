import re

from app.config.settings import THEME_NAMES
from app.ui.theme import stylesheet


def test_stylesheet_has_no_unreplaced_tokens_for_every_theme():
    for name in THEME_NAMES:
        css = stylesheet(name)
        assert not re.search(r"@[A-Z0-9]+@", css), name
        assert css.count("{") == css.count("}"), name


def test_accent_follows_theme_and_unknown_falls_back():
    assert "#a855f7" in stylesheet("violet")          # violet accent 1
    assert "#22c55e" in stylesheet("green")
    assert stylesheet("nonsense") == stylesheet("violet")
