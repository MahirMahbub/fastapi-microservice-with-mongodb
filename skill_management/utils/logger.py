import logging


import os
from logging import Logger


def get_logger() -> Logger:
    logger: Logger = logging.getLogger(__name__)
    if os.getenv("ENVIRONMENT") == "local":
        logger.propagate = False
    return logger
