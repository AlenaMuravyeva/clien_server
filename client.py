import socket
import pars_cmd_for_client_server
import select
import sys
import os


class Client():
    def __init__(self, port, address):
        self.port = port
        self.ip = address
        self.socket = socket.socket()
        self.socket.connect((self.ip, self.port))
        self.socket_list = []

    def close_socket(self):
        self.socket.close()

    def stdout_name():
        sys.stdout.write('<You> ')
        sys.stdout.flush()

    def send_msg(self):
        try:
            while True:
                self.socket_list = [sys.stdin, socket]
                read_sockets, write_sockets, error_sockets = select.select(
                    self.clients, [], []
                )
                for sock in read_sockets:
                    if self.socket == sock:
                        data = self.socket.recv(1024)
                        if not data:
                            sys.exit()
                        else:
                            sys.stdout.write(data)
                            self.stdout_name()
                    else:
                        msg = sys.stdin.readline()
                        if msg == 'quit':
                            self.socket.send(msg)
                            self.close_socket()
                            break
                        self.socket.send(msg)
                        self.stdout_name()

        finally:
            self.close_socket()


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    client = Client(port_ent_usr, address)
    client.send_msg()
