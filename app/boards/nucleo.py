import serial
import struct
import json

from app.utils.logging import device_logger


class Board:
    """
    Connect, disconnect and interact with a Nucleo board, using a serial link.
    The board runs N encryptions using the same key, and return the number of failed encryptions.
    """

    # Name of the board
    name = "Nucleo"

    def __init__(
        self,
        n=100,
        timeout=5,
        parity=serial.PARITY_NONE,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE,
    ):
        """Initialize the settings to connect to the board using a serial link"""
        self.n = n
        self.timeout = timeout
        self.parity = parity
        self.bytesize = bytesize
        self.stopbits = stopbits
        self._serial = None

    def help(self) -> str:
        """Provide help for the Nucleo target board

        Returns:
            Target board description and address format
        """
        return (
            "Nucleo target board\n"
            "Run N (0 <= N <= 65535) encryptions using the same key, and count failed encryptions\n"
            "Address should specify port and baudrate, separated by a semi-colon\n"
            "Example: COM3:9600"
        )

    @device_logger
    def connect(self, addr: str):
        """Connect the board using specified serial settings

        Args:
            addr: string specifying port and baudrate, separated by a semi-colon (eg: "COM3:9600")
        """
        if not (len(addr.split(":")) == 2 and addr.split(":")[1].isnumeric()):
            raise ValueError("Invalid address format")

        port = addr.split(":")[0]
        baudrate = addr.split(":")[1]

        self._serial = serial.Serial(
            port,
            baudrate=baudrate,
            timeout=self.timeout,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
        )

    @device_logger
    def disconnect(self):
        """Disconnect the board"""
        self._serial.close()
        self._serial = None

    @device_logger
    def is_connected(self) -> bool:
        """Check if serial link is open

        Returns:
            Wether the board is connected or not
        """
        return self._serial is not None and self._serial.isOpen()

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the target board

        Args:
            cmd: custom command to send to the target board
        """
        if isinstance(cmd, str):
            cmd = cmd.encode("utf-8") + b"\n"
        self._serial.write(cmd)

    @device_logger
    def read(self) -> bytes:
        """Read data from the target board

        Returns:
            The data read
        """
        return self._serial.read(1)

    @device_logger
    def get_settings(self) -> str:
        """Get board settings

        Returns:
            The settings as a config string
        """
        return json.dumps({"N": self.n}, indent=4)

    @device_logger
    def set_settings(self, settings: str):
        """Set board settings

        Args:
            settings: the settings as a config string
        """
        self.n = json.loads(settings)["N"]

    @device_logger
    def run(self):
        """Run encryption"""
        if self.n > 65535 or self.n < 0:
            self.n = 65535
        command = struct.pack("h", self.n)
        self._serial.write(command)

    @device_logger
    def stop(self):
        """Unsupported by this board"""

    @device_logger
    def get(self) -> tuple[int, str]:
        """Wait for the end of the encryption, and get the number of failed encryption

        Returns:
            The number of errors that occurred during the algorithm, and an empty string
        """
        data = self._serial.read(2)
        while not data:
            data = self._serial.read(2)
        return struct.unpack("h", data)[0], ""
