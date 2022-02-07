import pytest

from ssost.hotkeys._common import parse_key_combo_dsl, serialize_motions_to_str
from ssost.hotkeys._common import Press, Release


def test_parse_succeeds():
    assert parse_key_combo_dsl("↑↓shift↓o↓g") == (Press("shift"), Release("shift"), Press("o"), Press("g"))


def test_parse_fails_when_released_without_pressing():
    with pytest.raises(ValueError):
        parse_key_combo_dsl("↑s")


def test_parse_fails_when_released_multiple_times():
    with pytest.raises(ValueError):
        parse_key_combo_dsl("↓s↑s↑s")


def test_parse_fails_when_unknown_key_met():
    with pytest.raises(ValueError):
        parse_key_combo_dsl("↓omg↓wtf↓lol")


def test_serialize_succeeds():
    assert serialize_motions_to_str((Press("a"), Press("b"), Release("b"), Press("shift"), Release("shift"),
                                     Press("shift"), Release("shift"))) == "↓a↓↑b↓↑shift↓↑shift"
