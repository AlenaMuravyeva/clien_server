import socket
import pars_cmd_for_client_server
import select
import sys


class Client():
    def __init__(self, port, address):
        self.port = port
        self.ip = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.socket_list = []

    def close_socket(self):
        self.socket.close()

    def send_msg(self):
        while True:
            self.socket_list = [sys.stdin, self.socket]
            read_sockets, write_sockets, error_sockets = select.select(
                self.socket_list, [], []
            )
            for sock in read_sockets:
                if sock == self.socket:
                    msg = sock.recv(2048)
                    print msg
                else:
                    msg = sys.stdin.readline()
                    if msg == 'quit\n':
                        self.socket.send(msg)
                        self.socket.close()
                        sys.exit()
                    else:
                        self.socket.send(msg)
                        sys.stdout.flush()
        self.close_socket()


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    client = Client(port_ent_usr, address)
    client.send_msg()
