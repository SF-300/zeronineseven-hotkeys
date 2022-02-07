import enum
from enum import Enum

from ._common import normalize_action

__all__ = "all_controls",

_modes_root = "PyCharm"


@enum.unique
class Mode(tuple, Enum):
    EDITOR_VIM_NORMAL = (_modes_root, "editor", "vim normal")
    EDITOR_VIM_VISUAL = (_modes_root, "editor", "vim visual")
    EDITOR_VIM_LOCAL_SEARCH = (_modes_root, "editor", "vim local search")
    EDITOR_VIM_COMMAND = (_modes_root, "editor", "vim command")
    EDITOR_VIM_REPLACE = (_modes_root, "editor", "vim replace")
    EDITOR_NATIVE_LOCAL_SEARCH = (_modes_root, "editor", "native local search")
    EDITOR_NATIVE_LOCAL_REPLACE = (_modes_root, "editor", "native local replace")
    PROJECT_NORMAL = (_modes_root, "project", "normal")
    PROJECT_SEARCH = (_modes_root, "project", "search")
    FILE_STRUCTURE = (_modes_root, "file structure")


_global_controls = (
    ("↓ctrl↓shift↓f12", "Show/hide all panes except the text editor."),
    ("↓ctrl↓shift↓a", "Open 'Actions' search bar."),
    ("↓↑shift↓shift", "Open 'All' search bar."),
    ("↓f10", "Toggle 'Distraction-free' mode."),
)

_common_refactoring_controls = (
    ("↓shift↓f6", "Rename."),
)

_editor_common_native_search_controls = (
    ("↓f3", "Go to next found occurrence."),
    ("↓shift↓f3", "Go to next found occurrence."),
    ("↓alt↓j", "Add selection for next occurrence."),
    ("↓alt↓shift↓j", "Unselect occurrence."),
    ("↓ctrl↓alt↓shift↓j", "Select all occurrences."),
)

_editor_common_controls = (
    *_editor_common_native_search_controls,
    ("↓\\", "Open local (vim) search bar."),
    ("↓ctrl↓f", "Open local (native) search bar."),
    ("↓ctrl↓shift↓f", "Open global search bar."),
    ("↓ctrl↓r", "Open local replace bar."),
    ("↓ctrl↓shift↓r", "Open global replace bar."),
    ("↓h", "Move cursor one symbol left."),
    ("↓j", "Move cursor one line down."),
    ("↓k", "Move cursor one line up."),
    ("↓l", "Move cursor one symbol right."),
    ("↓ctrl↓u", "Scroll half-screen up."),
    ("↓ctrl↓d", "Scroll half-screen down."),
    ("↓ctrl↓f", "Scroll full-screen up."),
    ("↓ctrl↓b", "Scroll full-screen down."),
    ("↓ctrl↓}", "Scroll paragraph forward."),
    ("↓ctrl↓{", "Scroll paragraph backward."),
    ("↓alt↓1", "Focus 'Project' pane."),
    ("↓ctrl↓w", "Extend selection."),
    ("↓ctrl↓shift↓w", "Shrink selection."),
    ("↓ctrl↓z", "Undo."),
    ("↓ctrl↓shift↓z", "Redo."),
    ("↓ctrl↓e", "Show recently edited files."),
    ("↓ctrl↓shift↓e", "Show recently edited files' parts."),
    ("↓alt↓shift↓insert", "Toggle multiple cursors virtual spaces mode."),
    ("↓alt↓shift↓g", "Add carets to the end of each line in the selected block."),
)

all_controls = tuple(normalize_action(k, *v) for k, vs in {
    Mode.PROJECT_NORMAL: (
        *_global_controls,
        *_common_refactoring_controls,
        ("↓j", "Move cursor one line down."),
        ("↓k", "Move cursor one line up."),
    ),
    Mode.EDITOR_NATIVE_LOCAL_SEARCH: (
        *_global_controls,
        *_editor_common_native_search_controls,
        ("↓alt↓down", "Show and focus 'Search history' drop-down."),
        ("↓alt↓c", "Toggle case-sensitivity."),
        ("↓alt↓w", "Toggle full words matching only."),
        ("↓alt↓x", "Toggle regexp matching mode."),
        ("↓ctrl↓alt↓f", "Show filter popup."),
        ("↓enter", "Go to next found occurrence."),
        ("↓shift↓enter", "Go to next found occurrence."),
    ),
    Mode.EDITOR_VIM_VISUAL: (
        *_global_controls,
        *_editor_common_controls,
        *_common_refactoring_controls,
        # ("↓alt↓n", "Start multiple cursors."),
    ),
    Mode.EDITOR_VIM_NORMAL: (
        *_global_controls,
        *_editor_common_controls,
        ("↓shift↓k", "Show definition without navigating to it."),
    ),
    Mode.FILE_STRUCTURE: (
        ("↓esc", "Jump back to the sub-mode which is active inside The Editor"),
    )
}.items() for v in vs)
# assert set(modes_to_controls.keys()) == set(Mode)
