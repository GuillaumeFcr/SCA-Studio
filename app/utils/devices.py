from importlib import import_module
from pathlib import Path

DEVICES_TYPES = {
    "boards": "Board",
    "cameras": "Camera",
    "oscilloscopes": "Oscilloscope",
    "positioning": "Positioning",
    "injectors": "Injector",
}


def get_available_devices(type: str) -> list:
    """Get available devices

    Args:
        type: device type, which must be an allowed device type ("boards", "cameras"...)

    Return:
        A list of imported devices
    """
    if type not in DEVICES_TYPES:
        return []
    devices = []
    for board_file in Path(f"app/{type}").glob("*.py"):
        path = f"app.{type}.{board_file.with_suffix('').name}"
        board = getattr(import_module(path), DEVICES_TYPES[type])
        devices.append(board)
    return devices


class Devices:
    """List of devices and other objects shared by all tabs"""

    injector = None
    camera = None
    positioning = None
    oscilloscope = None
    board = None
    grid = []
    img = None
