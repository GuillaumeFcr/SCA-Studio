import chipwhisperer as cw
import json
from time import sleep

from app.utils.logging import device_logger


class Board:
    """
    Connect, disconnect and interact with a Chipwhisperer board running the SimpleSerial-AES firmware.
    Key and text follow the NewAE's Basic Key Text Pattern
    """

    # Name of the board
    name = "ChipWhisperer SimpleSerial-AES"

    def __init__(self):
        """Initialize the settings to connect to the target board"""
        self._scope = None
        self._target = None
        self._platform = ""
        self._key, self._text = b"", b""
        self._ktp = cw.ktp.Basic()

    def _reset(self):
        """Reset the target board"""
        if self._platform == "CW308_SAM4S" or self._platform == "CWHUSKY":
            self._scope.io.target_pwr = 0
            sleep(0.2)
            self._scope.io.target_pwr = 1
            sleep(0.2)
        if self._platform == "CW303" or self._platform == "CWLITEXMEGA":
            self._scope.io.pdic = "low"
            sleep(0.1)
            self._scope.io.pdic = "high_z"  # XMEGA doesn't like pdic driven high
            sleep(0.1)  # xmega needs more startup time
        elif "neorv32" in self._platform.lower():
            raise IOError("Default iCE40 neorv32 build does not have external reset - reprogram device to reset")
        elif self._platform == "CW308_SAM4S":
            self._scope.io.nrst = "low"
            sleep(0.25)
            self._scope.io.nrst = "high_z"
            sleep(0.25)
        else:
            self._scope.io.nrst = "low"
            sleep(0.05)
            self._scope.io.nrst = "high_z"
            sleep(0.05)

    def help(self) -> str:
        """Provide help for the target board

        Returns:
            Help for the target board
        """
        return (
            "Chipwhisperer SimpleSerial-AES target board\n"
            "Interact with the SimpleSerial-AES firmware\n"
            "Use NewAE's Basic Key Text Pattern\n"
            "Address should specify PLATFORM and SimpleSerial version, separated by a semi-colon\n"
            "Example: CWLITEARM:SS_VER_1_1"
        )

    @device_logger
    def connect(self, addr: str):
        """Connect the board using specified serial settings

        Args:
            addr: string specifying PLATFORM and SimpleSerial version (eg: "CWLITEARM:SS_VER_1_1")
        """
        if not (len(addr.split(":")) == 2):
            raise ValueError("Invalid address format")

        platform = addr.split(":")[0]
        ssver = addr.split(":")[1]

        self._platform = platform

        if ssver == "SS_VER_1_1":
            target_type = cw.targets.SimpleSerial
        elif ssver == "SS_VER_2_1":
            target_type = cw.targets.SimpleSerial2
        else:
            raise ValueError("Invalid SimpleSerial version: should be SS_VER_1_1 or SS_VER_2_1")

        self._scope = cw.scope()
        self._target = cw.target(self._scope, target_type)
        self._scope.default_setup()
        self._reset()

    @device_logger
    def disconnect(self):
        """Disconnect the board"""
        self._scope.dis()
        self._target.dis()
        self._scope = None
        self._target = None

    @device_logger
    def is_connected(self) -> bool:
        """Check if the board is connected

        Returns:
            Wether the board is connected or not
        """
        return self._target is not None

    @device_logger
    def send(self, cmd: bytes | str):
        """Unsupported by this board"""

    @device_logger
    def read(self) -> bytes:
        """Unsupported by this board"""

    @device_logger
    def get_settings(self) -> str:
        """Get board settings

        Returns:
            The settings as a config string
        """
        settings = {
            "fixed_key": self._ktp.fixed_key,
            "fixed_text": self._ktp.fixed_text,
        }
        return json.dumps(settings, indent=4)

    @device_logger
    def set_settings(self, settings: str):
        """Set board settings

        Args:
            settings: the settings as a config string
        """
        settings = json.loads(settings)
        self._ktp.fixed_key = settings["fixed_key"]
        self._ktp.fixed_text = settings["fixed_text"]

    @device_logger
    def run(self):
        """Run the encryption"""
        self._key, self._text = self._ktp.next()
        self._target.set_key(self._key)
        self._target.simpleserial_write("p", self._text)

    @device_logger
    def stop(self):
        """Unsupported by this board"""

    @device_logger
    def get(self) -> tuple[int, str]:
        """Wait for the end of the encryption. Returns the key & the text used, and the result of the encryption.
        Does NOT count the number of failed encryption (returns 0)

        Returns:
            The key & the text used, and the result of the encryption as string
        """
        data = self._target.simpleserial_read("r", 16)
        return 0, f"{self._key.hex()} {self._text.hex()} {data.hex()}"
