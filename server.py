import socket
import pars_cmd_for_client_server
import signal
import sys
import logging


def handler(signum, frame):
    print("Pressed Ctrl+c {}{}".format(signum, frame))
    server.close_socket()
    sys.exit(0)


class Server():
    def __init__(self, port, address):
        logger.info('creating an instance of Server')
        self.max_clients = 1
        self.server_listen_port = port
        self.server_listen_ip = str(address)
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def init_server(self):
        self.server_sock.bind((self.server_listen_ip, self.server_listen_port))
        self.server_sock.listen(self.max_clients)
        logger.info("init_server: port {}, address {}".format(
            self.server_listen_port, self.server_listen_ip)
        )

    def close_socket(self):
        self.server_sock.close()
        logger.info('Close server socket')

    def run_server(self):
        try:
            self.client_sock, self.client_addr = self.server_sock.accept()
            logger.info(
                "run_server client_sock {}, client_address{}".format(
                    self.client_sock, self.client_addr
                )
            )
            while True:
                client_data = self.client_sock.recv(1024)
                if client_data:
                    self.client_sock.send(client_data)
                    logger.info('Send data {}'.format(client_data))
        finally:
            self.close_socket()


if __name__ == '__main__':
    logger = logging.getLogger("loger")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logger1.log")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    server = Server(port_ent_usr, address)
    server.init_server()
    signal.signal(signal.SIGINT, handler)
    server.run_server()
