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
        self.devices = devices
        self.devices.injector = None

        # Get available devices
        self.injector_devices = get_available_devices("injectors")
        self.devices.injector = self.injector_devices[0]()
        # for injector in self.injector_devices:
        #     self.ui.injectorDeviceComboBox.addItem(injector.name)

        # Initialize signals
        self.ui.pulseModeRadio.toggled.connect(self.on_pulseModeRadio_toggled)

        self.ui.frequencyRadio.toggled.connect(self.on_frequencyRadio_toggled)
        self.ui.frequencySpinBox.valueChanged.connect(self.on_frequencySpinBox_changed)
        self.ui.frequencySlider.valueChanged.connect(self.on_frequencySlider_changed)

        self.ui.pulseLevelSpinBox.valueChanged.connect(self.on_pulseLevelSpinBox_changed)
        self.ui.pulseLevelSlider.valueChanged.connect(self.on_pulseLevelSlider_changed)

        self.ui.disableCounterRadio.toggled.connect(self.on_disableCounterRadio_toggled)
        self.ui.pulseCounterRadio.toggled.connect(self.on_pulseCounterRadio_toggled)
        self.ui.pulseCounterSpinBox.valueChanged.connect(self.on_pulseCounterSpinBox_changed)
        self.ui.timerRadio.toggled.connect(self.on_timerRadio_toggled)
        self.ui.timerEdit.timeChanged.connect(self.on_timerEdit_changed)

        self.ui.triggerDelayEdit.textChanged.connect(self.on_triggerDelayEdit_changed)

        self.ui.startPulsingButton.clicked.connect(self.on_startPulsingButton_click)
        self.ui.singlePulseButton.clicked.connect(self.on_singlePulseButton_click)

    def on_pulseModeRadio_toggled(self, checked):
        self.devices.injector.set_pulse_burst_mode(1-self.devices.injector.get_pulse_burst_mode())

    def on_frequencyRadio_toggled(self, checked):
        val=1/val #a verifier


    def on_frequencySpinBox_changed(self, val):
        pass

    def on_frequencySlider_changed(self, val):
        pass

    def on_pulseLevelSpinBox_changed(self, val):
        pass

    def on_pulseLevelSlider_changed(self, val):
        self.devices.injector.set_pulse_level_index(val) #a changer

    def on_disableCounterRadio_toggled(self, checked):
        if checked:
            self.devices.injector.set_counter_mode(0)

    def on_pulseCounterRadio_toggled(self, checked):
        if checked:
            self.devices.injector.set_counter_mode(1)

    def on_pulseCounterSpinBox_changed(self, val):
        self.devices.injector.set_pulse_counter(val)

    def on_timerRadio_toggled(self, checked):
        if checked:
            self.devices.injector.set_counter_mode(2)

    def on_timerEdit_changed(self, time):
        self.devices.injector.set_timer(time) #a verifier

    def on_triggerDelayEdit_changed(self, text):
        self.devices.injector.set_trigger_delay(int(text))

    @handle("Emission start pulsing")
    def on_startPulsingButton_click(self):
        self.devices.injector.set_control(1)
        self.devices.injector.send_injection()

    @handle("Emission single pulse")
    def on_singlePulseButton_click(self):
        self.devices.injector.set_control(2)
        self.devices.injector.send_injection()


