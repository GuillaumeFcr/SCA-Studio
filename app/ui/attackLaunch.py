from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog

from app.utils.devices import get_available_devices
from app.utils.logging import handle


class AttackUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices
        self.devices.board = None
        self.out_directory = ""
        self.board_thread = None
        self.acquisition_thread = None
        self.displayed_data = []

        # =========================
        # DEVICES
        # =========================
        self.board_devices = get_available_devices("boards")
        for board in self.board_devices:
            self.ui.comboBox_Board.addItem(board.name)

        # =========================
        # SIGNALS
        # =========================
        self.ui.comboBox_Board.currentIndexChanged.connect(self.on_boardDevice_change)
        self.ui.boardHelpButton_2.clicked.connect(self.on_boardHelpButton_clicked)
        self.ui.pushButton_boardConnect.clicked.connect(self.on_boardConnect_clicked)

        self.ui.pushButton_boardGetSettings.clicked.connect(self.on_boardGetSettings_clicked)
        self.ui.pushButton_boardSetSettings.clicked.connect(self.on_boardSetSettings_clicked)

        self.ui.pushButton_outputDirectory.clicked.connect(self.on_outputDirectory_clicked)
        self.ui.pushButton_attackLaunch.clicked.connect(self.on_attackLaunch_clicked)

        self.ui.pushButton_AttackStop.clicked.connect(self.on_attackStop_clicked)

    # =========================
    # BOARD CONNECTION
    # =========================

    def on_boardDevice_change(self, i):
        self.devices.board = self.board_devices[i]()
        self.ui.lineEdit_address_board.setEnabled(True)
        self.ui.boardHelpButton_2.setEnabled(True)
        self.ui.pushButton_boardConnect.setEnabled(True)

    @handle("Target Board connection")
    def on_boardConnect_clicked(self):

        if not self.devices.board.is_connected():

            self.devices.board.connect(self.ui.lineEdit_address_board.text())

            # enable UI
            self.ui.pushButton_boardGetSettings.setEnabled(True)
            self.ui.pushButton_boardSetSettings.setEnabled(True)
            self.ui.plainTextEdit_board_settings.setEnabled(True)

            self.ui.comboBox_Board.setEnabled(False)
            self.ui.lineEdit_address_board.setEnabled(False)

            # auto refresh
            self.on_boardGetSettings_clicked()

            self.ui.pushButton_boardConnect.setText("Disconnect")

        else:

            self.devices.board.disconnect()

            # disable UI
            self.ui.pushButton_boardGetSettings.setEnabled(False)
            self.ui.pushButton_boardSetSettings.setEnabled(False)
            self.ui.plainTextEdit_board_settings.setEnabled(False)

            self.ui.comboBox_Board.setEnabled(True)
            self.ui.lineEdit_address_board.setEnabled(True)

            self.ui.plainTextEdit_board_settings.clear()

            self.ui.pushButton_boardConnect.setText("Connect")

    @handle("Target Board help")
    def on_boardHelpButton_clicked(self):
        help = self.devices.board.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Target Board help", help).exec()


    # =========================
    # SETTINGS
    # =========================

    @handle("Target Board get settings")
    def on_boardGetSettings_clicked(self):
        settings = self.devices.board.boardGetSettings()
        self.ui.plainTextEdit_board_settings.setPlainText(settings)

    @handle("Target Board apply settings")
    def on_boardSetSettings_clicked(self):
        settings = self.ui.plainTextEdit_board_settings.toPlainText()
        self.devices.board.set_settings(settings)

    # =========================
    # OUTPUT DIRECTORY
    # =========================

    def on_outputDirectory_clicked(self):
        self.out_directory = QFileDialog.getExistingDirectory(dir="measures")

    @handle("Attack launch")
    def on_attackLaunch_clicked(self):

        # =========================
        # Vérifications
        # =========================
        if self.devices.board is None or not self.devices.board.is_connected():
            QMessageBox.warning(self.ui, "Erreur", "Target Board must be connected")
            return

        if self.devices.injector is None:
            QMessageBox.warning(self.ui, "Erreur", "Injector not available")
            return

        if not self.devices.injector.get_attackReady():
            QMessageBox.warning(self.ui, "Erreur", "Injector not configured (Attack Parameters tab)")
            return

        if self.devices.injector.get_status() != 0:
            QMessageBox.warning(self.ui, "Erreur", "Injector must be stopped before attack")
            return

        if not self.out_directory:
            QMessageBox.warning(self.ui, "Erreur", "Select output directory")
            return

        # =========================
        # LANCEMENT ATTAQUE
        # =========================

        # Lancer la target
        self.devices.board.run()

        # Lancer l'injection
        self.devices.injector.send_injection()

        # Récupérer résultat board
        errors, info = self.devices.board.get()

        # =========================
        # Affichage résultat
        # =========================
        msg = f"Attack finished: {errors} " + ("errors" if errors > 1 else "error")
        if info:
            msg += f"\nInfo: {info}"

        self.ui.label_5.setText("1")
        self.ui.label_7.setText(msg)



    def on_attackStop_clicked(self): #à reverifier
        self.ui.pushButton_AttackStop.setEnabled(False)
        if self.acquisition_thread is not None:
            # Stop acquisition thread
            self.acquisition_thread.stop()
            self.acquisition_thread = None

    def acquisition_refresher(self, current, max, point):
        progress = int(current / max * 100)
        self.ui.progressBar_attack.setValue(progress)