import asyncio
import contextlib
import itertools
import random
from asyncio.queues import Queue
from collections import deque
from contextlib import AsyncExitStack
from typing import NoReturn, Callable, Awaitable, AsyncIterator, Union, Deque

import attr
import qasync
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QLineEdit

from zeronineseven.hotkeys import all_controls
from ._common import Press, Release, Motion, Motions, Key, pretty_print_motion, pretty_print_motions, \
    NormalizedAction


def _extract_key(event: QKeyEvent) -> Key:
    # FIXME(zeronineseven): Distinguish left/right shift and similar keys.
    #                       * https://stackoverflow.com/questions/44813630/detecting-the-right-shift-key-in-qt
    try:
        key = {
            Qt.Key_Escape: "esc",
            Qt.Key_Enter: "enter",
            Qt.Key_Control: "ctrl",
            Qt.Key_Alt: "alt",
            Qt.Key_Shift: "shift",
            Qt.Key_Down: "down",
            Qt.Key_Up: "up",
            Qt.Key_Left: "left",
            Qt.Key_Right: "right",
            Qt.Key_Tab: "tab",
            Qt.Key_F1: "f1",
            Qt.Key_F2: "f2",
            Qt.Key_F3: "f3",
            Qt.Key_F4: "f4",
            Qt.Key_F5: "f5",
            Qt.Key_F6: "f6",
            Qt.Key_F7: "f7",
            Qt.Key_F8: "f8",
            Qt.Key_F9: "f9",
            Qt.Key_F10: "f10",
            Qt.Key_A: "a",
            Qt.Key_B: "b",
            Qt.Key_C: "c",
            Qt.Key_D: "d",
            Qt.Key_E: "e",
            Qt.Key_F: "f",
            Qt.Key_G: "g",
            Qt.Key_H: "h",
            Qt.Key_I: "i",
            Qt.Key_J: "j",
            Qt.Key_K: "k",
            Qt.Key_L: "l",
            Qt.Key_M: "m",
            Qt.Key_N: "n",
            Qt.Key_O: "o",
            Qt.Key_P: "p",
            Qt.Key_Q: "q",
            Qt.Key_R: "r",
            Qt.Key_S: "s",
            Qt.Key_T: "t",
            Qt.Key_U: "u",
            Qt.Key_V: "v",
            Qt.Key_W: "w",
            Qt.Key_X: "x",
            Qt.Key_Y: "y",
            Qt.Key_Z: "z",
        }[event.key()]
    except KeyError:
        key = event.text().lower()
    try:
        key = {
            "\t": "tab",
            "\r": "enter",
            " ": "space",
        }[key]
    except KeyError:
        pass
    return key


class _MotionsInput(QLineEdit):
    def __init__(self, q: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__q = q

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        self.__q.put_nowait(Release(_extract_key(event)))
        # super().keyReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return
        self.__q.put_nowait(Press(_extract_key(event)))
        # super().keyPressEvent(event)


def _flush_queue(q: Queue) -> Queue:
    while not q.empty():
        q.get_nowait()
    return q


@attr.mutable
class _ComboInput:
    @attr.frozen
    class Matched:
        combo: Motions

    @attr.frozen
    class Mismatched:
        expected: Motions
        entered: Motions

    ReadyForNextCombo = object()

    @classmethod
    @contextlib.asynccontextmanager
    async def exists(cls, get_next_combo: Callable[[], Awaitable[NormalizedAction]]) -> AsyncIterator["_ComboInput"]:
        # TODO(zeronineseven): Disable event compression for all platforms
        widget = _MotionsInput(motions := Queue())
        widget.setReadOnly(True)
        widget.setDisabled(True)

        async def process_motions() -> NoReturn:
            while True:
                expected_combo, entered_combo = await get_next_combo(), deque()
                expected_len = len(expected_combo)

                _flush_queue(motions)
                self.currently_entered = tuple()
                widget.setText("")

                widget.setDisabled(False)
                pressed: int = 0
                for n in itertools.count():
                    m = await motions.get()
                    print(pretty_print_motion(m))
                    entered_combo.append(m)
                    widget.setText(pretty_print_motions(entered_combo))
                    self.currently_entered = currently_entered = tuple(entered_combo)
                    pressed += 1 if isinstance(m, Press) else -1
                    events.put_nowait(m)
                    if entered_combo[n] != expected_combo[n] or len(entered_combo) > expected_len:
                        events.put_nowait(cls.Mismatched(expected_combo, currently_entered))
                        break
                    elif len(entered_combo) == expected_len:
                        events.put_nowait(cls.Matched(expected_combo))
                        break
                # NOTE(zeronineseven): Wait until all pressed keys are released to avoid leaking them to next task.
                while pressed > 0:
                    pressed += 1 if isinstance(await motions.get(), Press) else -1
                events.put_nowait(self.ReadyForNextCombo)

                widget.setDisabled(True)

        async with AsyncExitStack() as acm:
            acm: AsyncExitStack

            widget.grabKeyboard()
            acm.callback(widget.releaseKeyboard)

            acm.callback(asyncio.create_task(process_motions()).cancel)

            self = cls(widget, events := Queue(), tuple())
            yield self

    widget: QWidget
    events: Queue[Union[Motion, Matched, Mismatched]]
    currently_entered: Motions


def _handle_exception(loop, context):
    # msg = context.get("exception", context["message"])
    # logging.error(f"Caught exception: {msg}")
    # logging.info("Shutting down...")
    asyncio.get_event_loop().stop()


@attr.frozen
class _Gui:
    @classmethod
    @contextlib.asynccontextmanager
    async def running(cls, combos: Deque[NormalizedAction]):
        window = QWidget()
        layout = QVBoxLayout()

        description_label = QLabel("Description")
        layout.addWidget(description_label)

        currently_entered_label = QLabel("")
        layout.addWidget(currently_entered_label)

        unprocessed_combos = Queue()
        async with AsyncExitStack() as acm:
            acm: AsyncExitStack

            combo_input: _ComboInput = await acm.enter_async_context(
                _ComboInput.exists(unprocessed_combos.get)
            )

            async def lifecycle() -> NoReturn:
                try:
                    while len(combos) != 0:
                        try:
                            current_action = combos.pop()
                        except IndexError:
                            break
                        current_combo = current_action.combo
                        description_label.setText(current_action.description)
                        currently_entered_label.setText("")
                        currently_entered_label.setStyleSheet("")
                        unprocessed_combos.put_nowait(current_combo)
                        pressed: int = 0
                        while True:
                            event = await combo_input.events.get()
                            if isinstance(event, Press):
                                pressed += 1
                            elif isinstance(event, Release):
                                pressed -= 1
                            else:
                                break
                            currently_entered_label.setText(
                                pretty_print_motions(current_combo[:len(combo_input.currently_entered)])
                            )
                        assert isinstance(event, (_ComboInput.Matched, _ComboInput.Mismatched))
                        currently_entered_label.setText(pretty_print_motions(current_combo))
                        if isinstance(event, _ComboInput.Matched):
                            currently_entered_label.setStyleSheet("background-color: green")
                            wait_for = 0.1
                        else:
                            currently_entered_label.setStyleSheet("background-color: red")
                            wait_for = 0.5
                        event, _ = await asyncio.gather(combo_input.events.get(),
                                                        asyncio.create_task(asyncio.sleep(wait_for)))
                        assert event is _ComboInput.ReadyForNextCombo
                except Exception as e:
                    raise e

            layout.addWidget(combo_input.widget)
            window.setLayout(layout)
            window.show()

            lifecycle_task = asyncio.create_task(lifecycle())

            QApplication.instance().aboutToQuit.connect(lifecycle_task.cancel)

            yield cls(asyncio.shield(lifecycle_task))

    done: Awaitable[None]


async def _main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(_handle_exception)
    loop.set_debug(__debug__)

    async with _Gui.running(random.sample(all_controls, min(15, len(all_controls)))) as gui:
        await gui.done
        print("Victory!")


qasync.run(_main())
