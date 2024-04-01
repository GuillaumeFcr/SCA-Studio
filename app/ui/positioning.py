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


class PositioningUi:
    def __init__(self, ui, devices):
        self.ui = ui
        self.devices = devices
        self.devices.camera = None
        self.devices.positioning = None
        self.devices.img = None
        self.view_mode = ViewMode.DRAG
        self.marker = []
        self.points, self.paths = [], []
        self.grid = []
        self.selected_point = None

        # Get available devices
        self.camera_devices = get_available_devices("cameras")
        self.positioning_devices = get_available_devices("positioning")
        for camera in self.camera_devices:
            self.ui.cameraDeviceComboBox.addItem(camera.name)
        for positioning in self.positioning_devices:
            self.ui.positioningDeviceComboBox.addItem(positioning.name)

        # Default view is camera view
        self.ui.cameraAdvancedSettingsGroupBox.hide()
        self.ui.positioningAdvancedSettingsGroupBox.hide()

        # Initialize signals
        self.ui.cameraDeviceComboBox.currentIndexChanged.connect(self.on_cameraDeviceComboBox_change)
        self.ui.cameraHelpButton.clicked.connect(self.on_cameraHelpButton_click)
        self.ui.cameraConnectButton.clicked.connect(self.on_cameraConnectButton_click)
        self.ui.takePhotoButton.clicked.connect(self.on_takePhotoButton_click)

        self.ui.positioningDeviceComboBox.currentIndexChanged.connect(self.on_positioningDeviceComboBox_change)
        self.ui.positioningHelpButton.clicked.connect(self.on_positioningHelpButton_click)
        self.ui.positioningConnectButton.clicked.connect(self.on_positioningConnectButton_click)
        self.ui.positioningCalibrateButton.clicked.connect(self.on_positioningCalibrateButton_click)

        self.ui.cameraSettingsGetButton.clicked.connect(self.on_cameraSettingsGetButton_click)
        self.ui.cameraSettingsApplyButton.clicked.connect(self.on_cameraSettingsApplyButton_click)
        self.ui.positioningSettingsGetButton.clicked.connect(self.on_positioningSettingsGetButton_click)
        self.ui.positioningSettingsApplyButton.clicked.connect(self.on_positioningSettingsApplyButton_click)

        self.ui.cameraCmdLineEdit.returnPressed.connect(self.on_cameraCmdLineEdit_enter)
        self.ui.positioningCmdLineEdit.returnPressed.connect(self.on_positioningCmdLineEdit_enter)

        self.ui.positioningSwitchButton.clicked.connect(self.on_positioningSwitchButton_click)
        self.ui.positioningBoundariesButton.clicked.connect(self.on_positioningBoundariesButton_click)
        self.ui.positioningDrawAreaButton.clicked.connect(self.on_positioningDrawAreaButton_click)
        self.ui.positioningMoveToButton.clicked.connect(self.on_positioningMoveToButton_click)

        self.ui.positioningXpButton.clicked.connect(self.on_positioningXpButton_click)
        self.ui.positioningXmButton.clicked.connect(self.on_positioningXmButton_click)
        self.ui.positioningYpButton.clicked.connect(self.on_positioningYpButton_click)
        self.ui.positioningYmButton.clicked.connect(self.on_positioningYmButton_click)
        self.ui.positioningZpButton.clicked.connect(self.on_positioningZpButton_click)
        self.ui.positioningZmButton.clicked.connect(self.on_positioningZmButton_click)
        self.ui.positioningXCoordSpinBox.valueChanged.connect(self.on_positioningXCoordSpinBox_changed)
        self.ui.positioningYCoordSpinBox.valueChanged.connect(self.on_positioningYCoordSpinBox_changed)
        self.ui.positioningZCoordSpinBox.valueChanged.connect(self.on_positioningZCoordSpinBox_changed)
        self.ui.positioningRefreshButton.clicked.connect(self.on_positioningRefreshButton_click)
        self.ui.positioningMoveButton.clicked.connect(self.on_positioningMoveButton_click)

    def on_cameraDeviceComboBox_change(self, i):
        self.devices.camera = self.camera_devices[i]()
        self.ui.cameraAddressLineEdit.setEnabled(True)
        self.ui.cameraHelpButton.setEnabled(True)
        self.ui.cameraConnectButton.setEnabled(True)

    @handle("Camera help")
    def on_cameraHelpButton_click(self):
        help = self.devices.camera.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Camera help", help).exec()

    @handle("Camera connection")
    def on_cameraConnectButton_click(self):
        if not self.devices.camera.is_connected():
            self.devices.camera.connect(self.ui.cameraAddressLineEdit.text())
            self.ui.takePhotoButton.setEnabled(True)
            self.ui.cameraCmdLineEdit.setEnabled(True)
            self.ui.cameraAdvancedSettingsGroupBox.setEnabled(True)
            self.ui.cameraDeviceComboBox.setEnabled(False)
            self.ui.cameraAddressLineEdit.setEnabled(False)
            self.ui.cameraSettingsGetButton.click()
            self.ui.cameraConnectButton.setText("Disconnect")
        else:
            self.devices.camera.disconnect()
            self.ui.takePhotoButton.setEnabled(False)
            self.ui.cameraCmdLineEdit.setEnabled(False)
            self.ui.cameraAdvancedSettingsGroupBox.setEnabled(False)
            self.ui.cameraDeviceComboBox.setEnabled(True)
            self.ui.cameraAddressLineEdit.setEnabled(True)
            self.ui.cameraCmdLineEdit.clear()
            self.ui.cameraSettingsTextEdit.clear()
            self.ui.cameraConnectButton.setText("Connect")

    @handle("Camera photo")
    def on_takePhotoButton_click(self):
        self.display(self.devices.camera.get())

    @handle("Camera get settings")
    def on_cameraSettingsGetButton_click(self):
        settings = self.devices.camera.get_settings()
        self.ui.cameraSettingsTextEdit.setPlainText(settings)

    @handle("Camera apply settings")
    def on_cameraSettingsApplyButton_click(self):
        settings = self.ui.cameraSettingsTextEdit.toPlainText()
        self.devices.camera.set_settings(settings)

    @handle("Camera raw command")
    def on_cameraCmdLineEdit_enter(self):
        self.devices.camera.send(self.ui.cameraCmdLineEdit.text())
        res = self.devices.camera.read()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Camera raw command", "Result: " + str(res)).exec()
        self.ui.cameraCmdLineEdit.clear()

    def on_positioningDeviceComboBox_change(self, i):
        self.devices.positioning = self.positioning_devices[i]()
        self.ui.positioningAddressLineEdit.setEnabled(True)
        self.ui.positioningHelpButton.setEnabled(True)
        self.ui.positioningConnectButton.setEnabled(True)

    @handle("Positioning System help")
    def on_positioningHelpButton_click(self):
        help = self.devices.positioning.help()
        QApplication.restoreOverrideCursor()
        QMessageBox(QMessageBox.Information, "Positioning System help", help).exec()

    @handle("Positioning System connection")
    def on_positioningConnectButton_click(self):
        if not self.devices.positioning.is_connected():
            self.devices.positioning.connect(self.ui.positioningAddressLineEdit.text())
            self.ui.positioningCalibrateButton.setEnabled(True)
            self.ui.positioningCmdLineEdit.setEnabled(True)
            self.ui.positioningAdvancedSettingsGroupBox.setEnabled(True)
            self.ui.positioningBoundariesButton.setEnabled(True)
            self.ui.positioningDrawAreaButton.setEnabled(True)
            self.ui.positioningMoveToButton.setEnabled(True)
            self.ui.positioningMoveWidget.setEnabled(True)
            self.ui.positioningDeviceComboBox.setEnabled(False)
            self.ui.positioningAddressLineEdit.setEnabled(False)
            self.ui.positioningSettingsGetButton.click()
            self.ui.positioningConnectButton.setText("Disconnect")
        else:
            self.devices.positioning.disconnect()
            self.ui.positioningCalibrateButton.setEnabled(False)
            self.ui.positioningCmdLineEdit.setEnabled(False)
            self.ui.positioningAdvancedSettingsGroupBox.setEnabled(False)
            self.ui.positioningMoveWidget.setEnabled(False)
            self.ui.positioningXCoordSpinBox.setValue(0)
            self.ui.positioningYCoordSpinBox.setValue(0)
            self.ui.positioningZCoordSpinBox.setValue(0)
            for button in [
                self.ui.positioningBoundariesButton,
                self.ui.positioningDrawAreaButton,
                self.ui.positioningMoveToButton,
            ]:
                button.setAutoExclusive(False)
                button.setChecked(False)
                button.setAutoExclusive(True)
                button.setEnabled(False)
            self.ui.positioningDeviceComboBox.setEnabled(True)
            self.ui.positioningAddressLineEdit.setEnabled(True)
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.OpenHandCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.view_mode = ViewMode.DRAG
            clear_draw(self.ui.cameraDisplay.scene(), self.points, self.paths)
            clear_marker(self.ui.cameraDisplay.scene(), self.marker)
            self.ui.positioningCmdLineEdit.clear()
            self.ui.positioningSettingsTextEdit.clear()
            self.ui.positioningConnectButton.setText("Connect")

    @handle("Positioning System calibration")
    def on_positioningCalibrateButton_click(self):
        QApplication.restoreOverrideCursor()
        alertmsg = "Calibration may cause the positioning system to move. Please remove any additional hardware from the positioning system before proceeding."
        ret = QMessageBox(
            QMessageBox.Warning,
            "Positioning System settings",
            alertmsg,
            QMessageBox.Ok | QMessageBox.Cancel,
        ).exec()
        if ret == QMessageBox.Ok:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            self.devices.positioning.calibrate()
            self.devices.positioning.wait()
            self.ui.positioningRefreshButton.click()

    @handle("Positioning System get settings")
    def on_positioningSettingsGetButton_click(self):
        settings = self.devices.positioning.get_settings()
        self.ui.positioningSettingsTextEdit.setPlainText(settings)

    @handle("Positioning System set settings")
    def on_positioningSettingsApplyButton_click(self):
        settings = self.ui.positioningSettingsTextEdit.toPlainText()
        self.devices.positioning.set_settings(settings)

    @handle("Positioning System raw command")
    def on_positioningCmdLineEdit_enter(self):
        self.devices.positioning.send(self.ui.positioningCmdLineEdit.text())
        res = self.devices.positioning.read()
        QApplication.restoreOverrideCursor()
        QMessageBox(
            QMessageBox.Information,
            "Positioning System raw command",
            "Result: " + str(res),
        ).exec()
        self.ui.positioningCmdLineEdit.clear()

    def on_positioningSwitchButton_click(self):
        if self.ui.cameraDisplay.isVisible():
            self.ui.cameraDisplay.hide()
            self.ui.cameraAdvancedSettingsGroupBox.show()
            self.ui.positioningAdvancedSettingsGroupBox.show()
        else:
            self.ui.cameraDisplay.show()
            self.ui.cameraAdvancedSettingsGroupBox.hide()
            self.ui.positioningAdvancedSettingsGroupBox.hide()

    @handle("Positioning System set boundaries")
    def on_positioningBoundariesButton_click(self):
        if self.view_mode == ViewMode.BOUNDARIES:
            self.view_mode = ViewMode.DRAG
            self.ui.positioningBoundariesButton.setAutoExclusive(False)
            self.ui.positioningBoundariesButton.setChecked(False)
            self.ui.positioningBoundariesButton.setAutoExclusive(True)
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.OpenHandCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

            points = [p[1] for p in self.points]
            if len(points) == 4 and self.selected_point is None:
                width_real = self.devices.positioning.X_BOUNDS[1] - self.devices.positioning.X_BOUNDS[0]
                height_real = self.devices.positioning.Y_BOUNDS[1] - self.devices.positioning.Y_BOUNDS[0]
                wh_ratio = width_real / height_real
                h, w = self.devices.img.height(), self.devices.img.width()
                ch = int(self.devices.img.bytesPerLine() / w)
                data = np.frombuffer(self.devices.img.constBits(), np.uint8).reshape((h, w, ch))
                img = homography(data, points, wh_ratio)
                h, w = img.shape[:2]
                qimage = QtGui.QImage(img, w, h, ch * w, self.devices.img.format())
                self.display(qimage)
                self.show_marker()
            else:
                clear_draw(self.ui.cameraDisplay.scene(), self.points, self.paths)
                self.selected_point = None

        else:
            if self.view_mode == ViewMode.AREA_OF_INTEREST:
                self.ui.positioningDrawAreaButton.click()
            elif self.view_mode == ViewMode.MOVE_TO_POINT:
                self.ui.positioningMoveToButton.click()
            self.view_mode = ViewMode.BOUNDARIES
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.CrossCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.NoDrag)
            clear_draw(self.ui.cameraDisplay.scene(), self.points, self.paths)
            clear_grid(self.ui.cameraDisplay.scene(), self.grid)
            self.devices.grid.clear()
            self.ui.positioningBoundariesButton.setChecked(True)

    def on_positioningDrawAreaButton_click(self):
        if self.view_mode == ViewMode.AREA_OF_INTEREST:
            self.view_mode = ViewMode.DRAG
            self.ui.positioningDrawAreaButton.setAutoExclusive(False)
            self.ui.positioningDrawAreaButton.setChecked(False)
            self.ui.positioningDrawAreaButton.setAutoExclusive(True)
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.OpenHandCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            if len(self.points) == 4 and self.selected_point is None:
                self.devices.grid = [p for _, p in self.points]
                draw_grid(
                    self.ui.cameraDisplay.scene(),
                    self.devices.grid,
                    self.ui.acquisitionAreaNSpinBox.value(),
                    self.grid,
                )
            else:
                clear_draw(self.ui.cameraDisplay.scene(), self.points, self.paths)
                clear_grid(self.ui.cameraDisplay.scene(), self.grid)
                self.selected_point = None

        else:
            if self.view_mode == ViewMode.BOUNDARIES:
                self.ui.positioningBoundariesButton.click()
            elif self.view_mode == ViewMode.MOVE_TO_POINT:
                self.ui.positioningMoveToButton.click()
            self.view_mode = ViewMode.AREA_OF_INTEREST
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.CrossCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.NoDrag)
            clear_grid(self.ui.cameraDisplay.scene(), self.grid)
            self.devices.grid.clear()
            self.ui.positioningDrawAreaButton.setChecked(True)

    def on_positioningMoveToButton_click(self):
        if self.view_mode == ViewMode.MOVE_TO_POINT:
            self.view_mode = ViewMode.DRAG
            self.ui.positioningMoveToButton.setAutoExclusive(False)
            self.ui.positioningMoveToButton.setChecked(False)
            self.ui.positioningMoveToButton.setAutoExclusive(True)
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.OpenHandCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            if self.view_mode == ViewMode.BOUNDARIES:
                self.ui.positioningBoundariesButton.click()
            elif self.view_mode == ViewMode.AREA_OF_INTEREST:
                self.ui.positioningDrawAreaButton.click()
            self.view_mode = ViewMode.MOVE_TO_POINT
            self.ui.cameraDisplay.setCursor(Qt.CursorShape.CrossCursor)
            self.ui.cameraDisplay.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.ui.positioningMoveToButton.setChecked(True)

    @handle("Positioning System move")
    def on_positioningXpButton_click(self):
        dx = 0.1
        self.devices.positioning.move(x=dx, absolute=False)
        xval = dx + self.ui.positioningXCoordSpinBox.value()
        self.ui.positioningXCoordSpinBox.setValue(xval)
        self.show_marker()

    @handle("Positioning System move")
    def on_positioningXmButton_click(self):
        dx = -0.1
        self.devices.positioning.move(x=dx, absolute=False)
        xval = dx + self.ui.positioningXCoordSpinBox.value()
        self.ui.positioningXCoordSpinBox.setValue(xval)
        self.show_marker()

    @handle("Positioning System move")
    def on_positioningYpButton_click(self):
        dy = 0.1
        self.devices.positioning.move(y=dy, absolute=False)
        yval = dy + self.ui.positioningYCoordSpinBox.value()
        self.ui.positioningYCoordSpinBox.setValue(yval)
        self.show_marker()

    @handle("Positioning System move")
    def on_positioningYmButton_click(self):
        dy = -0.1
        self.devices.positioning.move(y=dy, absolute=False)
        yval = dy + self.ui.positioningYCoordSpinBox.value()
        self.ui.positioningYCoordSpinBox.setValue(yval)
        self.show_marker()

    @handle("Positioning System move")
    def on_positioningZpButton_click(self):
        dz = 0.1
        self.devices.positioning.move(z=dz, absolute=False)
        zval = dz + self.ui.positioningZCoordSpinBox.value()
        self.ui.positioningZCoordSpinBox.setValue(zval)

    @handle("Positioning System move")
    def on_positioningZmButton_click(self):
        dz = -0.1
        self.devices.positioning.move(z=dz, absolute=False)
        zval = dz + self.ui.positioningZCoordSpinBox.value()
        self.ui.positioningZCoordSpinBox.setValue(zval)

    def on_positioningXCoordSpinBox_changed(self, val):
        min, max = self.devices.positioning.X_BOUNDS
        if val > max:
            self.ui.positioningXCoordSpinBox.setValue(max)
        if val < min:
            self.ui.positioningXCoordSpinBox.setValue(min)

    def on_positioningYCoordSpinBox_changed(self, val):
        min, max = self.devices.positioning.Y_BOUNDS
        if val > max:
            self.ui.positioningYCoordSpinBox.setValue(max)
        if val < min:
            self.ui.positioningYCoordSpinBox.setValue(min)

    def on_positioningZCoordSpinBox_changed(self, val):
        min, max = self.devices.positioning.Z_BOUNDS
        if val > max:
            self.ui.positioningZCoordSpinBox.setValue(max)
        if val < min:
            self.ui.positioningZCoordSpinBox.setValue(min)

    @handle("Positioning System refresh position")
    def on_positioningRefreshButton_click(self):
        # prevent to interact with the Positioning System if refreshed from the acquisition thread
        if not self.ui.acquisitionProgressBar.isEnabled():
            x_real, y_real, z_real = self.devices.positioning.locate()
            self.ui.positioningXCoordSpinBox.setValue(x_real - self.ui.positioningXOffsetSpinBox.value())
            self.ui.positioningYCoordSpinBox.setValue(y_real - self.ui.positioningYOffsetSpinBox.value())
            self.ui.positioningZCoordSpinBox.setValue(z_real - self.ui.positioningZOffsetSpinBox.value())

        self.show_marker()

    @handle("Positioning System move")
    def on_positioningMoveButton_click(self):
        x_real = self.ui.positioningXCoordSpinBox.value() + self.ui.positioningXOffsetSpinBox.value()
        y_real = self.ui.positioningYCoordSpinBox.value() + self.ui.positioningYOffsetSpinBox.value()
        z_real = self.ui.positioningZCoordSpinBox.value() + self.ui.positioningZOffsetSpinBox.value()
        self.devices.positioning.move(x=x_real, y=y_real, z=z_real, absolute=True)
        self.show_marker()

    def show_marker(self):
        if self.devices.img is not None:
            x_real = self.ui.positioningXCoordSpinBox.value() + self.ui.positioningXOffsetSpinBox.value()
            y_real = self.ui.positioningYCoordSpinBox.value() + self.ui.positioningYOffsetSpinBox.value()
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
            draw_marker(self.ui.cameraDisplay.scene(), self.marker, x_img, y_img)

    def display(self, qimage):
        clear_marker(self.ui.cameraDisplay.scene(), self.marker)
        clear_draw(self.ui.cameraDisplay.scene(), self.points, self.paths)
        clear_grid(self.ui.cameraDisplay.scene(), self.grid)
        item = QGraphicsPixmapItem(QtGui.QPixmap.fromImage(qimage))
        scene = cameraScene(self)
        self.ui.cameraDisplay.setScene(scene)
        self.ui.cameraDisplay.fitInView(item, Qt.KeepAspectRatio)
        scene.addItem(item)
        self.devices.img = qimage


class cameraScene(QGraphicsScene):
    def __init__(self, positioning_ui):
        super().__init__()
        self.positioning_ui = positioning_ui

    def wheelEvent(self, event):
        zoomFactor = 1.05
        if event.delta() < 0:
            zoomFactor = 0.95
        self.positioning_ui.ui.cameraDisplay.scale(zoomFactor, zoomFactor)
        event.accept()

    def mousePressEvent(self, event):
        point = (event.scenePos().x(), event.scenePos().y())

        if self.positioning_ui.view_mode == ViewMode.DRAG or self.positioning_ui.devices.img is None:
            return

        elif self.positioning_ui.view_mode == ViewMode.BOUNDARIES or self.positioning_ui.view_mode == ViewMode.AREA_OF_INTEREST:
            if self.positioning_ui.selected_point is None and event.button() == Qt.LeftButton:
                if len(self.positioning_ui.points) >= 4:
                    clear_draw(
                        self.positioning_ui.ui.cameraDisplay.scene(),
                        self.positioning_ui.points,
                        self.positioning_ui.paths,
                    )
                item = draw_point(
                    self.positioning_ui.ui.cameraDisplay.scene(),
                    self.positioning_ui.paths,
                    point,
                )
                self.positioning_ui.points.append((item, point))
                if len(self.positioning_ui.points) == 4:
                    draw_line(
                        self.positioning_ui.paths,
                        self.positioning_ui.points[0][1],
                        self.positioning_ui.points[-1][1],
                    )

            elif (
                self.positioning_ui.selected_point is None
                and event.button() == Qt.RightButton
                and len(self.positioning_ui.points) >= 4
            ):
                self.positioning_ui.selected_point = select_point(self.positioning_ui.points, point)

            elif self.positioning_ui.selected_point is not None:
                self.positioning_ui.points[self.positioning_ui.selected_point] = (
                    self.positioning_ui.points[self.positioning_ui.selected_point][0],
                    point,
                )
                self.positioning_ui.selected_point = None

        elif self.positioning_ui.view_mode == ViewMode.MOVE_TO_POINT:
            h, w = (
                self.positioning_ui.devices.img.height(),
                self.positioning_ui.devices.img.width(),
            )
            offset_x = self.positioning_ui.ui.positioningXOffsetSpinBox.value()
            offset_y = self.positioning_ui.ui.positioningYOffsetSpinBox.value()
            x, y = real_point(
                point[0],
                point[1],
                w,
                h,
                self.positioning_ui.devices.positioning.X_BOUNDS,
                self.positioning_ui.devices.positioning.Y_BOUNDS,
                offset_x,
                offset_y,
            )
            self.positioning_ui.ui.positioningXCoordSpinBox.setValue(x - offset_x)
            self.positioning_ui.ui.positioningYCoordSpinBox.setValue(y - offset_y)
            self.positioning_ui.ui.positioningMoveButton.click()

        event.accept()

    def mouseMoveEvent(self, event):
        point = (event.scenePos().x(), event.scenePos().y())

        if len(self.positioning_ui.points) > 0 and len(self.positioning_ui.points) < 4:
            draw_line(self.positioning_ui.paths, self.positioning_ui.points[-1][1], point)
            event.accept()

        elif self.positioning_ui.selected_point is not None:
            move_point(
                self.positioning_ui.points,
                self.positioning_ui.paths,
                self.positioning_ui.selected_point,
                point,
            )
