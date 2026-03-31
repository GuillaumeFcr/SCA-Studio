from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog

from app.utils.devices import get_available_devices
from app.utils.logging import handle


class AttackUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices
        self.devices.board = None
        self.out_directory = ""

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

    def on_attackLaunch_clicked(self):
        if self.acquisition_thread is None:
            if self.devices.board is None or not self.devices.board.is_connected():
                raise Exception("Target Board must be connected before attack")
            if self.board_thread is not None:
                raise Exception("Target Board must be stopped before attack")
            if self.devices.injector is None or self.devices.injector.get_status()!=0 or not self.devices.injector.get_attackReady():
                raise Exception("Injector must be connected, ready and stopped before attack")
            if not self.out_directory:
                raise Exception("Output directory must be selected before attack")