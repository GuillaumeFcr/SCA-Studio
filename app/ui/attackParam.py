from enum import Enum

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMessageBox,
)

from app.utils.devices import get_available_devices
from app.utils.logging import handle

ViewMode = Enum("ViewMode", ["DRAG", "BOUNDARIES", "AREA_OF_INTEREST", "MOVE_TO_POINT"])


class AttackParamUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices

        # Initialisation du device Injector (comme dans emission.py)
        self.devices.injector = None
        self.injector_devices = get_available_devices("injectors")
        for injector in self.injector_devices:
            self.ui.injectorComboBox.addItem(injector.name)

        # INITIALISATION DE LA SCÈNE
        self.scene = QGraphicsScene()
        if hasattr(self.ui, "graphicsView"):
            self.ui.graphicsView.setScene(self.scene)

        # --- Connexion des signaux (Signaux -> Slots) ---

        # 1. Connexion (Groupbox Connexion)
        self.ui.pushButton_2.clicked.connect(
            self.on_connect_clicked
        )  # Bouton "Connect"
        self.ui.pushButton_3.clicked.connect(
            self.on_check_status_clicked
        )  # Bouton "Check Status"
        self.ui.injectorComboBox.currentIndexChanged.connect(
            self.on_injectorComboBox_change
        )
        # 2. Modes (radioPulseMode, radioBurstMode)
        self.ui.radioPulseMode.toggled.connect(self.on_radioPulseMode_toggled)
        self.ui.radioBurstMode.toggled.connect(self.on_radioBurstMode_toggled)

        self.ui.spinBox_PulseBurst.valueChanged.connect(self.on_pulse_burst_changed)
        self.ui.doubleSpinBox_BurstPeriod.valueChanged.connect(
            self.on_burst_period_changed
        )

        # 3. Fréquence / Période
        self.ui.radioFrequency.toggled.connect(self.on_radioFrequency_toggled)
        self.ui.radioPeriod.toggled.connect(self.on_radioPeriod_toggled)
        self.ui.doubleSpinBox_Frequency.valueChanged.connect(self.on_frequency_changed)

        # 4. Pulse Level (Slider)
        self.ui.horizontalSlider_Pluse_Level.valueChanged.connect(
            self.on_pulse_level_changed
        )

        # 5. Counter / Timer
        self.ui.radioDisableCounter.toggled.connect(self.on_counter_mode_changed)
        self.ui.radioPulseCounter.toggled.connect(self.on_counter_mode_changed)
        self.ui.radioTimer.toggled.connect(self.on_counter_mode_changed)

        self.ui.SpinBox_PulseCounter.valueChanged.connect(
            self.on_pulse_counter_val_changed
        )
        self.ui.doubleSpinBox_Timer.valueChanged.connect(self.on_timer_val_changed)

        # 6. Trigger Delay
        self.ui.doubleSpinBox_TriggerDelay.valueChanged.connect(
            self.on_trigger_delay_changed
        )

        # 7. Bouton Save / Action
        self.ui.pushButton_SaveEmit.clicked.connect(self.on_save_view_clicked)
        self.ui.pushButton_testPulse.clicked.connect(self.on_send_test_pulse_clicked)

        # --- RECUPERATION DES VALEURS ---
        # On utilise .value() pour les SpinBox et .isChecked() pour les Radio

        self.is_pulse = None
        self.pulses_per_burst = None
        self.burst_period = None
        self.freq = None
        self.level = None
        self.is_counter_timer = None  # 1 pour counter, 2 pour Timer, 0 pour Désactivé
        self.counter_value = None
        self.timer_value = None
        self.delay = self.ui.doubleSpinBox_TriggerDelay.value()
        self.command_sent = False
        self.connected = False

    def command_validity(self):
        # Vérifie si tous les paramètres nécessaires sont définis
        # Indique si la configuration actuelle est valide pour être envoyée à l'injecteur (tous les paramètres nécessaires sont définis)
        if (
            self.is_pulse is not None
            and self.freq is not None
            and self.level is not None
            and self.is_counter_timer is not None
            and self.counter_value is not None
            and self.timer_value is not None
            and (
                self.is_pulse
                or (self.pulses_per_burst is not None and self.burst_period is not None)
            )
        ):
            return True
        else:
            return False

    # --- Définition des fonctions (Slots) ---

    def on_injectorComboBox_change(self, i):
        self.devices.injector = self.injector_devices[i]()
        self.connected = False
        self.command_sent = False

    @handle("Connexion à l'injecteur")
    def on_connect_clicked(self):
        print("Tentative de connexion à l'injecteur")
        self.devices.injector.connect()
        self.connected = True

    @handle("Vérification du statut")
    def on_check_status_clicked(self):
        print("Vérification du statut du matériel...")
        print(self.devices.injector.get_status())

    @handle("Changement Mode d'émission")
    def on_radioPulseMode_toggled(self, checked):
        if checked:
            self.is_pulse = True
            self.command_sent = False
            print("Mode Pulse activé")

    @handle("Changement Mode Burst")
    def on_radioBurstMode_toggled(self, checked):
        if checked:
            self.is_pulse = False
            self.command_sent = False
            print("Mode Burst activé")

    @handle("Modification Pulse per Burst")
    def on_pulse_burst_changed(self, val):
        self.pulses_per_burst = val
        self.command_sent = False
        print(f"Pulse per burst : {val}")

    @handle("Modification Burst Period")
    def on_burst_period_changed(self, val):
        self.burst_period = val
        self.command_sent = False
        print(f"Burst period : {val} s")

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioFrequency_toggled(self, checked):
        if checked:
            frequ_temp = self.ui.doubleSpinBox_Frequency.value()
            self.freq = frequ_temp
            self.ui.doubleSpinBox_Frequency.setSuffix(" Hz")
            self.command_sent = False

    @handle("Changement Unité (Fréquence/Période)")
    def on_radioPeriod_toggled(self, checked):
        if checked:
            frequ_temp = self.ui.doubleSpinBox_Frequency.value()
            self.freq = 1 / frequ_temp if frequ_temp != 0 else 0
            self.ui.doubleSpinBox_Frequency.setSuffix(" s")
            self.command_sent = False

    @handle("Modification Valeur Fréquence/Période")
    def on_frequency_changed(self, val):
        self.command_sent = False
        if self.ui.radioFrequency.isChecked():
            self.freq = val
        elif self.ui.radioPeriod.isChecked():
            self.freq = 1 / val if val != 0 else 0

        print(f"Nouvelle valeur temporelle : {val}")

    @handle("Modification Niveau Pulse")
    def on_pulse_level_changed(self, val):
        self.level = (
            val * 10
        )  # on remap sur les increments de 10V de l'emetteur (5-50 du slider -> 50-500V)
        # Mettre à jour le label
        self.ui.pulse_level_value.setText(f"{val*10}V")
        self.command_sent = False

    @handle("Changement Mode Compteur/Timer")
    def on_counter_mode_changed(self, checked):
        if not checked:
            return
        self.command_sent = False
        if self.ui.radioDisableCounter.isChecked():
            self.is_counter_timer = False
            self.counter_value = 0  # par sécurité
            self.timer_value = 0
            print("Compteur désactivé")
        elif self.ui.radioPulseCounter.isChecked():
            self.is_counter_timer = 1
            self.counter_value = self.ui.SpinBox_PulseCounter.value()
            self.timer_value = 0
            print("Mode Compteur de pulses activé")
        elif self.ui.radioTimer.isChecked():
            self.is_counter_timer = 2
            self.timer_value = self.ui.doubleSpinBox_Timer.value()
            self.counter_value = 0
            print("Mode Timer activé")

    @handle("Modification Valeur Compteur")
    def on_pulse_counter_val_changed(self, val):
        self.counter_value = val
        self.command_sent = False

    @handle("Modification Valeur Timer")
    def on_timer_val_changed(self, val):
        self.timer_value = val
        self.command_sent = False

    @handle("Modification Trigger Delay")
    def on_trigger_delay_changed(self, val):
        self.delay = (
            10**-9 * self.ui.doubleSpinBox_TriggerDelay.value()
        )  # on ajuste pour que ce soit en secondes (val est en ns)
        self.command_sent = False

    @handle("Sauvegarde et affichage du signal")
    def on_save_view_clicked(self):
        print(
            self.is_pulse,
            self.freq,
            self.level,
            self.pulses_per_burst,
            self.burst_period,
            self.is_counter_timer,
            self.counter_value,
            self.timer_value,
            self.delay,
        )

        if not self.command_validity():
            print("Veuillez configurer tous les paramètres avant de sauvegarder.")
            return

        else:
            if self.connected:
                self.devices.injector.set_pulse_burst_mode(0 if self.is_pulse else 1)
                self.devices.injector.set_pulse_frequency(self.freq)
                self.devices.injector.set_pulse_level(self.level)
                self.devices.injector.set_pulses_per_burst(self.pulses_per_burst)
                self.devices.injector.set_burst_period(self.burst_period)
                self.devices.injector.set_counter_mode(self.is_counter_timer)
                self.devices.injector.set_pulse_burst_counter(self.counter_value)
                self.devices.injector.set_timer(self.timer_value)
                self.devices.injector.set_trigger_delay(self.delay)
                self.command_sent = True

            # Sécurité : vérifier si la scène existe
            if not hasattr(self, "scene"):
                self.scene = QGraphicsScene()
                self.ui.graphicsView.setScene(self.scene)

            print("Mise à jour de la prévisualisation...")

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

            if self.is_counter_timer == 2:  # Timer actif
                t_max = start_time + self.timer_value
            else:
                t_max = base_duration

            # =========================
            # 2. GÉNÉRATION DES PULSES
            # =========================

            if self.is_pulse:
                # train de pulses continu
                pulse_times = np.arange(start_time, t_max, pulse_period)

                # pulse counter
                if self.is_counter_timer == 1:
                    pulse_times = pulse_times[: self.counter_value]

            else:
                # génération des bursts
                burst_times = np.arange(start_time, t_max, self.burst_period)

                # burst counter
                if self.is_counter_timer == 1:
                    burst_times = burst_times[: self.counter_value]

                pulse_times = []

                for b in burst_times:
                    for i in range(self.pulses_per_burst):
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

    @handle("Envoi d'un signal de test à l'injecteur")
    def on_send_test_pulse_clicked(self):
        if not self.command_sent:
            print(
                "Veuillez configurer tous les paramètres, connecter un injecteur et valider la commande avant d'envoyer un signal de test."
            )
            return

        else:
            # Pense à mettre un timer de 5secondes dans cette emission pour faire le test

            print(
                "Envoi d'un signal de test à l'injecteur avec les paramètres suivants :"
            )
            print(
                self.is_pulse,
                self.freq,
                self.level,
                self.delay,
                self.is_counter_timer,
                self.counter_value,
                self.timer_value,
            )
            self.devices.injector.send_injection()
            return
