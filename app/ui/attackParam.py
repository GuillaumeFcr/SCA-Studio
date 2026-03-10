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

        self.ui.spinBox_PulseBurst.valueChanged.connect(self.on_pulse_burst_changed)
        self.ui.doubleSpinBox_BurstPeriod.valueChanged.connect(self.on_burst_period_changed)

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

        self.ui.SpinBox_PulseCounter.valueChanged.connect(self.on_pulse_counter_val_changed)
        self.ui.doubleSpinBox_Timer.valueChanged.connect(self.on_timer_val_changed)

        # 6. Trigger Delay
        self.ui.doubleSpinBox_TriggerDelay.valueChanged.connect(self.on_trigger_delay_changed)

        # 7. Bouton Save / Action
        self.ui.pushButton_SaveEmit.clicked.connect(self.on_save_view_clicked)



                # --- RECUPERATION DES VALEURS ---
        # On utilise .value() pour les SpinBox et .isChecked() pour les Radio

        self.is_pulse = None
        self.pulse_per_burst = None
        self.burst_period = None
        self.freq = None
        self.level = None
        self.is_counter_timer = None  # 2 pour counter, 3 pour Timer, False pour Désactivé
        self.counter_timer_value = None  # Valeur du compteur ou timer
        self.delay = self.ui.doubleSpinBox_TriggerDelay.value()

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
            self.is_pulse = self.ui.radioPulseMode.isChecked() #True si est coche, sinon False
            print("Mode Pulse activé")

    @handle("Changement Mode Burst")
    def on_radioBurstMode_toggled(self, checked):
        if checked:
            self.is_pulse = not self.ui.radioBurstMode.isChecked()
            print("Mode Burst activé")

    @handle("Modification Pulse per Burst")
    def on_pulse_burst_changed(self, val):
        self.pulse_per_burst = val
        print(f"Pulse per burst : {val}")

    @handle("Modification Burst Period")
    def on_burst_period_changed(self, val):
        self.burst_period = val
        print(f"Burst period : {val} s")

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioFrequency_toggled(self, checked):
        if checked:
            frequ_temp = self.ui.doubleSpinBox_Frequency.value()
            self.freq = frequ_temp
            self.ui.doubleSpinBox_Frequency.setSuffix(" Hz")

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioPeriod_toggled(self, checked):
        if checked:
            frequ_temp = self.ui.doubleSpinBox_Frequency.value()
            self.freq = 1 / frequ_temp if frequ_temp != 0 else 0
            self.ui.doubleSpinBox_Frequency.setSuffix(" s")

    @handle("Modification Valeur Fréquence/Période")
    def on_frequency_changed(self, val):
        if self.ui.radioFrequency.isChecked():
            self.freq = val
        elif self.ui.radioPeriod.isChecked():
            self.freq = 1 / val if val != 0 else 0

        print(f"Nouvelle valeur temporelle : {val}")

    @handle("Modification Niveau Pulse")
    def on_pulse_level_changed(self, val):

        self.level = val*10  #on remap sur les increments de 10V de l'emetteur (5-50 du slider -> 50-500V)
        # Mettre à jour le label
        self.ui.pulse_level_value.setText(f"{val*10}V")

        # val est un int venant du Slider
        if self.devices.injector:
            self.devices.injector.set_pulse_level_index(val*10)
        print(val*10)

    @handle("Changement Mode Compteur/Timer")
    def on_counter_mode_changed(self, checked):
        if not checked: return

        if self.ui.radioDisableCounter.isChecked():
            self.is_counter_timer = False
            self.counter_timer_value = 0 #par sécurité
            print("Compteur désactivé")
        elif self.ui.radioPulseCounter.isChecked():
            self.is_counter_timer = 2
            self.counter_timer_value = self.ui.SpinBox_PulseCounter.value()
            print("Mode Compteur de pulses activé")
        elif self.ui.radioTimer.isChecked():
            self.is_counter_timer = 3
            self.counter_timer_value = self.ui.doubleSpinBox_Timer.value()
            print("Mode Timer activé")

    @handle("Modification Valeur Compteur")
    def on_pulse_counter_val_changed(self, val):
        self.counter_timer_value = val
        pass

    @handle("Modification Valeur Timer")
    def on_timer_val_changed(self, val):
        self.counter_timer_value = val
        pass

    @handle("Modification Trigger Delay")
    def on_trigger_delay_changed(self, val):
        self.delay = 10**-9 * self.ui.doubleSpinBox_TriggerDelay.value() # on ajuste pour que ce soit en secondes (val est en ns)
        if self.devices.injector:
            self.devices.injector.set_trigger_delay(val)

    @handle("Sauvegarde et affichage du signal")
    def on_save_view_clicked(self):

        print(self.is_pulse, self.freq, self.level,
            self.pulse_per_burst, self.burst_period,
            self.is_counter_timer, self.counter_timer_value, self.delay)

        if (self.is_pulse is None or
            self.freq is None or
            self.level is None or
            self.is_counter_timer is None or
            self.counter_timer_value is None or
            (not self.is_pulse and (self.pulse_per_burst is None or self.burst_period is None))):
            print("Veuillez configurer tous les paramètres avant de sauvegarder.")
            return

        else :
            # Sécurité : vérifier si la scène existe
            if not hasattr(self, 'scene'):
                self.scene = QGraphicsScene()
                self.ui.graphicsView.setScene(self.scene)

            print("Mise à jour de la prévisualisation...")

            # --- CRÉATION DU PLOT MATPLOTLIB ---

            # --- CRÉATION DU PLOT MATPLOTLIB ---

            fig, ax = plt.subplots(figsize=(5, 3), dpi=80)

            pulse_width = 4e-9
            pulse_period = 1 / self.freq if self.freq > 0 else 0
            start_time = self.delay

            # =========================
            # 1. DÉTERMINATION DE t_max
            # =========================

            if self.is_pulse:
                base_duration = 10 * pulse_period
            else:
                base_duration = 2 * self.burst_period

            if self.is_counter_timer == 3:  # Timer actif
                t_max = start_time + self.counter_timer_value
            else:
                t_max = base_duration


            # =========================
            # 2. GÉNÉRATION DES PULSES
            # =========================

            if self.is_pulse:

                # train de pulses continu
                pulse_times = np.arange(start_time, t_max, pulse_period)

                # pulse counter
                if self.is_counter_timer == 2:
                    pulse_times = pulse_times[:self.counter_timer_value]


            else:

                # génération des bursts
                burst_times = np.arange(start_time, t_max, self.burst_period)

                # burst counter
                if self.is_counter_timer == 2:
                    burst_times = burst_times[:self.counter_timer_value]

                pulse_times = []

                for b in burst_times:
                    for i in range(self.pulse_per_burst):

                        tp = b + i * pulse_period

                        if tp > t_max:
                            break

                        pulse_times.append(tp)

                pulse_times = np.array(pulse_times)


            # =========================
            # 3. FILTRAGE FINAL (timer)
            # =========================

            pulse_times = pulse_times[pulse_times <= t_max]


            # =========================
            # 4. PLOT
            # =========================

            ax.vlines(pulse_times, 0, self.level, linewidth=2)

            ax.set_xlim(0, t_max)
            ax.set_ylim(0, self.level * 1.2)

            ax.set_title(f"Preview: {'Pulse' if self.is_pulse else 'Burst'}")
            ax.set_xlabel("Temps (s)")
            ax.set_ylabel("Amplitude")

            ax.grid(True)
            fig.tight_layout()
            # # --- CRÉATION DU PLOT MATPLOTLIB ---
            # # On crée une figure (ajustez figsize pour que ça rentre bien)
            # fig, ax = plt.subplots(figsize=(5, 3), dpi=80)

            # # Simulation d'un signal simple (Square wave)
            # # On définit une échelle de temps (ex: 2 cycles)
            # t_max = (1/self.freq) * 2 if self.freq > 0 else 0.1
            # t = np.linspace(0, t_max, 500)

            # # Logique de dessin : un créneau qui commence après le delay
            # # (Conversion arbitraire du délai pour l'exemple)
            # start_time = self.delay / 1000
            # signal = np.where((t > start_time) & (t < start_time + t_max/4), self.level, 0)

            # ax.plot(t, signal, 'r-', lw=2)
            # ax.set_title(f"Preview: {'Pulse' if self.is_pulse else 'Burst'}")
            # ax.set_xlabel("Temps (s)")
            # ax.set_ylabel("Amplitude")
            # ax.grid(True)
            # fig.tight_layout()

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