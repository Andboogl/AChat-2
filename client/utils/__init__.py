"""
A package with various program utilities including:
    - Server Utility
    - Data checks
    - Encryptor
    - Configuration Utility
"""


from PyQt6.QtWidgets import QMessageBox
from .settings import Settings
from .check import check_for_empty, is_int
from .connection import Connection


def show_message(win, msg, ex_type=None):
    """Show QMessageBox"""
    message_box = QMessageBox(win)
    message_box.setText(msg)

    if ex_type == 0:
        message_box.show()

    else:
        message_box.exec()
