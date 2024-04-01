from PySide6.QtWidgets import QApplication, QMessageBox

from app.utils.devices import get_available_devices
from app.utils.logging import handle


class OscilloscopeUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices
        self.devices.oscilloscope = None

        # Get available devices
        self.oscilloscope_devices = get_available_devices("oscilloscopes")
        for oscilloscope in self.oscilloscope_devices:
            self.ui.oscilloscopeDeviceComboBox.addItem(oscilloscope.name)

        # Initialize signals
        self.ui.oscilloscopeDeviceComboBox.currentIndexChanged.connect(self.on_oscilloscopeDeviceComboBox_change)
        self.ui.oscilloscopeHelpButton.clicked.connect(self.on_oscilloscopeHelpButton_click)
        self.ui.oscilloscopeConnectButton.clicked.connect(self.on_oscilloscopeConnectButton_click)

        self.ui.oscilloscopeChannelsComboBox.currentIndexChanged.connect(self.on_oscilloscopeChannelsComboBox_change)
        self.ui.oscilloscopeChannelsCheckBox.stateChanged.connect(self.on_oscilloscopeChannelsCheckBox_change)
        self.ui.oscilloscopeChannelsGetButton.clicked.connect(self.on_oscilloscopeChannelsGetButton_click)
        self.ui.oscilloscopeChannelsApplyButton.clicked.connect(self.on_oscilloscopeChannelsApplyButton_click)

        self.ui.oscilloscopeSettingsComboBox.currentIndexChanged.connect(self.on_oscilloscopeSettingsComboBox_change)
        self.ui.oscilloscopeSettingsGetButton.clicked.connect(self.on_oscilloscopeSettingsGetButton_click)
        self.ui.oscilloscopeSettingsApplyButton.clicked.connect(self.on_oscilloscopeSettingsApplyButton_click)

        self.ui.oscilloscopeCmdLineEdit.returnPressed.connect(self.on_oscilloscopeCmdLineEdit_enter)

    def on_oscilloscopeDeviceComboBox_change(self, i):
        self.devices.oscilloscope = self.oscilloscope_devices[i]()
        self.ui.oscilloscopeAddressLineEdit.setEnabled(True)
        self.ui.oscilloscopeHelpButton.setEnabled(True)
        self.ui.oscilloscopeConnectButton.setEnabled(True)

    @handle("Oscilloscope help")
    def on_oscilloscopeHelpButton_click(self):
        help = self.devices.oscilloscope.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Oscilloscope help", help).exec()

    @handle("Oscilloscope connection")
    def on_oscilloscopeConnectButton_click(self):
        if not self.devices.oscilloscope.is_connected():
            self.devices.oscilloscope.connect(self.ui.oscilloscopeAddressLineEdit.text())
            self.ui.oscilloscopeChannelsGroupBox.setEnabled(True)
            self.ui.oscilloscopeSettingsGroupBox.setEnabled(True)
            self.ui.oscilloscopeCmdLineEdit.setEnabled(True)
            self.ui.oscilloscopeDeviceComboBox.setEnabled(False)
            self.ui.oscilloscopeAddressLineEdit.setEnabled(False)
            for channel in self.devices.oscilloscope.channels:
                self.ui.oscilloscopeChannelsComboBox.addItem(channel)
            self.ui.oscilloscopeSettingsGetButton.click()
            self.ui.oscilloscopeConnectButton.setText("Disconnect")
        else:
            self.devices.oscilloscope.disconnect()
            self.ui.oscilloscopeChannelsGroupBox.setEnabled(False)
            self.ui.oscilloscopeSettingsGroupBox.setEnabled(False)
            self.ui.oscilloscopeCmdLineEdit.setEnabled(False)
            self.ui.oscilloscopeDeviceComboBox.setEnabled(True)
            self.ui.oscilloscopeAddressLineEdit.setEnabled(True)
            self.ui.oscilloscopeCmdLineEdit.clear()
            self.ui.oscilloscopeChannelsComboBox.clear()
            self.ui.oscilloscopeChannelsTextEdit.clear()
            self.ui.oscilloscopeSettingsComboBox.setCurrentIndex(0)
            self.ui.oscilloscopeSettingsTextEdit.clear()
            self.ui.oscilloscopeConnectButton.setText("Connect")

    def on_oscilloscopeChannelsComboBox_change(self, i):
        self.ui.oscilloscopeChannelsGetButton.click()

    @handle("Oscilloscope set channel status")
    def on_oscilloscopeChannelsCheckBox_change(self, state):
        channel = self.devices.oscilloscope.channels[self.ui.oscilloscopeChannelsComboBox.currentIndex()]
        if state == 2:
            self.devices.oscilloscope.enable_channel(channel)
        else:
            self.devices.oscilloscope.disable_channel(channel)

    @handle("Oscilloscope get channel settings")
    def on_oscilloscopeChannelsGetButton_click(self):
        channel = self.devices.oscilloscope.channels[self.ui.oscilloscopeChannelsComboBox.currentIndex()]
        enabled = self.devices.oscilloscope.get_channel_state(channel)
        self.ui.oscilloscopeChannelsCheckBox.blockSignals(True)
        self.ui.oscilloscopeChannelsCheckBox.setChecked(enabled)
        self.ui.oscilloscopeChannelsCheckBox.blockSignals(False)
        self.ui.oscilloscopeChannelsTextEdit.setPlainText(self.devices.oscilloscope.get_channel(channel))

    @handle("Oscilloscope set channel settings")
    def on_oscilloscopeChannelsApplyButton_click(self):
        channel = self.devices.oscilloscope.channels[self.ui.oscilloscopeChannelsComboBox.currentIndex()]
        settings = self.ui.oscilloscopeChannelsTextEdit.toPlainText()
        self.devices.oscilloscope.set_channel(channel, settings)

    def on_oscilloscopeSettingsComboBox_change(self, i):
        self.ui.oscilloscopeSettingsGetButton.click()

    @handle("Oscilloscope get settings")
    def on_oscilloscopeSettingsGetButton_click(self):
        settings_type = self.ui.oscilloscopeSettingsComboBox.currentIndex()
        settings = ""
        if settings_type == 0:
            settings = self.devices.oscilloscope.get_general()
        elif settings_type == 1:
            settings = self.devices.oscilloscope.get_trigger()
        elif settings_type == 2:
            settings = self.devices.oscilloscope.get_waveform()
        self.ui.oscilloscopeSettingsTextEdit.setPlainText(settings)

    @handle("Oscilloscope apply settings")
    def on_oscilloscopeSettingsApplyButton_click(self):
        settings_type = self.ui.oscilloscopeSettingsComboBox.currentIndex()
        settings = self.ui.oscilloscopeSettingsTextEdit.toPlainText()
        if settings_type == 0:
            settings = self.devices.oscilloscope.set_general(settings)
        elif settings_type == 1:
            settings = self.devices.oscilloscope.set_trigger(settings)
        elif settings_type == 2:
            settings = self.devices.oscilloscope.set_waveform(settings)

    @handle("Oscilloscope raw command")
    def on_oscilloscopeCmdLineEdit_enter(self):
        self.devices.oscilloscope.send(self.ui.oscilloscopeCmdLineEdit.text())
        res = self.devices.oscilloscope.read()
        QMessageBox(
            QMessageBox.Information,
            "Oscilloscope raw command",
            "Result: " + str(res),
        ).exec()
        self.ui.oscilloscopeCmdLineEdit.clear()
