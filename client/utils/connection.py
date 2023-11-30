"""Connection module"""


from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
from .chiper import Chiper
from loguru import logger
import socket
import base64
import pickle
import threading
import os


class Connection:
    """The class is needed to connect to the server"""
    def __init__(self, ip, port, user_nikname, messages_widget):
        """Connecting to the server and launching data handlers from the server"""
        self.connection_sock = socket.socket()  # Client socket
        self.connection_sock.connect((ip, port))
        logger.info('Створенно сокет кліента та зʼєднання з сервером')

        self.is_connected = True

        # Downloading the encryption key from the server
        data = self.connection_sock.recv(1024)
        data = pickle.loads(data)

        # If server request is correct
        if data[0] == 'KEY':
            key = data[1]
            self.chiper = Chiper(key)
            logger.info('Завантажений ключ шифрування')

            # Sending user nickname to server
            request = ['NIKNAME', user_nikname]
            self.connection_sock.sendall(self.chiper.encrypt(request))
            logger.info('Серверу надісланий нікнейм користувача')

            threading.Thread(
                target=self.messages_monitor,
                args=(messages_widget,), daemon=True).start()

        else:
            self.connection_sock.close()
            self.is_connected = False

    def messages_monitor(self, messages_widget):
        """Monitoring new messages from the server and outputting them to QListWidget"""
        while True:
            data = self.connection_sock.recv(100_000)
            data = self.chiper.decrypt(data)

            # If this is a request for a new message
            # ['MESSAGE', message, user_icon, nikname]
            if data[0] == 'MESSAGE':
                item = QListWidgetItem(messages_widget)
                item.setText(f'{data[3]}: {data[1]}')
                font = QFont()
                font.setPointSize(20)
                item.setFont(font)

                with open('.usr_icon', 'xb' if not os.path.exists('.usr_icon') else 'wb') as file:
                    file.write(base64.b64decode(data[2]))

                item.setIcon(QIcon('.usr_icon'))
                os.remove('.usr_icon')

                messages_widget.addItem(item)

            # If this is a request to disconnect a user
            # ['EXIT', <nikname>]
            elif data[0] == 'EXIT':
                item = QListWidgetItem(messages_widget)
                item.setText(f'{data[1]} вийшов з чату')
                font = QFont()
                font.setBold(True)
                font.setPointSize(25)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                messages_widget.addItem(item)

            # If this is a request for a new user
            # ['NEW_USER', <nikname>]
            elif data[0] == 'NEW_USER':
                item = QListWidgetItem(messages_widget)
                item.setText(f'{data[1]} доєднався до чату!')
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont()
                font.setBold(True)
                font.setPointSize(25)
                item.setFont(font)
                messages_widget.addItem(item)

    def send(self, data):
        data = self.chiper.encrypt(data)
        self.connection_sock.sendall(data)

    def exit(self):
        request = ['EXIT']
        self.connection_sock.sendall(self.chiper.encrypt(request))
        self.connection_sock.close()
