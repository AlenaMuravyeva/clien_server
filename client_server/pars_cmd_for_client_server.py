"""Parser for the configuration file"""
import argparse
import json
import re


class ValidationValueError(Exception):
    """Exception, if port or address are not correct"""
    pass


def validation_value_port(port):
    """The port value is validated"""
    if port <= 1023 or port >= 65535:
        return False
    else:
        return True


def address_validation(address):
    """The address value is validated"""
    # pylint: disable=anomalous-backslash-in-string
    result = re.match(
        r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        address
    )
    if result is None:
        return False
    else:
        return True


def args_validation(args_file):
    """Read args from file"""
    print args_file
    if args_file:
        readed_file = args_file.read()
        print readed_file
        data = json.loads(readed_file)
        port = data["Server_config"]["port"]
        address = data["Server_config"]["address"]
        value_port = validation_value_port(port)
        value_address = address_validation(address)
        if value_port is False or value_address is False:
            raise ValidationValueError()
        else:
            return port, address


def pars_cmd():
    """Created parser, which adds new arguments"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--file", dest="file", type=argparse.FileType('r'))
    args = parser.parse_args()
    return args_validation(args.file)


if __name__ == '__main__':
    pass
