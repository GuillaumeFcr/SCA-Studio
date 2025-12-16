import ctypes
import os
import sys

from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication

from app.ui.menubar import MenubarUi
from app.ui.positioning import PositioningUi
from app.ui.oscilloscope import OscilloscopeUi
from app.ui.acquisition import AcquisitionUi
from app.ui.emission import EmissionUi
from app.utils.devices import Devices


if __name__ == "__main__":
    # Initialize the app
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Round)
    loader = QUiLoader()
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setWindowIcon(QIcon("logo.ico"))

    # Set AppUserModelIDs on Windows, which allow our custom WindowIcon to appear in the taskbar
    if hasattr(ctypes, "windll"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("SCA_Studio.SCA_Studio")

    # Force current directory to app directory
    os.chdir(os.path.dirname(__file__))

    # Load the Qt ui
    ui_file = QFile("ui/main.ui")
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open main.ui: {ui_file.errorString()}")
        sys.exit(-1)
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)

    # Initialize ui components
    devices = Devices()
    menubar = MenubarUi(app, window, devices)
    positioning = PositioningUi(window, devices)
    oscilloscope = OscilloscopeUi(window, devices)
    acquisition = AcquisitionUi(window, devices)
    emission = EmissionUi(window, devices)

    # Run the app
    window.show()
    sys.exit(app.exec())
