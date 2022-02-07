import enum
import functools
from enum import Enum
from typing import Tuple

from ._common import normalize_action

__all__ = "all_controls",


@enum.unique
class Mode(tuple, Enum):
    NORMAL = ("Edge", "normal")
    VISUAL = ("Edge", "visual")


all_controls = tuple(normalize_action(k, *v) for k, vs in {
    Mode.NORMAL: (
        ("↓k", "Scroll one line up."),
        ("↓j", "Scroll one line down."),
        ("↓u", "Scroll half a screen up."),
        ("↓d", "Scroll half a screen down."),
        ("↓f", "Highlight links."),
        ("↓\\", "Open local (vim) search bar."),
        ("↓ctrl↓f", "Open local (native) search bar."),
    ),
}.items() for v in vs)
