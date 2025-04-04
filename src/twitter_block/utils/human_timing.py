import logging
import random
import time

from ..config import config_value


def human_delay(
    min_seconds=config_value["MIN_WAITING_TIME"],
    max_seconds=config_value["MIN_WAITING_TIME"] * 1.5,
    verbose=config_value["VERBOSE"],
):
    """Add a random delay to simulate human behavior"""
    logger = logging.getLogger("A_LOG")
    if min_seconds >= max_seconds:
        max_seconds = min_seconds * 1.5
    delay = random.uniform(min_seconds, max_seconds)
    if verbose:
        logger.debug(f"Sleeping for {delay:.2f} seconds")
        # print(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)
