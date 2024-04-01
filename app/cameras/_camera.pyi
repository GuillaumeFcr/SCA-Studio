# This file is a template for adding support for a new camera

from PySide6.QtGui import QImage

from app.utils.logging import device_logger

class Camera:
    """
    Generic class to interact with a camera
    """

    # Name of the camera
    name = "generic"

    def __init__(self, **args):
        """Initialize the settings to connect to the camera"""

    def help(self) -> str:
        """Provide help for the camera

        Returns:
            Help for the camera
        """

    @device_logger
    def connect(self, addr: str):
        """Connect to the camera

        Args:
            addr: address of the camera
        """

    @device_logger
    def disconnect(self):
        """Disconnect the camera"""

    @device_logger
    def is_connected(self) -> bool:
        """Check if the camera is connected

        Returns:
            Wether the oscilloscope is connected or not
        """

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the camera

        Args:
            cmd: custom command to send to the camera
        """

    @device_logger
    def read(self) -> bytes:
        """Read data from the camera

        Returns:
            The data read
        """

    @device_logger
    def get_settings(self) -> str:
        """Get camera settings

        Returns:
            The settings as a config string
        """

    @device_logger
    def set_settings(self, settings: str):
        """Set camera settings

        Args:
            settings: the settings as a config string
        """

    @device_logger
    def get(self) -> QImage:
        """Get an image from the camera

        Returns:
            The captured image
        """
