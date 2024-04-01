from PySide6.QtWidgets import QApplication, QMessageBox, QFileDialog

from app.utils.acquisition import (
    parse_out_directory,
    run_acquisition,
    run_target_board,
    stop_acquisition,
    stop_target_board,
)
from app.utils.devices import get_available_devices
from app.utils.drawing import display_data, hide_data
from app.utils.logging import handle
from app.utils.positioning import img_point, real_point, xy_by_box_number


class AcquisitionUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices
        self.devices.board = None
        self.out_directory = ""
        self.board_thread = None
        self.acquisition_thread = None
        self.displayed_data = []

        # Get available devices
        self.board_devices = get_available_devices("boards")
        for board in self.board_devices:
            self.ui.boardDeviceComboBox.addItem(board.name)

        # Initialize signals
        self.ui.boardDeviceComboBox.currentIndexChanged.connect(self.on_boardDeviceComboBox_change)
        self.ui.boardHelpButton.clicked.connect(self.on_boardHelpButton_click)
        self.ui.boardConnectButton.clicked.connect(self.on_boardConnectButton_click)
        self.ui.boardSettingsGetButton.clicked.connect(self.on_boardSettingsGetButton_click)
        self.ui.boardSettingsApplyButton.clicked.connect(self.on_boardSettingsApplyButton_click)
        self.ui.boardRunButton.clicked.connect(self.on_boardRunButton_click)
        self.ui.boardCmdLineEdit.returnPressed.connect(self.on_boardCmdLineEdit_enter)

        self.ui.selectOutButton.clicked.connect(self.on_selectOutButton_click)
        self.ui.acquisitionAreaNSpinBox.valueChanged.connect(self.on_acquisitionAreaNSpinBox_change)

        self.ui.displayDataGroupBox.toggled.connect(self.on_displayDataGroupBox_change)
        self.ui.displayActivityRadioButton.toggled.connect(self.on_displayActivityRadioButton_change)
        self.ui.displayErrorRadioButton.toggled.connect(self.on_displayErrorRadioButton_change)

        self.ui.acquisitionRunButton.clicked.connect(self.on_acquisitionRunButton_click)

    def on_boardDeviceComboBox_change(self, i):
        self.devices.board = self.board_devices[i]()
        self.ui.boardAddressLineEdit.setEnabled(True)
        self.ui.boardHelpButton.setEnabled(True)
        self.ui.boardConnectButton.setEnabled(True)

    @handle("Target Board help")
    def on_boardHelpButton_click(self):
        help = self.devices.board.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Target Board help", help).exec()

    @handle("Target Board connection")
    def on_boardConnectButton_click(self):
        if not self.devices.board.is_connected():
            self.devices.board.connect(self.ui.boardAddressLineEdit.text())
            self.ui.boardSettingsGetButton.setEnabled(True)
            self.ui.boardSettingsApplyButton.setEnabled(True)
            self.ui.boardSettingsTextEdit.setEnabled(True)
            self.ui.boardRunWidget.setEnabled(True)
            self.ui.boardCmdLineEdit.setEnabled(True)
            self.ui.boardDeviceComboBox.setEnabled(False)
            self.ui.boardAddressLineEdit.setEnabled(False)
            self.ui.boardSettingsGetButton.click()
            self.ui.boardConnectButton.setText("Disconnect")
        else:
            self.devices.board.disconnect()
            self.ui.boardSettingsGetButton.setEnabled(False)
            self.ui.boardSettingsApplyButton.setEnabled(False)
            self.ui.boardSettingsTextEdit.setEnabled(False)
            self.ui.boardRunWidget.setEnabled(False)
            self.ui.boardCmdLineEdit.setEnabled(False)
            self.ui.boardDeviceComboBox.setEnabled(True)
            self.ui.boardAddressLineEdit.setEnabled(True)
            self.ui.boardCmdLineEdit.clear()
            self.ui.boardSettingsTextEdit.clear()
            self.ui.boardConnectButton.setText("Connect")

    @handle("Target Board get settings")
    def on_boardSettingsGetButton_click(self):
        settings = self.devices.board.get_settings()
        self.ui.boardSettingsTextEdit.setPlainText(settings)

    @handle("Target Board apply settings")
    def on_boardSettingsApplyButton_click(self):
        settings = self.ui.boardSettingsTextEdit.toPlainText()
        self.devices.board.set_settings(settings)

    @handle("Target Board run")
    def on_boardRunButton_click(self):
        if self.board_thread is None and not self.ui.boardLoopCheckBox.isChecked():
            self.devices.board.run()
            errors, info = self.devices.board.get()
            msg = f"Target Board finished: {errors} " + ("errors" if errors > 1 else "error") + " occured during execution"
            msg += f"\nInfo: {info}" if info else ""
            QMessageBox(QMessageBox.Information, "Target Board run", msg).exec()

        elif self.board_thread is None:
            stop_refresh = self.ui.boardRunButton.click
            abort_on_error = self.ui.boardStopOnErrorCheckBox.isChecked()
            self.board_thread = run_target_board(self.devices.board, stop_refresh, abort_on_error)
            self.ui.boardConnectButton.setEnabled(False)
            self.ui.boardSettingsApplyButton.setEnabled(False)
            self.ui.boardLoopCheckBox.setEnabled(False)
            self.ui.boardStopOnErrorCheckBox.setEnabled(False)
            self.ui.boardRunButton.setText("Stop target board")

        else:
            errors = stop_target_board(self.devices.board, *self.board_thread)
            msg = f"Target Board finished: {errors} " + ("errors" if errors > 1 else "error") + " occured during execution"
            QMessageBox(QMessageBox.Information, "Target Board run", msg).exec()
            self.board_thread = None
            self.ui.boardConnectButton.setEnabled(True)
            self.ui.boardSettingsApplyButton.setEnabled(True)
            self.ui.boardLoopCheckBox.setEnabled(True)
            self.ui.boardStopOnErrorCheckBox.setEnabled(True)
            self.ui.boardRunButton.setText("Run target board")

    @handle("Target Board raw command")
    def on_boardCmdLineEdit_enter(self):
        self.devices.board.send(self.ui.boardCmdLineEdit.text())
        res = self.devices.board.read()
        QMessageBox(QMessageBox.Information, "Board raw command", "Result: " + str(res)).exec()
        self.ui.boardCmdLineEdit.clear()

    def on_selectOutButton_click(self):
        self.out_directory = QFileDialog.getExistingDirectory(dir="measures")
        self.update_displayed_data()

    def on_acquisitionAreaNSpinBox_change(self, val):
        if not self.ui.positioningDrawAreaButton.isChecked():  # trigger positioningDrawAreaButton twice to redraw the grid
            self.ui.positioningDrawAreaButton.click()
            self.ui.positioningDrawAreaButton.click()

    def on_displayDataGroupBox_change(self, checked):
        self.update_displayed_data()

    def on_displayActivityRadioButton_change(self, checked):
        self.update_displayed_data()

    def on_displayErrorRadioButton_change(self, checked):
        self.update_displayed_data()

    @handle("Acquisition run")
    def on_acquisitionRunButton_click(self):
        if self.acquisition_thread is None:
            if self.devices.positioning is None or not self.devices.positioning.is_connected():
                raise Exception("Positioning System must be connected before acquisition")
            if self.devices.oscilloscope is None or not self.devices.oscilloscope.is_connected():
                raise Exception("Oscilloscope must be connected before acquisition")
            if self.devices.board is None or not self.devices.board.is_connected():
                raise Exception("Target Board must be connected before acquisition")
            if self.board_thread is not None:
                raise Exception("Target Board must be stopped before acquisition")
            if not self.out_directory:
                raise Exception("Output directory must be selected before acquisition")

            points = []
            if self.ui.mapAreaCheckBox.isChecked():
                if self.devices.img is None or not self.devices.grid:
                    raise Exception("Area of interest must be defined on a photo first")
                n = self.ui.acquisitionAreaNSpinBox.value()
                h, w = self.devices.img.height(), self.devices.img.width()
                for i in range(n**2):
                    x, y = xy_by_box_number(i, n, self.devices.grid)
                    x_real, y_real = real_point(
                        x,
                        y,
                        w,
                        h,
                        self.devices.positioning.X_BOUNDS,
                        self.devices.positioning.Y_BOUNDS,
                        self.ui.positioningXOffsetSpinBox.value(),
                        self.ui.positioningYOffsetSpinBox.value(),
                    )
                    points.append((x_real, y_real))
            else:
                x, y, _ = self.devices.positioning.locate()
                points.append((x, y))

            runs_per_measure = self.ui.acquisitionCountSpinBox.value()
            self.acquisition_thread = run_acquisition(
                self.devices.board,
                self.devices.oscilloscope,
                self.devices.positioning,
                self.acquisition_refresher,
                points,
                runs_per_measure,
                self.out_directory,
            )
            self.ui.targetBoardBox.setEnabled(False)
            self.ui.acquisitionGroupBox.setEnabled(False)
            self.ui.oscilloscopeTab.setEnabled(False)
            self.ui.positioningSettingsWidget.setEnabled(False)
            self.ui.positioningMoveWidget.setEnabled(False)
            self.ui.cameraAdvancedSettingsGroupBox.setEnabled(False)
            self.ui.positioningAdvancedSettingsGroupBox.setEnabled(False)
            self.ui.positioningCommandWidget.setEnabled(False)
            if not self.ui.positioningSwitchButton.isChecked():
                self.ui.positioningSwitchButton.click()
            for button in [
                self.ui.positioningBoundariesButton,
                self.ui.positioningDrawAreaButton,
                self.ui.positioningMoveToButton,
            ]:
                if button.isChecked():
                    button.click()
            self.ui.positioningToolsWidget.setEnabled(False)
            self.ui.acquisitionProgressBar.setEnabled(True)
            self.ui.acquisitionRunButton.setText("Stop acquisition")

        else:
            stop_acquisition(self.devices.board, *self.acquisition_thread)
            self.acquisition_thread = None
            self.ui.targetBoardBox.setEnabled(True)
            self.ui.acquisitionGroupBox.setEnabled(True)
            self.ui.oscilloscopeTab.setEnabled(True)
            self.ui.positioningSettingsWidget.setEnabled(True)
            self.ui.positioningMoveWidget.setEnabled(True)
            self.ui.cameraAdvancedSettingsGroupBox.setEnabled(True)
            self.ui.positioningAdvancedSettingsGroupBox.setEnabled(True)
            self.ui.positioningCommandWidget.setEnabled(True)
            self.ui.positioningToolsWidget.setEnabled(True)
            self.ui.acquisitionProgressBar.setEnabled(False)
            self.ui.acquisitionRunButton.setText("Start acquisition")

            self.update_displayed_data()

    def acquisition_refresher(self, current, max, point):
        progress = int(current / max * 100)
        self.ui.acquisitionProgressBar.setValue(progress)

        x, y = point
        self.ui.positioningMoveWidget.setEnabled(True)
        self.ui.positioningXCoordSpinBox.setValue(x - self.ui.positioningXOffsetSpinBox.value())
        self.ui.positioningYCoordSpinBox.setValue(y - self.ui.positioningYOffsetSpinBox.value())
        self.ui.positioningRefreshButton.click()
        self.ui.positioningMoveWidget.setEnabled(False)

        if current == max:
            self.ui.acquisitionRunButton.click()

    @handle("Update displayed data")
    def update_displayed_data(self):
        if not self.out_directory or self.devices.img is None or self.devices.positioning is None:
            return

        hide_data(self.ui.cameraDisplay.scene(), self.displayed_data)

        if self.ui.displayDataGroupBox.isChecked():
            data = parse_out_directory(self.out_directory, errors_data=self.ui.displayErrorRadioButton.isChecked())
            data_img = {}
            for x_real, y_real in data.keys():
                h, w = self.devices.img.height(), self.devices.img.width()
                x_img, y_img = img_point(
                    x_real,
                    y_real,
                    w,
                    h,
                    self.devices.positioning.X_BOUNDS,
                    self.devices.positioning.Y_BOUNDS,
                    self.ui.positioningXOffsetSpinBox.value(),
                    self.ui.positioningYOffsetSpinBox.value(),
                )
                data_img[(x_img, y_img)] = data[(x_real, y_real)]
            display_data(self.ui.cameraDisplay.scene(), data_img, self.displayed_data)
