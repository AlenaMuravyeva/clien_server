"""This is the server side of the chat"""
import socket
import signal
import sys
import threading
import client_server.pars_cmd_for_client_server
import client_server.log
import client_server.database

DB_NAME = "users_name.db"
CLIENTS = []


def handler(signum, frame):
    """Create signal handler, for correct completion of the program"""
    print("Pressed Ctrl+c %s %s", signum, frame)
    SERVER.close_socket()
    sys.exit(0)


class ClientThread(threading.Thread):
    """Each client works in the sepsrate threading"""
    def __init__(self, client_sock, address, database):
        super(ClientThread, self).__init__()
        self.sock = client_sock
        self.address = address
        client_server.log.logger.info(
            "New connection added: address %s", address
        )
        self.database = database

    def run(self):
        client_server.log.logger.info(
            "Connection from: address %s", self.address
        )
        client_server.log.logger.info("Define status")
        self.define_status_user()
        while True:
            try:
                data = self.sock.recv(2048)
                if data == 'quit\n':
                    self.sock.close()
                if data and data != 'quit\n':
                    client_server.log.logger.info(
                        'address: %s, msg %s', self.address, data
                    )
                    msg = '<{}> {}'.format(self.address, data)
                    self.sent_to_all(msg, self.sock)
                else:
                    self.remove(self.sock)
            except socket.error:
                continue

    def define_status_user(self):
        """Ask questions which user (registered or unrigestered)"""
        self.sock.send("Are you registered. Enter yes or no")
        status = self.sock.recv(2048)
        if status == 'yes\n':
            self.action_if_status_yes()
        if status == 'no\n':
            self.action_if_status_no()

    def action_if_status_yes(self):
        """Action, if client already registered"""
        self.sock.send("Enter login")
        login = self.sock.recv(2048)
        self.sock.send("Enter password")
        password = self.sock.recv(2048)
        password_from_db = self.database.get_password(login)
        print password_from_db
        if password_from_db[0] == password:
            self.sock.send("Welcome to this chatroom!")
        else:
            other_passw = None
            counter_try = 0
            for _ in range(0, 2):
                self.sock.send(
                    "Password is not correct.Please enter correct password"
                )
                other_passw = self.sock.recv(2048)
                counter_try += 1
                if password_from_db[0] == other_passw:
                    self.sock.send("Welcome to this chatroom!")
                    break
                elif password_from_db[0] != other_passw and counter_try == 2:
                    self.sock.send(
                        "Try later. The number of attempts has expired"
                    )
                    self.sock.close()

    def action_if_status_no(self):
        """Action, if client did't registered"""
        self.sock.send("Please log in!\n")
        duplicate = True
        while duplicate is True:
            self.sock.send("Enter login")
            login = self.sock.recv(2048)
            duplicate = self.database.check_duplicate(login)
        self.sock.send("Enter password")
        password = self.sock.recv(2048)
        self.database.add_new_user(login, password)
        self.sock.send("Welcome to this chatroom!")

    def remove(self, sock):
        """Delete socket from clients list"""
        if sock in CLIENTS:
            CLIENTS.remove(sock)

    def sent_to_all(self, msg, sock):
        """Sent all clients message"""
        for item_socket in CLIENTS:
            if item_socket != sock:
                try:
                    item_socket.send(msg)
                    client_server.log.logger.info('Send datas %s', msg)
                except socket.error:
                    item_socket.close()
                    CLIENTS.remove(item_socket)


class Server(object):
    """Server"""
    def __init__(self, port, address):
        client_server.log.logger.info('creating an instance of Server')
        self.max_clients = 100
        self.port = port
        self.ip_address = str(address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip_address, self.port))
        self.socket.listen(self.max_clients)
        client_server.log.logger.info(
            "init_server: port %s, address %s", self.port, self.ip_address
        )
        self.database = client_server.database.DataBase(DB_NAME)

    def close_socket(self):
        """Close socket"""
        self.socket.close()
        client_server.log.logger.info('Close server socket')

    def run_server(self):
        """Started srver, which wait connections with new clients"""
        try:
            while True:
                client_sock, client_address = self.socket.accept()
                client_server.log.logger.info(
                    "run_server client_sock %s, addressess %s", client_sock,
                    client_address
                )
                CLIENTS.append(client_sock)
                client_server.log.logger.info('All CLIENTS %s', CLIENTS)
                newthread = ClientThread(
                    client_sock, client_address, self.database
                )
                newthread.daemon = True
                newthread.start()
        finally:
            self.close_socket()


if __name__ == '__main__':
    PORT, ADDRESS = client_server.pars_cmd_for_client_server.pars_cmd()
    SERVER = Server(PORT, ADDRESS)
    signal.signal(signal.SIGINT, handler)
    SERVER.run_server()
