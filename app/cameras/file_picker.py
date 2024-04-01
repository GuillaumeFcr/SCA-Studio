import json
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QFileDialog

from app.utils.logging import device_logger


class Camera:
    """
    A "fake" camera to pick up an image on the filesystem
    """

    # Name of the camera
    name = "File picker"

    def __init__(self, **args):
        """Initialize the settings to connect to the camera"""
        self.x_mirror, self.y_mirror = False, False
        self._is_connected = False

    def help(self) -> str:
        """Provide help for the file picker

        Returns:
            Help for the file picker
        """
        help = "File picker\nNo address is required\nTake a photo by selecting a file"
        return help

    @device_logger
    def connect(self, addr: str):
        """Connect to the camera

        Args:
            addr: address of the camera
        """
        self._is_connected = True

    @device_logger
    def disconnect(self):
        """Disconnect the camera"""
        self._is_connected = False

    @device_logger
    def is_connected(self) -> bool:
        """Check if the camera is connected

        Returns:
            Wether the oscilloscope is connected or not
        """
        return self._is_connected

    @device_logger
    def send(self, cmd: bytes | str):
        """Unsupported by this device"""

    @device_logger
    def read(self) -> bytes:
        """Unsupported by this device"""
        return b""

    @device_logger
    def get_settings(self) -> str:
        """Get camera settings

        Returns:
            The settings as a config string
        """
        settings = {"invert X": self.x_mirror, "invert Y": self.y_mirror}
        return json.dumps(settings, indent=4)

    @device_logger
    def set_settings(self, settings: str):
        """Set camera settings

        Args:
            settings: the settings as a config string
        """
        settings = json.loads(settings)
        self.x_mirror = bool(settings["invert X"])
        self.y_mirror = bool(settings["invert Y"])

    @device_logger
    def get(self) -> QImage:
        """Get an image from the camera

        Returns:
            The captured image
        """
        qimage = QImage()
        filename, _ = QFileDialog().getOpenFileName(filter="Image Files (*.png *.jpg *jpeg *.bmp *.webp *.svg *.gif)")
        if filename:
            qimage = QImage(filename).mirrored(horizontally=self.x_mirror, vertically=self.y_mirror)
        return qimage
