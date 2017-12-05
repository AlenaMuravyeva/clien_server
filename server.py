import socket
import pars_cmd_for_client_server
import signal
import sys
import threading
import log
import select


def handler(signum, frame):
    print("Pressed Ctrl+c {}{}".format(signum, frame))
    server.close_socket()
    sys.exit(0)


class ClientThread(threading.Thread):
    def __init__(self, address, client_sock):
        super(ClientThread, self).__init__()
        self.sock = client_sock
        self.address = address
        log.logger.info("New connection added: address {}".format(address))

    def run(self):
        log.logger.info("Connection from: address {}".format(self.address))
        data = self.sock.recv(1024)
        if data:
            if data == 'quit':
                self.sock.close()
        server.clients.append(self.sock)
        log.logger.info('Client registered name: {}'.format(data))
        log.logger.info('All clients {}'.format(server.clients))
        while True:
            data = self.sock.recv(1024)
            if data == 'quit':
                self.sock.close()
            if data:
                log.logger.info('Dispatching msg {}'.format(data))
                server.sent_to_all(data, socket)


class Server():
    def __init__(self, port, address):
        log.logger.info('creating an instance of Server')
        self.max_clients = 1
        self.port = port
        self.ip = str(address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.clients.append(socket)

    def init_server(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(self.max_clients)
        log.logger.info("init_server: port {}, address {}".format(
            self.port, self.ip)
        )

    def close_socket(self):
        self.socket.close()
        log.logger.info('Close server socket')

    def run_server(self):
        try:
            while True:
                read_sockets, write_sockets, error_sockets = select.select(
                    self.clients, [], [], 0.5
                )
                self.client_sock, self.address = self.socket.accept()
                log.logger.info(
                    "run_server client_sock {}, addressess{}".format(
                        self.client_sock, self.address
                    )
                )
                newthread = ClientThread(self.address, self.client_sock)
                newthread.daemon = True
                newthread.start()
        finally:
            self.close_socket()

    def sent_to_all(self, data, socket):
        for item_socket in self.clients:
            if item_socket != socket and item_socket != item_socket:
                try:
                    item_socket.send(data)
                    log.logger.info('Send datas {}'.format(data))
                except:
                    item_socket.close()
                    self.clients.remove(item_socket)


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    server = Server(port_ent_usr, address)
    server.init_server()
    signal.signal(signal.SIGINT, handler)
    server.run_server()
