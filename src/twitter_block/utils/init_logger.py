import logging
from pathlib import Path

import coloredlogs

from ..config import config_value


# Set up the WebDriver
def get_logger():
    """
    Generate a logger or return the existing one.

    Behavior
    --------
    - If the logger already exists, it will return the existing logger.
    - If the logger does not exist, it will create a new logger with the specified configuration.
    - The logger will log messages to both a file and the console.
    - The log level and format are configurable through the `config_value` dictionary.

    Returns
    -------
    - logger: `logging.Logger`
        The logger instance configured with the specified settings.
    """
    logger = logging.getLogger("A_LOG")
    if logger.hasHandlers():
        return logger
    logger.setLevel(getattr(logging, config_value["LOG_LEVEL"]))
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # Create a file handler
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(getattr(logging, config_value["LOG_LEVEL"]))

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config_value["LOG_LEVEL"]))
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        r"%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    coloredlogs.install(
        level=config_value["LOG_LEVEL"],
        level_styles={
            "info": {"color": "green"},
            "debug": {"color": "blue"},
            "warning": {"color": "yellow"},
            "error": {"color": "red"},
            "critical": {"color": "red", "bold": True},
        },
        logger=logger,
        fmt=formatter._fmt,
        datefmt=r"%Y-%m-%d %H:%M:%S",
        field_styles={
            "asctime": {"color": "green"},
            "name": {"color": "cyan"},
            # Leave levelname empty to use level_styles
        },
        force_colors=True,
        isatty=True,
    )
    return logger


def clear_log():
    """
    Clear the log file if it exists.
    
    Behavior
    --------
    - If the log file `debug.log` exists, it will be deleted.
    """
    if Path("debug.log").exists():
        Path("debug.log").unlink(missing_ok=True)
