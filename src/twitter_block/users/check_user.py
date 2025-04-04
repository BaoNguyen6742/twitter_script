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


def check_is_good_user(driver, action, username, username_element):
    try:
        logger = logging.getLogger("A_LOG")
        # Hover over username
        # print("Scroll to user name")

        # print("Hover over user name")
        logger.debug("Hover over user name")
        action.move_to_element(username_element).perform()
        hover_card: EC.WebElement = WebDriverWait(
            driver, config_value["MIN_WAITING_TIME"] * 3
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-testid='HoverCard']")
            )
        )
        human_delay(
            min_seconds=config_value["MIN_WAITING_TIME"],
        )
        # print("Hover card found")
        logger.debug("Hover card found")

        status = check_user_status(driver, action, hover_card, username)
        if status == FollowerStatus.ERROR:
            # print("Error in checking follow status")
            logger.error("Error in checking follow status")
            # return None
        elif status == FollowerStatus.FOLLOWING:
            # print(f"User @{username} is in follower list")
            logger.info(f"User @{username} is in follower list")
            # return True
        elif status == FollowerStatus.NOT_FOLLOWING:
            status = check_user_status_in_network(driver, action, hover_card, username)
        # print("Hover out")
        logger.debug("Hover out")
        body_element = driver.find_element(
            By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']"
        )
        action.move_to_element(body_element).perform()
        human_delay()
        return status
    except Exception as e:
        print(f"Error finding username: {e}")
        print(traceback.format_exc())
        return None


def check_user_status_in_network(driver, action, hover_card: EC.WebElement, username):
    try:
        logger = logging.getLogger("A_LOG")
        divs = hover_card.find_elements(
            By.XPATH,
            ".//div[contains(text(), 'Followed by')]",
        )
        if len(divs):
            logger.debug(f"User @{username} is not in follower list but in network")
            return FollowerStatus.FOLLOWING_BY_NETWORK
        else:
            logger.debug(f"User @{username} is not in follower list and not in network")
            return FollowerStatus.NOT_FOLLOWING
    except Exception:
        # print(f"Error finding username: {e}")
        logger.error("Error finding username")
        print(traceback.format_exc())
        return FollowerStatus.ERROR


def check_user_status(driver, action, hover_card, username):
    try:
        logger = logging.getLogger("A_LOG")
        follow_button = hover_card.find_element(By.XPATH, ".//button")
        follow_status = follow_button.get_attribute("aria-label").split()

        if follow_status[1] != f"@{username}":
            # print("Error in checking follow status")
            # print(f"Follow status: {follow_status}")
            logger.error("Error in checking follow status")
            logger.error(f"Follow status: {follow_status}")
            return FollowerStatus.ERROR
        elif follow_status == ["Following", f"@{username}"]:
            # print(f"User @{username} is in follower list")
            logger.debug(f"User @{username} is in follower list")
            return FollowerStatus.FOLLOWING
        else:
            # print(f"User @{username} is not in follower list")
            logger.debug(f"User @{username} is not in follower list")
            return FollowerStatus.NOT_FOLLOWING
    except NoSuchElementException:
        # print(f"Error finding username: {e}")
        # print("Username element not found")
        logger.error("Username element not found")
        print(traceback.format_exc())
        return FollowerStatus.ERROR
    except TimeoutException:
        # print("Page load timed out")
        logger.error("Page load timed out")
        print(traceback.format_exc())
        return FollowerStatus.ERROR
    except StaleElementReferenceException:
        # print(f"{hover_card = }")
        logger.error("Stale element reference")
        print(traceback.format_exc())
        return FollowerStatus.ERROR
    # finally:
    #     print(f"{follow_status = }")
    # print(f"An error occurred: {e}")
    # return None
