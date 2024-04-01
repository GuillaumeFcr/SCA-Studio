import json
import os
from PySide6 import QtCore
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QFileDialog

from app.utils.logging import handle, LOG_FILE


class MenubarUi:
    def __init__(self, app, ui, devices):
        self.app = app
        self.ui = ui
        self.devices = devices

        # Initialize doc
        docsMenu = {"docs": self.ui.menuHelp}
        for root, dirs, files in os.walk("docs"):
            for dir in dirs:
                path = os.path.join(root, dir)
                docsMenu[path] = docsMenu[root].addMenu(dir)
            for file in files:
                path = os.path.join(root, file)
                action = docsMenu[root].addAction(file)
                action.triggered.connect(lambda _=False, path=path: os.startfile(path))

        # Initialize signals
        self.ui.actionLight.triggered.connect(self.on_actionLight_click)
        self.ui.actionDark.triggered.connect(self.on_actionDark_click)
        self.ui.actionLoad.triggered.connect(self.on_actionLoad_click)
        self.ui.actionSave.triggered.connect(self.on_actionSave_click)
        self.ui.actionLogs.triggered.connect(self.on_actionLogs_click)
        self.ui.actionQuit.triggered.connect(self.on_actionQuit_click)

        # Set light mode by default
        self.ui.actionLight.trigger()

    def on_actionLight_click(self):
        palette = QPalette(QColor("#eeeeee"))
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor("#c8c8c8"),
        )
        self.app.setPalette(palette)

    def on_actionDark_click(self):
        palette = QPalette(QColor("#222222"))
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.WindowText,
            QColor("#505050"),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.ButtonText,
            QColor("#505050"),
        )
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.PlaceholderText,
            QColor("#505050"),
        )
        palette.setColor(QPalette.ColorRole.Base, QColor("#222222"))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor("#3a3a3a"))
        self.app.setPalette(palette)

    @handle("Load settings")
    def on_actionLoad_click(self):
        config = {}
        QApplication.restoreOverrideCursor()
        filename, _ = QFileDialog().getOpenFileName(dir="configs", filter="JSON config file (*.json)")
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        if not filename:
            return

        with open(filename, "r") as f:
            config = json.loads(f.read())

        self.ui.positioningXOffsetSpinBox.setValue(config["offset"]["x"])
        self.ui.positioningYOffsetSpinBox.setValue(config["offset"]["y"])
        self.ui.positioningZOffsetSpinBox.setValue(config["offset"]["z"])

        if "camera" in config and (self.devices.camera is None or not self.devices.camera.is_connected()):
            for i in range(self.ui.cameraDeviceComboBox.count()):
                if config["camera"]["name"] == self.ui.cameraDeviceComboBox.itemText(i):
                    self.ui.cameraDeviceComboBox.setCurrentIndex(i)
                    break
            self.ui.cameraAddressLineEdit.setText(config["camera"]["address"])
            self.ui.cameraConnectButton.click()
            self.devices.camera.set_settings(config["camera"]["settings"])
            self.ui.cameraSettingsGetButton.click()

        if "positioning" in config and (self.devices.positioning is None or not self.devices.positioning.is_connected()):
            for i in range(self.ui.positioningDeviceComboBox.count()):
                if config["positioning"]["name"] == self.ui.positioningDeviceComboBox.itemText(i):
                    self.ui.positioningDeviceComboBox.setCurrentIndex(i)
                    break
            self.ui.positioningAddressLineEdit.setText(config["positioning"]["address"])
            self.ui.positioningConnectButton.click()
            self.devices.positioning.set_settings(config["positioning"]["settings"])
            self.ui.positioningSettingsGetButton.click()

        if "oscilloscope" in config and (self.devices.oscilloscope is None or not self.devices.oscilloscope.is_connected()):
            for i in range(self.ui.oscilloscopeDeviceComboBox.count()):
                if config["oscilloscope"]["name"] == self.ui.oscilloscopeDeviceComboBox.itemText(i):
                    self.ui.oscilloscopeDeviceComboBox.setCurrentIndex(i)
                    break
            self.ui.oscilloscopeAddressLineEdit.setText(config["oscilloscope"]["address"])
            self.ui.oscilloscopeConnectButton.click()
            self.devices.oscilloscope.set_general(config["oscilloscope"]["general_settings"])
            self.devices.oscilloscope.set_trigger(config["oscilloscope"]["trigger_settings"])
            self.devices.oscilloscope.set_waveform(config["oscilloscope"]["waveform_settings"])
            for channel in self.devices.oscilloscope.channels:
                self.devices.oscilloscope.set_channel(channel, config["oscilloscope"]["channels"][channel]["settings"])
                if config["oscilloscope"]["channels"][channel]["enabled"]:
                    self.devices.oscilloscope.enable_channel(channel)
                else:
                    self.devices.oscilloscope.disable_channel(channel)
            self.ui.oscilloscopeSettingsGetButton.click()
            self.ui.oscilloscopeChannelsGetButton.click()

        if "board" in config and (self.devices.board is None or not self.devices.board.is_connected()):
            for i in range(self.ui.boardDeviceComboBox.count()):
                if config["board"]["name"] == self.ui.boardDeviceComboBox.itemText(i):
                    self.ui.boardDeviceComboBox.setCurrentIndex(i)
                    break
            self.ui.boardAddressLineEdit.setText(config["board"]["address"])
            self.ui.boardConnectButton.click()
            self.devices.board.set_settings(config["board"]["settings"])
            self.ui.boardSettingsGetButton.click()

    @handle("Save settings")
    def on_actionSave_click(self):
        config = {}

        config["offset"] = {
            "x": self.ui.positioningXOffsetSpinBox.value(),
            "y": self.ui.positioningYOffsetSpinBox.value(),
            "z": self.ui.positioningZOffsetSpinBox.value(),
        }

        if self.devices.camera is not None and self.devices.camera.is_connected():
            config["camera"] = {"name": self.devices.camera.name, "address": self.ui.cameraAddressLineEdit.text()}
            config["camera"]["settings"] = self.devices.camera.get_settings()

        if self.devices.positioning is not None and self.devices.positioning.is_connected():
            config["positioning"] = {"name": self.devices.positioning.name, "address": self.ui.positioningAddressLineEdit.text()}
            config["positioning"]["settings"] = self.devices.positioning.get_settings()

        if self.devices.oscilloscope is not None and self.devices.oscilloscope.is_connected():
            config["oscilloscope"] = {
                "name": self.devices.oscilloscope.name,
                "address": self.ui.oscilloscopeAddressLineEdit.text(),
            }
            config["oscilloscope"]["general_settings"] = self.devices.oscilloscope.get_general()
            config["oscilloscope"]["trigger_settings"] = self.devices.oscilloscope.get_trigger()
            config["oscilloscope"]["waveform_settings"] = self.devices.oscilloscope.get_waveform()
            config["oscilloscope"]["channels"] = {}
            for channel in self.devices.oscilloscope.channels:
                config["oscilloscope"]["channels"][channel] = {
                    "enabled": self.devices.oscilloscope.get_channel_state(channel),
                    "settings": self.devices.oscilloscope.get_channel(channel),
                }

        if self.devices.board is not None and self.devices.board.is_connected():
            config["board"] = {"name": self.devices.board.name, "address": self.ui.boardAddressLineEdit.text()}
            config["board"]["settings"] = self.devices.board.get_settings()

        QApplication.restoreOverrideCursor()
        filename, _ = QFileDialog().getSaveFileName(dir="configs", filter="JSON config file (*.json)")
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if filename:
            with open(filename, "w") as f:
                f.write(json.dumps(config, indent=4))

    def on_actionLogs_click(self):
        open(LOG_FILE, "a")
        os.startfile(LOG_FILE)

    def on_actionQuit_click(self):
        QtCore.QCoreApplication.instance().quit()
