import socket
import pars_cmd_for_client_server


class Client():
    def __init__(self, port, address):
        self.server_port = port
        self.server_ip = address
        self.client_sock = socket.socket()
        self.client_sock.connect((self.server_ip, self.server_port))

    def close_socket(self):
        self.client_sock.close()

    def send_msg(self):
        try:
            while True:
                msg_from_usr = raw_input("Enter msg:")
                if msg_from_usr == 'quit':
                    self.close_socket()
                    break
                self.client_sock.send(msg_from_usr)
                data = self.client_sock.recv(1024)
                print data
        finally:
            self.close_socket()


if __name__ == '__main__':
    port_ent_usr, address = pars_cmd_for_client_server.pars_cmd()
    client = Client(port_ent_usr, address)
    client.send_msg()
