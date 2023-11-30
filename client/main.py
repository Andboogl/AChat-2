"""The main module. Launches the application"""


from app import MainWindow
from PyQt6.QtWidgets import QApplication, QMessageBox
from loguru import logger
from getpass import getuser
from datetime import datetime
import sys
import os


# Logger settings
achat_folder_path = f'/Users/{getuser()}/.achat'
logs_folder_path = f'/Users/{getuser()}/.achat/logs'

if not os.path.exists(achat_folder_path):
    os.mkdir(achat_folder_path)
    os.mkdir(logs_folder_path)

if not os.path.exists(logs_folder_path):
    os.mkdir(logs_folder_path)

logger.add(
    sink=f'/Users/{getuser()}/.achat/logs/{datetime.now()}'
)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    if os.name == 'posix':
        window.show()

    else:
        msg = QMessageBox(window)
        msg.setText('AChat працює тільки на системах Unix')
        msg.exec()
        exit()

    app.exec()


if __name__ == '__main__':
    main()
