import logging


import os


def get_logger():
    logger = logging.getLogger(__name__)
    if os.getenv("ENVIRONMENT") == "local":
        logger.propagate = False
    return logger
