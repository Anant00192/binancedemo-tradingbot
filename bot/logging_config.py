import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir="logs", log_file="trading_bot.log"):
    """Sets up the root logger with both file and console handlers."""

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    # avoid adding duplicate handlers if called twice
    if logger.handlers:
        return logger

    # -- file handler (debug level, rotates at 5 MB) --
    fh = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(file_fmt)

    # -- console handler (info level, minimal) --
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(console_fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
