"""Module for GUI processing and display"""


from ui.ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem
from PyQt6.QtGui import QPixmap, QFont, QIcon, QKeySequence
from PyQt6.QtCore import Qt, QSize
from getpass import getuser
from loguru import logger
import utils
import base64
import threading
import os


class MainWindow(QMainWindow):
    """
    The MainWindow class creates the main window of the
    program and processes the graphical interface
    """

    def __init__(self):
        """Uploading the design, user settings and avatar"""
        QMainWindow.__init__(self)

        self.settings = utils.Settings()
        self.is_connected = False

        # Downloading widgets
        self.widgets = Ui_MainWindow()
        self.widgets.setupUi(self)
        self.widgets.messages_widget.setIconSize(QSize(50, 50))

        # Load settings if a settings file exists
        if os.path.exists(self.settings.settings_file_path):
            try:
                data = self.settings.get_settings()
                self.widgets.server_ip.setText(data['ip'])
                self.widgets.server_port.setText(str(data['port']))
                self.widgets.user_nikname.setText(data['user_nikname'])
                logger.info('Налаштування користувача завантаженні')

            except Exception as error:
                logger.error(f'Помилка {error}. Не вдалося завантажити налаштування користувача')
                utils.show_message(self,
                                   'Не вдалося завантажити налаштування. Спробуйте видалити файл налаштуваннь або зберегти нові'
                                   , 0)

        self.setWindowTitle('AChat')
        self.setFixedSize(832, 449)

        self.load_icon()

        # Message that you need to connect to the server to communicate
        item = QListWidgetItem(self.widgets.messages_widget)
        item.setText('Вам потрібно підключитися до сервера для спілкування')
        font = QFont()
        font.setPointSize(25)
        font.setBold(True)
        item.setFont(font)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.widgets.messages_widget.addItem(item)

        # Pressing the buttons
        self.widgets.save_settings.clicked.connect(self.save_settings)
        self.widgets.chose_avatar.clicked.connect(self.chose_avatar)
        self.widgets.set_default_avatar.clicked.connect(self.set_default_avatar)
        self.widgets.connect_to_server.clicked.connect(self.connect_to_server)
        self.widgets.send_message.clicked.connect(self.send_message)
        self.widgets.quit_from_chat.clicked.connect(self.exit_from_server)

        self.widgets.send_message.setShortcut(QKeySequence('Ctrl+s'))

        logger.info('AChat запущений')

    def save_settings(self):
        """Save user settings"""
        ip = self.widgets.server_ip.text()
        port = self.widgets.server_port.text()
        user_nikname = self.widgets.user_nikname.text()

        if not utils.check_for_empty(ip) and not utils.check_for_empty(port) and not utils.check_for_empty(user_nikname):
            if utils.is_int(port):
                data = {
                    'ip': ip,
                    'port': int(port),
                    'user_nikname': user_nikname
                }
                self.settings.load_settings(data)

            else:
                utils.show_message(self, 'Порт повинен бути числом')

        else:
            utils.show_message(self, 'Ви вказали не всі поля')

        logger.info('Налаштування збережені')

    def load_icon(self):
        """Upload an user avatar"""
        achat_folder_path = os.path.join('/', 'Users', getuser(), '.achat')
        img_path = os.path.join(achat_folder_path, 'user.png')
        standart_img_path = os.path.join('icons', 'standart.png')

        # Створення аватарки користувача, якщо її не існує
        if not os.path.exists(img_path):
            with open(standart_img_path, 'rb') as st:
                if not os.path.exists(achat_folder_path):
                    os.mkdir(achat_folder_path)

                with open(img_path, 'xb') as n:
                    n.write(st.read())

        pixmap = QPixmap(img_path)
        self.widgets.label.setPixmap(pixmap)
        self.widgets.label.setScaledContents(True)
        self.widgets.label.resize(100, 100)
        self.widgets.label.move(10, 200)

        logger.info('Іконка користувача завантажена')

    def set_default_avatar(self):
        """Set a default avatar"""
        achat_folder_path = os.path.join('/', 'Users', getuser(), '.achat')
        img_path = os.path.join(achat_folder_path, 'user.png')
        standart_img_path = os.path.join('icons', 'standart.png')

        if not os.path.exists(achat_folder_path):
            os.mkdir(achat_folder_path)

        with open(standart_img_path, 'rb') as st:
            with open(img_path, 'xb' if not os.path.exists(img_path) else 'wb') as n:
                n.write(st.read())

        self.load_icon()
        logger.info('Встановлений аватар за замовчюванням')

    def chose_avatar(self):
        """Selecting a user avatar"""
        path = QFileDialog.getOpenFileName(self, 'Виберіть PNG-файл', filter='PNG File (*.png)')[0]

        # If the user did not click Cancel
        if path:
            achat_folder_path = os.path.join('/', 'Users', getuser(), '.achat')
            img_path = os.path.join(achat_folder_path, 'user.png')

            if not os.path.exists(achat_folder_path):
                os.mkdir(achat_folder_path)

            with open(path, 'rb') as usv:
                with open(img_path, 'xb' if not os.path.exists(img_path) else 'wb') as n:
                    n.write(usv.read())

        self.load_icon()
        logger.info('Аватар вибраний')

    def send_message(self):
        """Send a message to the server"""
        if self.is_connected:
            try:
                message = self.widgets.message_text.text()

                if not utils.check_for_empty(message):
                    achat_folder_path = os.path.join('/', 'Users', getuser(), '.achat')
                    img_path = os.path.join(achat_folder_path, 'user.png')

                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as file:
                            request = ['MESSAGE', message, base64.b64encode(file.read())]
                            logger.debug(request)
                            logger.debug(self.connection.chiper.encrypt(request))
                            self.connection.send(request)

                            logger.info('Повідомлення відправлено')

                        # Add a message to the message list
                        item = QListWidgetItem()
                        item.setText(f'Ви: {message}')

                        if os.path.exists(img_path):
                            icon = QIcon(img_path)
                            item.setIcon(icon)
                            font = QFont()
                            font.setPointSize(20)
                            item.setFont(font)
                            self.widgets.messages_widget.addItem(item)

                    else:
                        utils.show_message(self, 'Ви або хтось видалили файл іконки користувача. Вийдіть з серверу та виберіть її.')

                else:
                    utils.show_message(self, 'Ви не ввели повідомлення')

            except Exception as error:
                logger.error(f'Не вдалося відправити повідомлення на сервер (помилка {error})')
                self.is_connected = False
                del self.connection
                utils.show_message(self, 'Не вдалося відправити повідомлення на сервер. Можливо він перестав працювати.')

                self.widgets.messages_widget.clear()

                # Message that you need to connect to the server to communicate
                item = QListWidgetItem(self.widgets.messages_widget)
                item.setText('Вам потрібно підключитися до сервера для спілкування')
                font = QFont()
                font.setPointSize(25)
                font.setBold(True)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.widgets.messages_widget.addItem(item)

                # Unlocking settings
                self.widgets.server_ip.setEnabled(True)
                self.widgets.server_port.setEnabled(True)
                self.widgets.user_nikname.setEnabled(True)
                self.widgets.save_settings.setEnabled(True)
                self.widgets.connect_to_server.setEnabled(True)
                self.widgets.chose_avatar.setEnabled(True)
                self.widgets.set_default_avatar.setEnabled(True)

        else:
            utils.show_message(self, 'Ви не підключилися до сервера')

    def exit_from_server(self):
        """Log out of the chat room"""
        if self.is_connected:
            try:
                self.connection.exit()

                self.is_connected = False

                logger.info('Виконано вихід з серверу')

            except Exception as err:
                logger.error(f'Не вийщло вийти з серверу. Помилка {err}')
                self.is_connected = False
                utils.show_message(self, 'Не вийшло вийти з серверу, оскільки він перестав працювати')

            # Unlocking settings
            self.widgets.server_ip.setEnabled(True)
            self.widgets.server_port.setEnabled(True)
            self.widgets.user_nikname.setEnabled(True)
            self.widgets.save_settings.setEnabled(True)
            self.widgets.connect_to_server.setEnabled(True)
            self.widgets.chose_avatar.setEnabled(True)
            self.widgets.set_default_avatar.setEnabled(True)

            self.widgets.messages_widget.clear()

            # Message that you need to connect to the server to communicate
            item = QListWidgetItem(self.widgets.messages_widget)
            item.setText('Вам потрібно підключитися до сервера для спілкування')
            font = QFont()
            font.setPointSize(25)
            font.setBold(True)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.widgets.messages_widget.addItem(item)

        else:
            utils.show_message(self, 'Ви не підключилися до сервера')

    def connect_to_server(self):
        """Connect to the server"""
        ip = self.widgets.server_ip.text()
        port = self.widgets.server_port.text()
        user_nikname = self.widgets.user_nikname.text()

        # If the user has entered all fields
        if not utils.check_for_empty(ip) and not utils.check_for_empty(port) and not utils.check_for_empty(user_nikname):
            if utils.is_int(port):  # If the port is a number
                try:
                    self.connection = utils.Connection(ip, int(port), user_nikname, self.widgets.messages_widget)

                    # Adding information that the user is connected to the server
                    self.widgets.messages_widget.clear()
                    item = QListWidgetItem(self.widgets.messages_widget)
                    item.setText('Ви успішно підключені до сервера!')
                    font = QFont()
                    font.setBold(True)
                    font.setPointSize(25)
                    item.setFont(font)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.widgets.messages_widget.addItem(item)

                    self.is_connected = True

                    # Locking settings
                    self.widgets.server_ip.setEnabled(False)
                    self.widgets.server_port.setEnabled(False)
                    self.widgets.user_nikname.setEnabled(False)
                    self.widgets.save_settings.setEnabled(False)
                    self.widgets.connect_to_server.setEnabled(False)
                    self.widgets.chose_avatar.setEnabled(False)
                    self.widgets.set_default_avatar.setEnabled(False)

                    # Start monitoring of new messages from the server
                    threading.Thread(target=self.connection.messages_monitor, args=self.widgets.messages_widget).start()

                    logger.info('Підключення з сервером створене')

                except Exception as error:
                    logger.error(f'Не вдалося доєднатися до сервера за IP {ip} та портом {port}. Помилка {error}')
                    utils.show_message(self, 'Не вдалося доєднатися до сервера. Можливо такого сервера не існує або цей сервер не підтримує AChat.')

            else:
                utils.show_message(self, 'Порт повиннен бути цілим числом')

        else:
            utils.show_message(self, 'Ви не ввели всі поля')

    def closeEvent(self, a0):
        if self.is_connected:
            self.connection.exit()

        a0.accept()
