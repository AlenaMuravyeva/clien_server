"""Parser for the configuration file"""
import argparse
import json
import re


def validation_value_port(user_defined_port):
    """The port value is validated"""
    if user_defined_port <= 1023 or user_defined_port >= 65535:
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


def total_validation(user_defined_port, user_defined_address):
    """
    Total validation for port and ip_address and resive data of cmd,
    if port and ip_address are  not correct
    """
    user_input_port = user_defined_port
    user_input_address = user_defined_address
    while validation_value_port(user_defined_port) is False:
        user_input_port = raw_input(
            "Enter other port value from 1023 to 65535   "
        )
        user_defined_port = user_input_port
    while address_validation(user_defined_address) is False:
        user_input_address = raw_input(
            "Enter other address value: 127.0.0.1 "
        )
        user_defined_address = user_input_address
    return user_defined_port, user_defined_address


def args_validation(args):
    """Read args from file"""
    if args.file:
        readed_file = args.file.read()
        data = json.loads(readed_file)
        user_defined_port = data["Server_config"]["port"]
        user_defined_address = data["Server_config"]["address"]
        return total_validation(user_defined_port, user_defined_address)

    else:
        return total_validation(user_defined_port, user_defined_address)


def pars_cmd():
    """Created parser, which adds new arguments"""
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--file", dest="file", type=argparse.FileType('r'))
    return args_validation(parser.parse_args())


if __name__ == '__main__':
    pass
