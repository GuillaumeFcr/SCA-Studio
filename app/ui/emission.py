from enum import Enum

import numpy as np
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QMessageBox

from app.utils.devices import get_available_devices
from app.utils.drawing import (
    clear_draw,
    clear_grid,
    clear_marker,
    draw_grid,
    draw_line,
    draw_marker,
    draw_point,
    move_point,
    select_point,
)
from app.utils.logging import handle
from app.utils.positioning import homography, img_point, real_point

ViewMode = Enum("ViewMode", ["DRAG", "BOUNDARIES", "AREA_OF_INTEREST", "MOVE_TO_POINT"])


class EmissionUi:
    def __init__(self, ui, devices):
        self.ui = ui


