"""This is the client side of the chat"""
import socket
import select
import sys
import client_server.pars_cmd_for_client_server


class Client(object):
    """Client"""
    def __init__(self, port, address):
        self.port = port
        self.ip_address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip_address, self.port))
        self.socket_list = []

    def close_socket(self):
        """Close socket"""
        self.socket.close()

    def send_msg(self):
        """Send and accept from server"""
        # pylint: disable=unused-variable
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
    PORT, ADDRESS = client_server.pars_cmd_for_client_server.pars_cmd()
    CLIENTS = Client(PORT, ADDRESS)
    CLIENTS.send_msg()
