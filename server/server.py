from cryptography.fernet import Fernet
import socket
import pickle
import threading


class Server:
    """Сервер AChat 2.0"""
    def __init__(self, ip, port):
        self.server_sock = socket.socket()

        try:
            self.server_sock.bind((ip, int(port)))

            self.str_key = Fernet.generate_key()
            self.key = Fernet(self.str_key)
            self.users = []  # Список сокетів користувачів (для розсилки)

            self.server_sock.listen(0)
            self.users_monitor()

        except:
            print('Не вдалося створити сервер. Невірний IP та порт або такий адрес вже зайнятий')

    def users_monitor(self):
        """Моніторинг нових користувачів"""
        while True:
            try:
                user, adr = self.server_sock.accept()

                # Надсилаємо ключ шифрування
                # ['KEY', self.str_key]
                request = pickle.dumps(['KEY', self.str_key])
                user.send(request)

                # Отримуємо нікнейм користувача
                # ['NIKNAME', <нікнейм>]
                data = user.recv(1024)
                user_nikname = pickle.loads(self.key.decrypt(data))

                if user_nikname[0] == 'NIKNAME':
                    user_nikname = user_nikname[1]

                    request = self.key.encrypt(pickle.dumps(['NEW_USER', user_nikname]))

                    for i in self.users:
                        i.send(request)

                    self.users.append(user)
                    print(f'{user_nikname} доєднався до чату')

                    # Запуск потока обробки користувача
                    threading.Thread(
                        target=self.user_handler,
                        args=(user, user_nikname)).start()

                else:
                    continue

            except:
                print('Не вийшло доєднати користувача')

    def user_handler(self, user_sock, nikname):
        """User Handler"""
        while True:
            try:
                data = user_sock.recv(100_000)
                data = pickle.loads(self.key.decrypt(data))

                # Запрос на відключення
                # ['EXIT']
                if data[0] == 'EXIT':
                    self.users.remove(user_sock)

                    request = self.key.encrypt(pickle.dumps(['EXIT', nikname]))

                    for i in self.users:
                        i.send(request)

                    print(f'{nikname} вийшов з чату')
                    break

                # Запрос на нове повідомлення
                # ['MESSAGE', <msg>, icon]
                if data[0] == 'MESSAGE':
                    message = data[1]
                    user_icon = data[2]
                    request = ['MESSAGE', message, user_icon, nikname]

                    for i in self.users:
                        if i != user_sock:
                            i.send(self.key.encrypt(pickle.dumps(request)))

                    print(f'{nikname}: {message}')

                else:
                    break

            except:
                print(f'Помилка обробника користувача {nikname}')
                break


if __name__ == '__main__':
    ip = input('Введіть IP сервера: ')
    port = input('Введіть порт сервера: ')
    Server(ip, port)
