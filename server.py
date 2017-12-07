import socket
import pars_cmd_for_client_server
import signal
import sys
import threading
import log


clients = []


def handler(signum, frame):
    print("Pressed Ctrl+c {}{}".format(signum, frame))
    server.close_socket()
    sys.exit(0)


class ClientThread(threading.Thread):
    def __init__(self, client_sock, address):
        super(ClientThread, self).__init__()
        self.sock = client_sock
        self.address = address
        log.logger.info("New connection added: address {}".format(address))

    def run(self):
        log.logger.info("Connection from: address {}".format(self.address))
        self.sock.send("Welcome to this chatroom!")
        while True:
            try:
                data = self.sock.recv(2048)
                if data == 'quit\n':
                    self.sock.close()
                if data and data != 'quit\n':
                    log.logger.info(
                        'address: {}, msg {}'.format(self.address, data)
                    )
                    msg = '<{}> {}'.format(self.address, data)
                    self.sent_to_all(msg, self.sock)
                else:
                    self.remove(self.sock)
            except socket.error:
                continue

    def remove(self, sock):
        if sock in clients:
            clients.remove(sock)

    def sent_to_all(self, msg, socket):
        for item_socket in clients:
            if item_socket != socket:
                try:
                    item_socket.send(msg)
                    log.logger.info('Send datas {}'.format(msg))
                except socket.error:
                    item_socket.close()
                    clients.remove(item_socket)


class Server():
    def __init__(self, port, address):
        log.logger.info('creating an instance of Server')
        self.max_clients = 100
        self.port = port
        self.ip = str(address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                client_sock, client_address = self.socket.accept()
                print client_sock
                log.logger.info(
                    "run_server client_sock {}, addressess{}".format(
                        client_sock, client_address
                    )
                )
                clients.append(client_sock)
                log.logger.info('All clients {}'.format(clients))
                newthread = ClientThread(client_sock, client_address)
                newthread.daemon = True
                newthread.start()
        finally:
            self.close_socket()


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    server = Server(port_ent_usr, address)
    signal.signal(signal.SIGINT, handler)
    server.run_server()
