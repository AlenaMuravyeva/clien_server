import logging


def logging_handler():
    logger = logging.getLogger("logger")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("logger1.log")
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


logger = logging_handler()
