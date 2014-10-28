import logging
import os

LOGGER = None


def setup_custom_logger(name, level):
    global LOGGER
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler("{}/{}.log".format(
        os.getenv('HOME'), name))
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    LOGGER = logger


def getLogger():
    global LOGGER
    if LOGGER is not None:
        return LOGGER
    return logging.getLogger()
