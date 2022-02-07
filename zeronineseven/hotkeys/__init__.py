import enum
from enum import Enum
from itertools import chain

from ssost.hotkeys.pycharm import all_controls as pycharm_controls
from ssost.hotkeys.edge import all_controls as edge_controls

__all__ = "all_controls",

all_controls = (*pycharm_controls, *edge_controls)
