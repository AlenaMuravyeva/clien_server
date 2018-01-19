"""Tests chat"""
# pylint: disable=redefined-outer-name
import json
import socket
import time
import sqlite3
import pytest
from client_server import pars_cmd_for_client_server
from client_server import server
from client_server import database


class FileMock(object):
    """Mock for config file"""
    def __init__(self, input_data):
        self.data = input_data

    def read(self):
        """Return data, which dumps json modul"""
        return json.dumps(self.data)


class SocketMock(object):
    """Mock for socket"""
    def __init__(self, param_list):
        self.params = []
        self.params.extend(param_list)
        self.client_socket = "mock client_socket"
        self.counter_send = 0
        self.msg = None

    def setsockopt(self, value1, value2, number):
        """Setsockopt"""
        pass

    def bind(self, connection_param):
        """Bind port and address"""
        pass

    def listen(self, max_clients):
        """Listen clients"""
        pass

    def accept(self):
        """Return client_socket, client_address"""
        if self.params:
            return (self.client_socket, self.params.pop())
        else:
            while True:
                time.sleep(10)

    def send(self, msg):
        """Send data"""
        self.counter_send += 1
        self.msg = msg

    def close(self):
        """Close socket"""
        pass


class ThreadMock(object):
    """Mock for thread"""
    def __init__(self, client_sock, client_address, user_database):
        self.sock = client_sock
        self.address = client_address
        self.database = user_database

    def remove(self, socket):
        """Remove socket """
        pass

    def start(self):
        """Start thread"""
        pass

    def daemon(self):
        """Daemom thread"""
        pass


class ConnectMock(object):
    """Mock for connect"""
    def __init__(self, name_db, check_same_thread):
        pass

    def cursor(self):
        """Create cursor"""
        return CursorMock("str_request")


class CursorMock(object):
    """Mock for cursor"""
    def __init__(self, str_request):
        self.str_request = str_request
        self.data = None

    def execute(self, str_request):
        """Execute from db"""
        list_words_str_request = str_request.split(' ')
        self.data = list_words_str_request[-1]
        self.data = self.data[1:-1]

    def fetchone(self):
        """Fetchone from db"""
        return self.data


class DatabaseMock(object):
    """Mock for database"""
    def __init__(self, name_db):
        self.name = name_db

    def start(self):
        """Start db"""
        pass

    def daemon(self):
        """Daemom thread"""
        pass


@pytest.mark.parametrize("test_input,expected", [
    (
        1500, True
    ),
    (
        77000, False
    ),
])
def test_validation_value_port(test_input, expected):
    """ Test, which check the port value is valid"""
    return_value = pars_cmd_for_client_server.validation_value_port(test_input)
    assert return_value == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        '127.0.0.1', True
    ),
    (
        '0.0', False
    ),
])
def test_address_validation(test_input, expected):
    """ Test, which check the address value is valid"""
    return_value = pars_cmd_for_client_server.address_validation(test_input)
    assert return_value == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        FileMock({
            "Server_config": {
                "port": 1500,
                "address": "127.0.0.1"
            }
        }
                ),
        (1500, "127.0.0.1")
    ),
])
def test_args_validation(test_input, expected):
    """ Test, which check parsing and assignmenting args"""
    assert pars_cmd_for_client_server.args_validation(test_input) == expected


@pytest.mark.parametrize("test_input", [
    (
        FileMock({
            "Server_config": {
                "port": 0,
                "address": "127.0.0"
            }
        }
                )
    ),
])
def test_raise_exception_validation_value(test_input):
    """Test, which raise exception, if port or address not correct"""
    with pytest.raises(pars_cmd_for_client_server.ValidationValueError):
        pars_cmd_for_client_server.args_validation(test_input)


@pytest.mark.parametrize("test_input, expected", [
    (
        [1500, '127.0.0.1'], 1
    ),
])
def test_accept_client(test_input, expected):
    """Test, which add clients in list"""
    # pylint: disable=unused-argument
    def monkey_socket(port, address):
        """monkeypatch for socket.socket"""
        return SocketMock(test_input)

    socket.socket = monkey_socket
    server_instanse = server.Server(DatabaseMock("users_db"), *test_input)
    server_instanse.accept_client()
    assert len(server.CLIENTS) == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            "client_sock1", "client_sock2", "client_sock3"
        ], 2
    ),
])
def test_remove(test_input, expected):
    """Test, which remove clients in list"""
    server.CLIENTS = test_input
    client_thread = server.ClientThread("client_sock2", "address", "database")
    client_thread.remove("client_sock2")
    assert len(server.CLIENTS) == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            [
                [1500, '127.0.0.1'], [1400, '127.0.0.1'], [1600, '127.0.0.1'],
                [1800, '127.0.0.1'], "Hello"
            ], 0
        ]
    )
])
def test_sent_to_all(test_input, expected):
    """Test, which check sending msg current client """
    server.CLIENTS = SocketMock(test_input[0]), SocketMock(test_input[1]),
    SocketMock(test_input[2])
    sock, msg = SocketMock(test_input[3]), test_input[4]
    client_thread = server.ClientThread("client_sock2", "address", "database")
    client_thread.sent_to_all(msg, sock)
    assert sock.counter_send == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            ["user_db", "alena"], True
        ]
    ),
])
def test_check_duplicate(test_input, expected):
    """Test, which check return value"""
    def monkey_connect(name_db, check_same_thread):
        """"monkeypatch for connect"""
        return ConnectMock(name_db, check_same_thread)
    name_db, login = test_input
    sqlite3.connect = monkey_connect
    user_db = database.DataBase(name_db)
    assert user_db.check_duplicate(login) == expected


@pytest.mark.parametrize("test_input, expected", [
    (
        [
            ["user_db", "alena"], "alena"
        ]
    ),
])
def test_get_password(test_input, expected):
    """Test, which check get value"""
    def monkey_connect(name_db, check_same_thread):
        """monkeypatch for connect"""
        return ConnectMock(name_db, check_same_thread)
    name_db, login = test_input
    sqlite3.connect = monkey_connect
    user_db = database.DataBase(name_db)
    assert user_db.get_password(login) == expected
