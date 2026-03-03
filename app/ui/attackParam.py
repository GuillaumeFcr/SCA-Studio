from enum import Enum

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
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


        # INITIALISATION DE LA SCÈNE
        self.scene = QGraphicsScene()
        if hasattr(self.ui, 'graphicsView'):
            self.ui.graphicsView.setScene(self.scene)

        # --- Connexion des signaux (Signaux -> Slots) ---

        # 1. Connexion (Groupbox Connexion)
        self.ui.pushButton_2.clicked.connect(self.on_connect_clicked)      # Bouton "Connect"
        self.ui.pushButton_3.clicked.connect(self.on_check_status_clicked) # Bouton "Check Status"

        # 2. Modes (radioPulseMode, radioBurstMode)
        self.ui.radioPulseMode.toggled.connect(self.on_radioPulseMode_toggled)
        self.ui.radioBurstMode.toggled.connect(self.on_radioBurstMode_toggled)

        # 3. Fréquence / Période
        self.ui.radioFrequency.toggled.connect(self.on_radioFrequency_toggled)
        self.ui.radioPeriod.toggled.connect(self.on_radioPeriod_toggled)
        self.ui.doubleSpinBox_Frequency.valueChanged.connect(self.on_frequency_changed)

        # 4. Pulse Level (Slider)
        self.ui.horizontalSlider_Pluse_Level.valueChanged.connect(self.on_pulse_level_changed)

        # 5. Counter / Timer
        self.ui.radioDisableCounter.toggled.connect(self.on_counter_mode_changed)
        self.ui.radioPulseCounter.toggled.connect(self.on_counter_mode_changed)
        self.ui.radioTimer.toggled.connect(self.on_counter_mode_changed)

        self.ui.doubleSpinBox_PulseCounter.valueChanged.connect(self.on_pulse_counter_val_changed)
        self.ui.doubleSpinBox_Timer.valueChanged.connect(self.on_timer_val_changed)

        # 6. Trigger Delay
        self.ui.doubleSpinBox_TriggerDelay.valueChanged.connect(self.on_trigger_delay_changed)

        # 7. Bouton Save / Action
        self.ui.pushButton_SaveEmit.clicked.connect(self.on_save_view_clicked)

    # --- Définition des fonctions (Slots) ---

    @handle("Connexion à l'injecteur")
    def on_connect_clicked(self):
        # Récupère le device sélectionné dans le comboBox
        device_name = self.ui.comboBox.currentText()
        print(f"Tentative de connexion à : {device_name}")
        # Insérez votre logique de connexion ici

    @handle("Vérification du statut")
    def on_check_status_clicked(self):
        print("Vérification du statut du matériel...")

    @handle("Changement Mode d'émission")
    def on_radioPulseMode_toggled(self, checked):
        if checked:
            print("Mode Pulse activé")

    @handle("Changement Mode Burst")
    def on_radioBurstMode_toggled(self, checked):
        if checked:
            print("Mode Burst activé")

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioFrequency_toggled(self, checked):
        if checked:
            self.ui.doubleSpinBox_Frequency.setSuffix(" Hz")

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioPeriod_toggled(self, checked):
        if checked:
            self.ui.doubleSpinBox_Frequency.setSuffix(" s")

    @handle("Modification Valeur Fréquence/Période")
    def on_frequency_changed(self, val):
        print(f"Nouvelle valeur temporelle : {val}")

    @handle("Modification Niveau Pulse")
    def on_pulse_level_changed(self, val):
        # val est un int venant du Slider
        if self.devices.injector:
            self.devices.injector.set_pulse_level_index(val)
        print(val)

    @handle("Changement Mode Compteur/Timer")
    def on_counter_mode_changed(self, checked):
        if not checked: return

        if self.ui.radioDisableCounter.isChecked():
            print("Compteur désactivé")
        elif self.ui.radioPulseCounter.isChecked():
            print("Mode Compteur de pulses activé")
        elif self.ui.radioTimer.isChecked():
            print("Mode Timer activé")

    @handle("Modification Valeur Compteur")
    def on_pulse_counter_val_changed(self, val):
        pass

    @handle("Modification Valeur Timer")
    def on_timer_val_changed(self, val):
        pass

    @handle("Modification Trigger Delay")
    def on_trigger_delay_changed(self, val):
        if self.devices.injector:
            self.devices.injector.set_trigger_delay(val)

    @handle("Sauvegarde et affichage du signal")
    def on_save_view_clicked(self):
        # Sécurité : vérifier si la scène existe
        if not hasattr(self, 'scene'):
            self.scene = QGraphicsScene()
            self.ui.graphicsView.setScene(self.scene)

        print("Mise à jour de la prévisualisation...")

        # --- RECUPERATION DES VALEURS ---
        # On utilise .value() pour les SpinBox et .isChecked() pour les Radio
        freq = self.ui.doubleSpinBox_Frequency.value()
        level = self.ui.horizontalSlider_Pluse_Level.value()
        delay = self.ui.doubleSpinBox_TriggerDelay.value()
        is_pulse = self.ui.radioPulseMode.isChecked()

        # --- CRÉATION DU PLOT MATPLOTLIB ---
        # On crée une figure (ajustez figsize pour que ça rentre bien)
        fig, ax = plt.subplots(figsize=(5, 3), dpi=80)

        # Simulation d'un signal simple (Square wave)
        # On définit une échelle de temps (ex: 2 cycles)
        t_max = (1/freq) * 2 if freq > 0 else 0.1
        t = np.linspace(0, t_max, 500)

        # Logique de dessin : un créneau qui commence après le delay
        # (Conversion arbitraire du délai pour l'exemple)
        start_time = delay / 1000
        signal = np.where((t > start_time) & (t < start_time + t_max/4), level, 0)

        ax.plot(t, signal, 'r-', lw=2)
        ax.set_title(f"Preview: {'Pulse' if is_pulse else 'Burst'}")
        ax.set_xlabel("Temps (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True)
        fig.tight_layout()

        # --- AFFICHAGE DANS QT ---
        # On transforme la figure en widget
        canvas = FigureCanvas(fig)

        # On nettoie la scène et on ajoute le nouveau canvas
        self.scene.clear()
        self.scene.addWidget(canvas)

        # On force le graphicsView à ajuster sa taille au contenu
        self.ui.graphicsView.fitInView(self.scene.itemsBoundingRect())

        # Important : Fermer la figure matplotlib pour libérer la mémoire RAM
        plt.close(fig)