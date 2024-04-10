import json
import serial
from time import sleep

from app.utils.logging import device_logger


class Positioning:
    """
    Connect, disconnect, send command and positionate a DiscoUltimate 3D printer using a serial link
    """

    # Name of the positioning system
    name = "Disco Ultimate"

    # Positioning system boundaries ([min, max] in cm)
    X_BOUNDS = [0, 20]
    Y_BOUNDS = [0, 20]
    Z_BOUNDS = [0, 20]

    # Commands to interact with DiscoUltimate (GCode)
    EOL = b"\n"
    UNIT_MM = b"G21"
    ABSOLUTE = b"G90"
    RELATIVE = b"G91"
    HOMING = b"G28"
    MOVE = b"G0"
    GET_CURRENT_POSITION = b"M114"
    FINISH_MOVES = b"M400"

    def __init__(
        self,
        timeout=5,
    ):
        """
        Initialize the settings to connect to the printer using a serial link
        """
        self._timeout = timeout
        self._serial = None
        self.up_before_move = {"enabled": False, "Z-level": 1, "Z-value": 0.1}

    def help(self) -> str:
        """Provide help for the positioning system

        Returns:
            Address format for the Disco Ultimate
        """
        return (
            "Disco Ultimate printer\n"
            "Address should specify port and baudrate, separated by a semi-colon\n"
            "Example: COM7:250000"
        )

    @device_logger
    def connect(self, addr):
        """Connect the positionning system

        Args:
            addr: string specifying port and baudrate, separated by a semi-colon (eg: "COM7:250000")
        """
        if not (len(addr.split(":")) == 2 and addr.split(":")[1].isnumeric()):
            raise ValueError("Invalid address format")

        port = addr.split(":")[0]
        baudrate = addr.split(":")[1]

        self._serial = serial.Serial(
            port,
            baudrate=baudrate,
            timeout=self._timeout,
        )

        self.read()  # wait for successful connection
        self.send(self.UNIT_MM + self.EOL)  # set units to millimeters

    @device_logger
    def disconnect(self):
        """Disconnect the positioning system"""
        self._serial.close()
        self._serial = None

    @device_logger
    def is_connected(self) -> bool:
        """Check if the positioning system is connected

        Returns:
            Wether the positioning system is connected or not
        """
        if self._serial is None:
            return False
        return self._serial.isOpen()

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the positioning system

        Args:
            cmd: custom command to send to the positioning system
        """
        self._serial.flushInput()  # clear the input buffer, so that the next call to read() will return the command's response
        if isinstance(cmd, str):
            cmd = cmd.encode("utf-8") + b"\n"
        self._serial.write(cmd)

    @device_logger
    def read(self) -> bytes:
        """Read data from the positioning system

        Returns:
            The data read
        """
        return self._serial.readline()

    @device_logger
    def get_settings(self) -> str:
        """Get positioning system settings

        Returns:
            The settings as a config string
        """
        settings = {"up-before-move": self.up_before_move}
        return json.dumps(settings, indent=4)

    @device_logger
    def set_settings(self, settings: str):
        """Set positioning system settings

        Args:
            settings: the settings as a config string
        """
        settings = json.loads(settings)
        self.up_before_move = settings["up-before-move"]

    @device_logger
    def calibrate(self):
        """Calibrate the positioning system (homing)"""
        self.send(self.HOMING + self.EOL)

    @device_logger
    def locate(self) -> tuple[float, float, float]:
        """Get the current position of the positioning system

        Returns:
            Tuple of (x,y,z) coordinates in cm
        """
        self.send(self.GET_CURRENT_POSITION + self.EOL)
        pos = self.read().decode("utf-8")
        x = float(pos.split(" ")[0].split(":")[1]) / 10
        y = float(pos.split(" ")[1].split(":")[1]) / 10
        z = float(pos.split(" ")[2].split(":")[1]) / 10
        return (x, y, z)

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
        up_before_move, up_val = False, 0
        if self.up_before_move["enabled"]:
            _, _, current_z = self.locate()
            if z is None or (current_z == z and absolute) or (z == 0 and not absolute):
                if current_z <= self.up_before_move["Z-level"]:
                    up_before_move = True
                    up_val = str(self.up_before_move["Z-value"] * 10)

        cmd = b""

        if up_before_move:
            cmd += self.RELATIVE + self.EOL + self.MOVE + f" Z{up_val}".encode("utf-8") + self.EOL

        if absolute:
            cmd += self.ABSOLUTE + self.EOL
        else:
            cmd += self.RELATIVE + self.EOL

        cmd += self.MOVE

        if x is not None:
            cmd += f" X{x * 10}".encode("utf-8")
        if y is not None:
            cmd += f" Y{y * 10}".encode("utf-8")
        if z is not None and not up_before_move:
            cmd += f" Z{z * 10}".encode("utf-8")

        cmd += self.EOL

        if up_before_move:
            cmd += self.RELATIVE + self.EOL + self.MOVE + f" Z-{up_val}".encode("utf-8") + self.EOL

        self.send(cmd)

    @device_logger
    def wait(self):
        """Wait for the positioning system to finish moving"""
        sleep(0.5)  # wait for all pending commands to be properly acknowledged
        self.send(self.FINISH_MOVES + self.EOL)
        while self.read().strip() != b"ok":
            pass
