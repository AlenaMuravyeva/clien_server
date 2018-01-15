"""Logger"""
import logging


def logging_handler():
    """Set up logger"""
    logger_file = logging.getLogger("logger")
    logger_file.setLevel(logging.INFO)
    file_handler = logging.FileHandler("logger1.log")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    logger_file.addHandler(file_handler)
    return logger_file


# pylint: disable=invalid-name
logger = logging_handler()
