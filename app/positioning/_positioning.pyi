# This file is a template for adding support for a new positioning system

from app.utils.logging import device_logger

class Positioning:
    """
    Generic class to interact with a positioning system
    """

    # Name of the positioning system
    name = "generic"

    # Positioning system boundaries ([min, max] in cm)
    X_BOUNDS = [0, 0]
    Y_BOUNDS = [0, 0]
    Z_BOUNDS = [0, 0]

    def __init__(self, **args):
        """Initialize the settings to connect to the positioning system"""

    def help(self) -> str:
        """Provide help for the positioning system

        Returns:
            Help for the positioning system
        """

    @device_logger
    def connect(self, addr: str):
        """Connect the positionning system

        Args:
            addr: the address of the positioning system
        """

    @device_logger
    def disconnect(self):
        """Disconnect the positioning system"""

    @device_logger
    def is_connected(self) -> bool:
        """Check if the positioning system is connected

        Returns:
            Wether the positioning system is connected or not
        """

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the positioning system

        Args:
            cmd: custom command to send to the positioning system
        """

    @device_logger
    def read(self) -> bytes:
        """Read data from the positioning system

        Returns:
            The data read
        """

    @device_logger
    def get_settings(self) -> str:
        """Get positioning system settings

        Returns:
            The settings as a config string
        """

    @device_logger
    def set_settings(self, settings: str):
        """Set positioning system settings

        Args:
            settings: the settings as a config string
        """

    @device_logger
    def calibrate(self):
        """Calibrate the positioning system"""

    @device_logger
    def locate(self) -> tuple[float, float, float]:
        """Get the current position of the positioning system

        Returns:
            Tuple of (x,y,z) coordinates in cm
        """

    @device_logger
    def move(
        self,
        x: float | None = None,
        y: float | None = None,
        z: float | None = None,
        absolute: bool = True,
    ):
        """Use the positioning system to move to the specified coordinates

        Args:
            x: x-axis coordinate to move to (in cm)
            y: y-axis coordinate to move to (in cm)
            z: z-axis coordinate to move to (in cm)
            absolute: whether the coordinates are absolute or relative
        """

    @device_logger
    def wait(self):
        """Wait for the positioning system to finish moving"""
