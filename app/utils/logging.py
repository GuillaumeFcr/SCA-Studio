from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

LOG_FILE = "logs.txt"


def log(message: str):
    """Add an entry to the logs

    Args:
        message: the message to log
    """
    with open(LOG_FILE, mode="a") as f:
        f.write(f"{datetime.now()} - {message}\n")


def device_logger(f):
    """Decorator for logging device methods: device name, method name, method args, method result"""

    def wrapper(self, *args, **kw):
        argskw = ",".join([str(arg) for arg in args] + [f"{key}={str(val)}" for key, val in kw.items()])
        log(f"{self.name} :: {f.__name__}({argskw})")
        return f(self, *args, **kw)

    return wrapper


def handle(context: str):
    """Decorator to use a WaitCursor and handle exceptions

    Args:
        context: title for the error message box and the log entry
    """

    def decorate(f):
        def wrapper(*args, **kw):
            log(f"{context} - Started")
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                return f(*args, **kw)
            except Exception as e:
                log(f"{context} - Error: {e}")
                QMessageBox(QMessageBox.Critical, context, f"Error: {e}").exec()
            finally:
                QApplication.restoreOverrideCursor()

        return wrapper

    return decorate
