import logging
import random
import time

from ..config import config_value


def human_delay(
    min_seconds=config_value["MIN_WAITING_TIME"],
    max_seconds=config_value["MIN_WAITING_TIME"] * 1.5,
    verbose=config_value["VERBOSE"],
):
    """
    Sleep for a random amount of time between min_seconds and max_seconds.

    Behavior
    --------
    1. If min_seconds is greater than max_seconds, set max_seconds to min_seconds * 1.5.
    2. Generate a random delay between min_seconds and max_seconds.
    3. If verbose is True, log the delay time.
    4. Sleep for the generated delay time.

    Parameters
    ----------
    - min_seconds : `float`. Optional, by default `config_value["MIN_WAITING_TIME"]`
        The minimum number of seconds to sleep,
    - max_seconds : `float`. Optional, by default `config_value["MIN_WAITING_TIME"]*1.5`
        The maximum number of seconds to sleep,
    - verbose : `bool`. Optional, by default `config_value["VERBOSE"]`
        If True, log the delay time.
    """
    logger = logging.getLogger("A_LOG")
    if min_seconds >= max_seconds:
        max_seconds = min_seconds * 1.5
    delay = random.uniform(min_seconds, max_seconds)
    if verbose:
        logger.debug(f"Sleeping for {delay:.2f} seconds")
    time.sleep(delay)
