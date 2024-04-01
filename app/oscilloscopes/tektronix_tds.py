import pyvisa
import numpy as np
import json

from app.utils.logging import device_logger


class Oscilloscope:
    """
    Connect, disconnect and interact with a Tektronix oscilloscope (TDS Series) using a visa link
    """

    # Name of the oscilloscope
    name = "Tektronix TDS"

    # Allowed channels
    channels = ["CH1", "CH2", "CH3", "CH4"]

    def __init__(self, timeout=5000):
        """Initialize oscilloscope settings"""

        self._timeout = timeout
        self._is_open = False

    def _query(self, command):
        """
        Send a query request to the oscilloscope
        """
        return self._oscilloscope.query(command)

    def _write(self, command):
        """
        Send a command to the oscilloscope
        """
        self._oscilloscope.write(command)

    def help(self) -> str:
        """Provide help for the oscilloscope

        Returns:
            Address format for the Tektronix TDS oscilloscope
        """
        return (
            "Tektronix TDS oscilloscope\n"
            "Address should be a valid visa resource name\n"
            "Example: TCPIP::150.197.100.17::gpib0,1::INSTR"
        )

    @device_logger
    def connect(self, addr):
        """Connect to the oscilloscope

        Args:
            addr: address of the oscilloscope
        """
        rm = pyvisa.ResourceManager("@py")
        self._oscilloscope = rm.open_resource(addr)
        self._oscilloscope.timeout = self._timeout
        self._is_open = True

        # Enforce waveform transfer format
        self._write("DATa:ENCdg RIBinary")
        self._write("WFMOutpre:BYT_Nr 2")

    @device_logger
    def disconnect(self):
        """Disconnect oscilloscope"""
        self._oscilloscope.close()
        self._is_open = False

    @device_logger
    def is_connected(self) -> bool:
        """Check if the oscilloscope is connected

        Returns:
            Wether the oscilloscope is connected or not
        """
        return self._is_open

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the oscilloscope

        Args:
            cmd: custom command to send to the oscilloscope
        """
        self._oscilloscope.write(cmd)

    @device_logger
    def read(self) -> bytes:
        """Read data from the oscilloscope

        Returns:
            The data read
        """
        try:
            return self._oscilloscope.read()
        except pyvisa.errors.VisaIOError:
            b""

    @device_logger
    def get_channel_state(self, channel: str) -> bool:
        """Get a channel state

        Args:
            channel: the channel to check

        Returns:
            Whether the channel is enabled or not
        """
        if channel not in self.channels:
            raise ValueError

        enabled = self._query(f"SELECT:{channel}?").strip()
        return bool(int(enabled.lower().split()[-1]))

    @device_logger
    def get_channel(self, channel: str) -> str:
        """Get channel settings

        Args:
            channel: the channel whose settings must be retrieved

        Returns:
            The channel settings as a config string
        """
        if channel not in self.channels:
            raise ValueError

        scale = self._query(f"{channel}:SCAle?").strip()
        position = self._query(f"{channel}:POSition?").strip()

        settings = {"scale": scale, "position": position}
        return json.dumps(settings, indent=4)

    @device_logger
    def get_general(self) -> str:
        """Get general settings

        Returns:
            The general settigns as a config string
        """
        scale = self._query("HORizontal:SCAle?").strip()
        position = self._query("HORizontal:POSition?").strip()
        resolution = self._query("HORizontal:RESOlution?").strip()

        settings = {
            "horizontal": {
                "scale": scale,
                "position": position,
                "resolution": resolution,
            }
        }
        return json.dumps(settings, indent=4)

    @device_logger
    def get_trigger(self) -> str:
        """Get trigger settings

        Returns:
            The trigger settings as a config string
        """
        source = self._query("TRIGger:A:EDGE:SOUrce?").strip()
        coupling = self._query("TRIGger:A:EDGE:COUPling?").strip()
        slop = self._query("TRIGger:A:EDGE:SLOpe?").strip()
        level = self._query("TRIGger:A:LEVel?").strip()
        mode = self._query("TRIGger:A:MODe?").strip()

        settings = {
            "source": source,
            "coupling": coupling,
            "slop": slop,
            "level": level,
            "mode": mode,
        }
        return json.dumps(settings, indent=4)

    @device_logger
    def get_waveform(self) -> str:
        """Get waveform settings

        Returns:
            The waveform settings as a config string
        """
        source = self._query("DATa:SOUrce?").strip()
        start = self._query("DATa:STARt?").strip()
        stop = self._query("DATa:STOP?").strip()
        mode = self._query("ACQuire:MODe?").strip()

        settings = {
            "source": source,
            "start": start,
            "stop": stop,
            "mode": mode,
        }
        return json.dumps(settings, indent=4)

    @device_logger
    def enable_channel(self, channel: str):
        """Enable a channel

        Args:
            channel: the channel to enable
        """
        if channel not in self.channels:
            raise ValueError

        self._write(f"SELECT:{channel} ON")

    @device_logger
    def disable_channel(self, channel: str):
        """Disable a channel

        Args:
            channel: the channel to disable
        """
        if channel not in self.channels:
            raise ValueError

        self._write(f"SELECT:{channel} Off")

    @device_logger
    def set_channel(self, channel: str, settings: str):
        """Set channel settings

        Args:
            channel: the channel on which the settings should be applied
            settings: the channel settings as a config string
        """
        settings = json.loads(settings)

        if channel not in self.channels:
            raise ValueError

        self._write(f"SELECT:{channel} ON")
        self._write(f"{channel}:SCAle {settings['scale']}")
        self._write(f"{channel}:POSition {settings['position']}")

    @device_logger
    def set_general(self, settings: str):
        """Set general settings

        Args:
            settings: the general settings as a config string
        """
        settings = json.loads(settings)

        self._write(f"HORizontal:SCAle {settings['horizontal']['scale']}")
        self._write(f"HORizontal:POSition {settings['horizontal']['position']}")
        self._write(f"HORizontal:RESOlution {settings['horizontal']['resolution']}")

    @device_logger
    def set_trigger(self, settings: str):
        """Set trigger settings

        Args:
            settings: the trigger settings as a config string
        """
        settings = json.loads(settings)

        if settings["source"] not in self.channels:
            raise ValueError

        self._write(f"TRIGger:A:EDGE:SOUrce {settings['source']}")
        self._write(f"TRIGger:A:EDGE:COUPling {settings['coupling']}")
        self._write(f"TRIGger:A:EDGE:SLOpe {settings['slop']}")
        self._write(f"TRIGger:A:LEVel {settings['level']}")
        self._write(f"TRIGger:A:MODe {settings['mode']}")

    @device_logger
    def set_waveform(self, settings: str):
        """Set waveform settings

        Args:
            settings: the waveform settings as a config string
        """
        settings = json.loads(settings)

        if settings["source"] not in self.channels:
            raise ValueError

        self._write(f"DATa:SOUrce {settings['source']}")
        self._write(f"DATa:STARt {settings['start']}")
        self._write(f"DATa:STOP {settings['stop']}")
        self._write(f"ACQuire:MODe {settings['mode']}")

    @device_logger
    def get_data(self) -> np.array:
        """Get measured data

        Returns:
            A numpy array representing measured data
        """
        data = self._oscilloscope.query_binary_values("CURVe?", datatype="h", is_big_endian=True)
        return np.array(data)
