# This file is a template for adding support for a new target board

from app.utils.logging import device_logger

class Board:
    """
    Generic class to interact with a target board
    """

    # Name of the board
    name = "generic"

    def __init__(self, **args):
        """Initialize the settings to connect to the target board"""

    def help(self) -> str:
        """Provide help for the target board

        Returns:
            Help for the target board
        """

    @device_logger
    def connect(self, addr: str):
        """Connect the board

        Args:
            addr: the address of the target board
        """

    @device_logger
    def disconnect(self):
        """Disconnect the board"""

    @device_logger
    def is_connected(self) -> bool:
        """Check if the board is connected

        Returns:
            Wether the board is connected or not
        """

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the target board

        Args:
            cmd: custom command to send to the target board
        """

    @device_logger
    def read(self) -> bytes:
        """Read data from the target board

        Returns:
            The data read
        """

    @device_logger
    def get_settings(self) -> str:
        """Get board settings

        Returns:
            The settings as a config string
        """

    @device_logger
    def set_settings(self, settings: str):
        """Set board settings

        Args:
            settings: the settings as a config string
        """

    @device_logger
    def run(self):
        """Run the algorithm"""

    @device_logger
    def stop(self):
        """Stop the algorithm"""

    @device_logger
    def get(self) -> tuple[int, str]:
        """Wait for the end of the algorithm, and return information about the encryption & the error count

        Returns:
            Tuple of:
            - the number of errors that occurred during the algorithm
            - information about the encryption as a string
        """
