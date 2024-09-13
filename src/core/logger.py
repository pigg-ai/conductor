import logging
import os
from logging.handlers import TimedRotatingFileHandler

import sys

log_path = os.path.join(sys.path[0], "logs", "app.log")


def setup_logger(name, log_file=log_path, level=logging.DEBUG):
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create a rotating file handler that creates a new log file every day
    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7
    )
    handler.suffix = "%Y%m%d"  # Add date to the filename
    handler.setLevel(level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Avoid duplicate logging by removing existing handlers
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger


logger = setup_logger(__name__)
