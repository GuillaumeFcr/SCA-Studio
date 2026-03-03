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

class AttackParamUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices

        # Initialisation du device Injector (comme dans emission.py)
        self.devices.injector = None
        self.injector_devices = get_available_devices("injectors")
        if self.injector_devices:
            self.devices.injector = self.injector_devices[0]()
            # Si vous avez un ComboBox pour choisir l'injecteur :
            # for injector in self.injector_devices:
            #     self.ui.injectorDeviceComboBox.addItem(injector.name)

        # --- Connexion des signaux (Signaux -> Slots) ---

        # Modes d'émission
        self.ui.pulseModeRadio.toggled.connect(self.on_pulseModeRadio_toggled)
        self.ui.cwModeRadio.toggled.connect(self.on_cwModeRadio_toggled)

        # Paramètres de fréquence et niveau
        self.ui.frequencySpinBox.valueChanged.connect(self.on_frequencySpinBox_changed)
        self.ui.pulseLevelSlider.valueChanged.connect(self.on_pulseLevelSlider_changed)

        # Modes de comptage / Timer
        self.ui.disableCounterRadio.toggled.connect(self.on_disableCounterRadio_toggled)
        self.ui.pulseCounterRadio.toggled.connect(self.on_pulseCounterRadio_toggled)
        self.ui.timerRadio.toggled.connect(self.on_timerRadio_toggled)

        # Valeurs numériques
        self.ui.pulseCounterSpinBox.valueChanged.connect(self.on_pulseCounterSpinBox_changed)
        self.ui.triggerDelayEdit.textChanged.connect(self.on_triggerDelayEdit_changed)

        # Bouton d'action principal (ex: Lancement de l'attaque)
        # Note : Vérifiez si le bouton s'appelle 'attackRunButton' dans votre UI
        if hasattr(self.ui, 'attackRunButton'):
            self.ui.attackRunButton.clicked.connect(self.on_attackRunButton_clicked)

    # --- Définition des fonctions (Slots) ---

    @handle("Changement mode Pulse")
    def on_pulseModeRadio_toggled(self, checked):
        if checked:
            print("ezojbfceo")
            # Insérer le code pour activer le mode pulse sur l'injecteur
            pass

    @handle("Changement mode Continu (CW)")
    def on_cwModeRadio_toggled(self, checked):
        if checked:
            # Insérer le code pour activer le mode continu
            pass

    @handle("Modification Fréquence")
    def on_frequencySpinBox_changed(self, val):
        # Logique pour mettre à jour la fréquence
        pass

    @handle("Modification Niveau Pulse")
    def on_pulseLevelSlider_changed(self, val):
        if self.devices.injector:
            self.devices.injector.set_pulse_level_index(val)

    @handle("Désactivation Compteur")
    def on_disableCounterRadio_toggled(self, checked):
        if checked and self.devices.injector:
            self.devices.injector.set_counter_mode(0)

    @handle("Activation Compteur de Pulses")
    def on_pulseCounterRadio_toggled(self, checked):
        if checked and self.devices.injector:
            self.devices.injector.set_counter_mode(1)

    @handle("Modification du nombre de pulses")
    def on_pulseCounterSpinBox_changed(self, val):
        if self.devices.injector:
            self.devices.injector.set_pulse_counter(val)

    @handle("Activation Timer")
    def on_timerRadio_toggled(self, checked):
        if checked and self.devices.injector:
            self.devices.injector.set_counter_mode(2)

    @handle("Modification du délai de trigger")
    def on_triggerDelayEdit_changed(self, text):
        try:
            val = int(text)
            if self.devices.injector:
                self.devices.injector.set_trigger_delay(val)
        except ValueError:
            pass

    @handle("Lancement de l'attaque")
    def on_attackRunButton_clicked(self):
        # Code pour démarrer l'émission ou l'attaque
        print("Lancement de l'attaque avec les paramètres définis.")