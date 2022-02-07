import itertools
import typing
from collections import deque
from typing import Literal, Union, Tuple, Sequence, FrozenSet, Iterable, Iterator, NamedTuple

from attr import frozen
from typing_extensions import TypeAlias

__all__ = "Key", "Action", "Motions", "Motion", "get_combo_keys", "normalize_action", "NormalizedAction", "parse_key_combo_dsl", "parse_key_combo_dsl_iter", "Press", "pretty_print_motions", "pretty_print_context", "pretty_print_motion", "Release", "serialize_motions_to_str", "serialize_motions_to_str_iter"

Key = Literal[
    "esc",
    "enter",
    "ctrl",
    "alt",
    "shift",
    "insert",
    "down",
    "up",
    "left",
    "right",
    "tab",
    "\\",
    "}",
    "{",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
]


@frozen
class Press:
    key: Key


@frozen
class Release:
    key: Key


Motion: TypeAlias = Union[Press, Release]
Motions: TypeAlias = Sequence[Motion]
Action: TypeAlias = Tuple[Tuple[str], str, str]


class NormalizedAction(NamedTuple):
    context: Tuple[str]
    combo: Motions
    description: str


def _validate_key(k: str) -> Key:
    if k not in set(typing.get_args(Key)):
        raise ValueError(f"Unknown keyboard key '{k}'")
    return typing.cast(Key, k)


def parse_key_combo_dsl_iter(keys_combos: str) -> Iterator[Motion]:
    pressed, index = set(), 0
    while index < len(keys_combos):
        m_index = index
        while keys_combos[m_index] in {"↓", "↑"}:
            m_index += 1
        k_index = m_index
        try:
            while keys_combos[k_index] not in {"↓", "↑"}:
                k_index += 1
        except IndexError:
            pass
        m = keys_combos[index: m_index]
        k = _validate_key(keys_combos[m_index: k_index])
        if m == "↓↑":
            yield Press(k)
            yield Release(k)
        elif m == "↑↓":
            raise ValueError("Invalid motion '↑↓'!")
        elif m == "↑":
            try:
                pressed.remove(k)
            except KeyError:
                raise ValueError(f"'{k}' was never indicated as pressed!")
            yield Release(k)
        elif m == "↓":
            if k in pressed:
                raise RuntimeError(f"'{k}' key should already be pressed!")
            pressed.add(k)
            yield Press(k)
        elif __debug__ is True:
            raise AssertionError()
        index = k_index


def parse_key_combo_dsl(keys_combos: str) -> Motions:
    return tuple(parse_key_combo_dsl_iter(keys_combos))


def normalize_action(context: Tuple[str], combo: str, description: str) -> NormalizedAction:
    return NormalizedAction(context, parse_key_combo_dsl(combo), description)


class _PeekWrapper:
    def __init__(self, iter_, window_size: int = 1):
        self.__iter = iter_
        self.__window = deque(maxlen=window_size)
        self.__window_size = window_size

    def forward(self, n: int):
        for _ in itertools.repeat(None, n):
            try:
                self.__window.append(next(self.__iter))
            except StopIteration:
                self.__window.popleft()

    def peek(self, n: int):
        assert n <= self.__window_size
        try:
            while len(self.__window) < n:
                self.__window.append(next(self.__iter))
        except StopIteration:
            raise IndexError() from None
        return self.__window[n - 1]

    def __next__(self):
        if len(self.__window) < 1:
            try:
                self.__window.append(next(self.__iter))
            except StopIteration:
                pass
        try:
            return self.__window.popleft()
        except IndexError:
            raise StopIteration() from None

    def __iter__(self):
        return self


def serialize_motions_to_str_iter(ms: Iterable[Motion]) -> Iterator[str]:
    ms_iter = _PeekWrapper(iter(ms))
    for cur_m in ms_iter:
        if isinstance(cur_m, Press):
            try:
                next_m = ms_iter.peek(1)
            except IndexError:
                next_m = None
            if isinstance(next_m, Release) and next_m.key == cur_m.key:
                ms_iter.forward(1)
                yield "↓↑" + cur_m.key
            else:
                yield "↓" + cur_m.key
        else:
            yield "↑" + cur_m.key


def serialize_motions_to_str(ms: Iterable[Motion]) -> str:
    return "".join(serialize_motions_to_str_iter(ms))


def pretty_print_motions(ms: Iterable[Motion]) -> str:
    return "·".join(serialize_motions_to_str_iter(ms))


def pretty_print_motion(m: Motion) -> str:
    if isinstance(m, Press):
        return "↓" + m.key
    elif isinstance(m, Release):
        return "↑" + m.key
    else:
        raise TypeError()


def pretty_print_context(c: Tuple[str]) -> str:
    return "/".join(p.capitalize() for p in c)


def get_combo_keys(ms: Iterable[Motion]) -> FrozenSet[Key]:
    return frozenset(m.key for m in ms)
