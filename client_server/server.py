import socket
import signal
import sys
import threading
import sqlite3
import time
from . import pars_cmd_for_client_server
from . import log

DB_NAME = "users_name.db"
CLIENTS = []


def handler(signum, frame):
    print("Pressed Ctrl+c %s %s", signum, frame)
    SERVER.close_socket()
    sys.exit(0)


class DataBase(object):
    """Initializes database."""
    def __init__(self, name_database):
        self.database = name_database
        self.created_db()

    def created_db(self):
        log.logger.info("Initialization SQL %s", self.database)
        try:
            self.connection_db = sqlite3.connect(
                self.database, check_same_thread=False
            )
            self.cur = self.connection_db.cursor()
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS users (login VARCHAR, password VARCHAR)"
            )
            log.logger.info("Initialization SQL: DB is initialized OK...")

        except sqlite3.DatabaseError as err:
            print("Initialization SQL: DB creation FAIL: %s", err)
            log.logger.info(
                "Initialization SQL: DB creation FAIL: %s", err
            )
            sys.exit(1)

    def check_duplicate(self, login):
        data = False
        get_login = "SELECT login FROM users WHERE login = '{}'".format(login)
        self.cur.execute(get_login)
        data = self.cur.fetchone()
        if data is None:
            return data
        else:
            data = True
            return data

    def get_password(self, login):
        password = None
        get_password = "SELECT  password FROM users WHERE login = '{}'".format(login)
        self.cur.execute(get_password)
        password = self.cur.fetchone()
        return password

    def add_new_user(self, login, password):
        login_password = (login, password)
        new_entry = ("INSERT INTO users VALUES(?,?)")
        self.cur.execute(new_entry, login_password)
        self.connection_db.commit()


class ClientThread(threading.Thread):
    def __init__(self, client_sock, address, database):
        super(ClientThread, self).__init__()
        self.sock = client_sock
        self.address = address
        log.logger.info("New connection added: address %s", address)
        self.database = database

    def run(self):
        log.logger.info("Connection from: address %s", self.address)
        log.logger.info("Define status")
        self.define_status_user()
        while True:
            try:
                data = self.sock.recv(2048)
                if data == 'quit\n':
                    self.sock.close()
                if data and data != 'quit\n':
                    log.logger.info('address: %s, msg %s', self.address, data)
                    msg = '<{}> {}'.format(self.address, data)
                    self.sent_to_all(msg, self.sock)
                else:
                    self.remove(self.sock)
            except socket.error:
                continue

    def define_status_user(self):
        self.sock.send("Are you registered. Enter yes or no")
        status = self.sock.recv(2048)
        if status == 'yes\n':
            self.action_if_status_yes()
        if status == 'no\n':
            self.action_if_status_no()

    def action_if_status_yes(self):
        self.sock.send("Enter login")
        login = self.sock.recv(2048)
        self.sock.send("Enter password")
        password = self.sock.recv(2048)
        password_from_db = self.database.get_password(login)
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
                    time.sleep(60)
                    self.action_if_status_yes()

    def action_if_status_no(self):
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
        if sock in CLIENTS:
            CLIENTS.remove(sock)

    def sent_to_all(self, msg, sock):
        for item_socket in CLIENTS:
            if item_socket != sock:
                try:
                    item_socket.send(msg)
                    log.logger.info('Send datas %s', msg)
                except socket.error:
                    item_socket.close()
                    CLIENTS.remove(item_socket)


class Server(object):
    def __init__(self, port, address):
        log.logger.info('creating an instance of Server')
        self.max_clients = 100
        self.port = port
        self.ip_address = str(address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip_address, self.port))
        self.socket.listen(self.max_clients)
        log.logger.info(
            "init_server: port %s, address %s", self.port, self.ip_address
        )
        self.database = DataBase(DB_NAME)

    def close_socket(self):
        self.socket.close()
        log.logger.info('Close server socket')

    def run_server(self):
        try:
            while True:
                client_sock, client_address = self.socket.accept()
                print client_sock
                log.logger.info(
                    "run_server client_sock %s, addressess %s", client_sock,
                    client_address
                )
                CLIENTS.append(client_sock)
                log.logger.info('All CLIENTS %s', CLIENTS)
                newthread = ClientThread(
                    client_sock, client_address, self.database
                )
                newthread.daemon = True
                newthread.start()
        finally:
            self.close_socket()


if __name__ == '__main__':
    PORT, ADDRESS = pars_cmd_for_client_server.pars_cmd()
    SERVER = Server(PORT, ADDRESS)
    DATADASE = DataBase(DB_NAME)
    signal.signal(signal.SIGINT, handler)
    SERVER.run_server()
