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
        self.ui.boardHelpButton_2.clicked.connect(self.on_board_help_clicked)
        self.ui.pushButton_connect_board.clicked.connect(self.on_connect_clicked)

        self.ui.pushButton_boardGetSettings.clicked.connect(self.on_get_settings_clicked)
        self.ui.pushButton_boardSetSettings.clicked.connect(self.on_apply_settings_clicked)

        self.ui.pushButton_outputDirectory.clicked.connect(self.on_select_output_clicked)

    # =========================
    # BOARD CONNECTION
    # =========================

    def on_boardDevice_change(self, i):
        self.devices.board = self.board_devices[i]()
        self.ui.lineEdit_address_board.setEnabled(True)
        self.ui.boardHelpButton_2.setEnabled(True)
        self.ui.pushButton_connect_board.setEnabled(True)

    @handle("Target Board connection")
    def on_connect_clicked(self):

        if not self.devices.board.is_connected():

            self.devices.board.connect(self.ui.lineEdit_address_board.text())

            # enable UI
            self.ui.pushButton_boardGetSettings.setEnabled(True)
            self.ui.pushButton_boardSetSettings.setEnabled(True)
            self.ui.plainTextEdit_board_settings.setEnabled(True)

            self.ui.comboBox_Board.setEnabled(False)
            self.ui.lineEdit_address_board.setEnabled(False)

            # auto refresh
            self.on_get_settings_clicked()

            self.ui.pushButton_connect_board.setText("Disconnect")

        else:

            self.devices.board.disconnect()

            # disable UI
            self.ui.pushButton_boardGetSettings.setEnabled(False)
            self.ui.pushButton_boardSetSettings.setEnabled(False)
            self.ui.plainTextEdit_board_settings.setEnabled(False)

            self.ui.comboBox_Board.setEnabled(True)
            self.ui.lineEdit_address_board.setEnabled(True)

            self.ui.plainTextEdit_board_settings.clear()

            self.ui.pushButton_connect_board.setText("Connect")

    @handle("Target Board help")
    def on_board_help_clicked(self):
        help = self.devices.board.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Target Board help", help).exec()


    # =========================
    # SETTINGS
    # =========================

    @handle("Target Board get settings")
    def on_get_settings_clicked(self):
        settings = self.devices.board.get_settings()
        self.ui.plainTextEdit_board_settings.setPlainText(settings)

    @handle("Target Board apply settings")
    def on_apply_settings_clicked(self):
        settings = self.ui.plainTextEdit_board_settings.toPlainText()
        self.devices.board.set_settings(settings)

    # =========================
    # OUTPUT DIRECTORY
    # =========================

    def on_select_output_clicked(self):
        self.out_directory = QFileDialog.getExistingDirectory(dir="measures")