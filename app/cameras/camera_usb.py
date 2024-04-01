import cv2
import json
from PySide6.QtGui import QImage

from app.utils.logging import device_logger


class Camera:
    """
    Connect, disconnect and get images from a USB camera
    """

    # Name of the camera
    name = "USB Camera"

    def __init__(self):
        """Initialize the settings to connect to the camera"""
        self.x_mirror, self.y_mirror = False, False
        self._cap = None

    def help(self) -> str:
        """Provide help for the USB camera device

        Returns:
            Help string which lists available cameras (index < 10)
        """
        cameras, max_devices = [], 10
        for i in range(max_devices):
            cap = cv2.VideoCapture(i)
            if cap and cap.isOpened():
                cameras.append(str(i))
            cap.release()

        cam_help = ", ".join(cameras)
        help = f"USB Camera\nAddress should be a number\nFollowing available indexes detected:\n{cam_help}"
        return help

    @device_logger
    def connect(self, device: str):
        """
        Connect to the camera

        Args:
            device: device id of the camera
        """
        if not device.isnumeric():
            raise ValueError("Invalid address format")

        self._cap = cv2.VideoCapture(int(device))
        if not self._cap.isOpened():
            self._cap = None
            raise Exception(f"Couldn't open camera {device}")

    @device_logger
    def disconnect(self):
        """Disconnect the camera"""
        self._cap.release()
        self._cap = None

    @device_logger
    def is_connected(self) -> bool:
        """Check if camera is connected

        Returns:
            Wether the oscilloscope is connected or not
        """
        return self._cap and self._cap.isOpened()

    @device_logger
    def send(self, cmd: bytes | str):
        """Unsupported by this camera"""

    @device_logger
    def read(self) -> bytes:
        """Unsupported by this camera"""
        return b""

    @device_logger
    def get_settings(self) -> str:
        """Get camera settings

        Returns:
            The settings as a config string
        """
        settings = {
            "width": self._cap.get(cv2.CAP_PROP_FRAME_WIDTH),
            "height": self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            "invert X": self.x_mirror,
            "invert Y": self.y_mirror,
        }
        return json.dumps(settings, indent=4)

    @device_logger
    def set_settings(self, settings: str):
        """Set camera settings

        Args:
            settings: the settings as a config string
        """
        settings = json.loads(settings)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings["width"])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings["height"])
        self.x_mirror = bool(settings["invert X"])
        self.y_mirror = bool(settings["invert Y"])

    @device_logger
    def get(self) -> QImage:
        """Get an image from the camera

        Returns:
            The captured image
        """
        if not self._cap or not self._cap.grab():
            raise Exception("failed to get an image from the camera")
        img = self._cap.retrieve()[1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimage = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
        qimage = qimage.mirrored(horizontally=self.x_mirror, vertically=self.y_mirror)
        return qimage
