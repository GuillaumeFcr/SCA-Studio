# This file is a template for adding support for a new oscilloscope

import numpy as np

from app.utils.logging import device_logger

class Oscilloscope:
    """
    Generic class to interact with an oscilloscope
    """

    # Name of the oscilloscope
    name = "generic"

    # Allowed channels
    channels = [""]

    @device_logger
    def __init__(self, **args):
        """Initialize oscilloscope settings"""

    @device_logger
    def help(self) -> str:
        """Provide help for the oscilloscope

        Returns:
            Help for the oscilloscope
        """

    @device_logger
    def connect(self, addr: str):
        """Connect to the oscilloscope

        Args:
            addr: address of the oscilloscope
        """

    @device_logger
    def disconnect(self):
        """Disconnect oscilloscope"""

    @device_logger
    def is_connected(self) -> bool:
        """Check if the oscilloscope is connected

        Returns:
            Wether the oscilloscope is connected or not
        """

    @device_logger
    def send(self, cmd: bytes | str):
        """Send custom command to the oscilloscope

        Args:
            cmd: custom command to send to the oscilloscope
        """

    @device_logger
    def read(self) -> bytes:
        """Read data from the oscilloscope

        Returns:
            The data read
        """

    @device_logger
    def get_channel_state(self, channel: str) -> bool:
        """Get a channel state

        Args:
            channel: the channel to check

        Returns:
            Whether the channel is enabled or not
        """

    @device_logger
    def get_channel(self, channel: str) -> str:
        """Get channel settings

        Args:
            channel: the channel whose settings must be retrieved

        Returns:
            The channel settings as a config string
        """

    @device_logger
    def get_general(self) -> str:
        """Get general settings

        Returns:
            The general settigns as a config string
        """

    @device_logger
    def get_trigger(self) -> str:
        """Get trigger settings

        Returns:
            The trigger settings as a config string
        """

    @device_logger
    def get_waveform(self) -> str:
        """Get waveform settings

        Returns:
            The waveform settings as a config string
        """

    @device_logger
    def enable_channel(self, channel: str):
        """Enable a channel

        Args:
            channel: the channel to enable
        """

    @device_logger
    def disable_channel(self, channel: str):
        """Disable a channel

        Args:
            channel: the channel to disable
        """

    @device_logger
    def set_channel(self, channel: str, settings: str):
        """Set channel settings

        Args:
            channel: the channel on which the settings should be applied
            settings: the channel settings as a config string
        """

    @device_logger
    def set_general(self, settings: str):
        """Set general settings

        Args:
            settings: the general settings as a config string
        """

    @device_logger
    def set_trigger(self, settings: str):
        """Set trigger settings

        Args:
            settings: the trigger settings as a config string
        """

    @device_logger
    def set_waveform(self, settings: str):
        """Set waveform settings

        Args:
            settings: the waveform settings as a config string
        """

    @device_logger
    def get_data(self) -> np.array:
        """Get measured data

        Returns:
            A numpy array representing measured data
        """
