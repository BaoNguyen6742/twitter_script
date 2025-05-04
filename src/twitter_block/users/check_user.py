import logging
import traceback

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import config_value
from ..utils.follower_status import FollowerStatus
from ..utils.human_timing import human_delay


def get_user_status(driver, action, username, username_element):
    """
    Check if the user is a good user based on their follow status.

    Behavior
    --------
    This function checks if the user is a good user by hovering over their username and checking their follow status.
    - It uses the `check_user_status` function to determine if the user is following the given username.
    - If the user is not following, it checks if they are in the network of the given username using the `check_user_status_in_network` function.
    - If the user is not in the network, it returns `FollowerStatus.NOT_FOLLOWING`.

    Parameters
    ----------
    - driver : `selenium.webdriver.Chrome`
        The Selenium WebDriver instance.
    - action : `selenium.webdriver.ActionChains`
        The ActionChains instance for performing actions on the browser.
    - username : `str`
        The username of the user to check.
    - username_element : `WebElement`
        The WebElement representing the username element.

    Returns
    -------
    - _ : `FollowerStatus | None`
        The follow status of the user or None if an error occurs.
    """
    try:
        logger = logging.getLogger("A_LOG")
        # Hover over username
        logger.debug("Hover over user name")
        action.move_to_element(username_element).perform()
        hover_card: EC.WebElement = WebDriverWait(
            driver, config_value["MIN_WAITING_TIME"] * 3
        ).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@data-testid='HoverCard']",
            ))
        )
        human_delay(
            min_seconds=config_value["MIN_WAITING_TIME"],
        )
        logger.debug("Hover card found")

        status = check_user_status(hover_card, username)
        if status == FollowerStatus.ERROR:
            logger.error("Error in checking follow status")
        elif status == FollowerStatus.FOLLOWING:
            logger.info(f"User @{username} is in follower list")
        elif status == FollowerStatus.NOT_FOLLOWING:
            status: FollowerStatus | FollowerStatus | FollowerStatus = (
                check_user_status_in_network(hover_card, username)
            )
        logger.debug("Hover out")
        body_element = driver.find_element(
            By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']"
        )
        action.move_to_element(body_element).perform()
        human_delay()
        return status
    except Exception as e:
        logger.error(f"Error finding username: {e}")
        logger.error(traceback.format_exc())
        return None


def check_user_status_in_network(hover_card: EC.WebElement, username):
    """
    Check if the user is in the network of the given username.

    Behavior
    --------
    This function checks if the user is in the network of the given username by looking for the "Followed by" text in the hover card.

    Parameters
    ----------
    - hover_card : `EC.WebElement`
        The hover card element containing user information.
    - username : `str`
        The username of the user to check.

    Returns
    -------
    - _ : `FollowerStatus`
        The follow status of the user.
    """
    try:
        logger = logging.getLogger("A_LOG")
        divs = hover_card.find_elements(
            By.XPATH,
            ".//div[contains(text(), 'Followed by')]",
        )
        if len(divs):
            logger.debug(f"User @{username} is in follower network list")
            return FollowerStatus.FOLLOWING_BY_NETWORK
        else:
            logger.debug(f"User @{username} is not in follower list")
            return FollowerStatus.NOT_FOLLOWING
    except Exception:
        logger.error("Error finding username")
        logger.error(traceback.format_exc())
        return FollowerStatus.ERROR


def check_user_status(hover_card, username):
    """
    Check if the user is following status the given username.

    Behavior
    --------
    This function checks the follow status of a user based on the hover card information.

    Parameters
    ----------
    - hover_card : `WebElement`
        The hover card element containing user information.
    - username : `str`
        The username of the user to check.

    Returns
    -------
    - _ : `FollowerStatus`
        The follow status of the user.
    """
    try:
        logger = logging.getLogger("A_LOG")
        follow_button = hover_card.find_element(By.XPATH, ".//button")
        follow_status = follow_button.get_attribute("aria-label").split()

        if follow_status[1] != f"@{username}":
            logger.error("Error in checking follow status")
            logger.error(f"Follow status: {follow_status}")
            return FollowerStatus.ERROR
        elif follow_status == ["Following", f"@{username}"]:
            # logger.debug(f"User @{username} is in follower list")
            return FollowerStatus.FOLLOWING
        else:
            return FollowerStatus.NOT_FOLLOWING
    except NoSuchElementException:
        logger.error("Username element not found")
        logger.error(traceback.format_exc())
        return FollowerStatus.ERROR
    except TimeoutException:
        logger.error("Page load timed out")
        logger.error(traceback.format_exc())
        return FollowerStatus.ERROR
    except StaleElementReferenceException:
        logger.error("Stale element reference")
        logger.error(traceback.format_exc())
        return FollowerStatus.ERROR
