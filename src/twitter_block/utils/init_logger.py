import logging

import coloredlogs

from ..config import config_value


# Set up the WebDriver
def get_logger():
    logger = logging.getLogger("A_LOG")
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


logger = get_logger()
