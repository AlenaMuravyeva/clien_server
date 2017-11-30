import socket
import pars_cmd_for_client_server
import signal
import sys


def print_info(data):
    print("{}".format(data))


def handler(signum, frame):
    print_info("Pressed Ctrl+c {}{}".format(signum, frame))
    server.close_socket()
    sys.exit(0)


class Server():
    def __init__(self, port, address):
        self.max_clients = 1
        self.server_listen_port = port
        self.server_listen_ip = str(address)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def init_server(self):
        self.server_sock.bind((self.server_listen_ip, self.server_listen_port))
        self.server_sock.listen(self.max_clients)
        print_info("init_server with port {}, address {}".format(
            self.server_listen_port, self.server_listen_ip)
        )

    def close_socket(self):
        self.server_sock.close()

    def run_server(self):
        try:
            self.client_sock, self.client_addr = self.server_sock.accept()
            print_info(
                "run_server client_sock {}, client_address{}".format(
                    self.client_sock, self.client_addr
                )
            )
            while True:
                client_data = self.client_sock.recv(1024)
                if client_data:
                    print(client_data)
                    self.client_sock.send(client_data)
        finally:
            self.close_socket()


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    server = Server(port_ent_usr, address)
    server.init_server()
    signal.signal(signal.SIGINT, handler)
    server.run_server()
