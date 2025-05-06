import logging
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..utils.follower_status import FollowerStatus
from ..utils.load_user import add_user_to_file


def apply_action(
    driver,
    action,
    username,
    username_element,
    follow_status: FollowerStatus,
    good_user_list: set[str],
    bad_user_list: set[str],
) -> None:
    """
    Apply action on the user based on their follow status.

    Behavior
    --------
    This function applies actions on the user based on their follow status.
    - If the user is a good user (is following or following in network), adds them to the good user list.
    - If the user is a bad user (not following), adds them to the bad user list and mutes and blocks the user.

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
    - follow_status : `FollowerStatus`
        The follow status of the user.
    """
    add_user_to_class(
        username=username,
        follow_status=follow_status,
        good_user_list=good_user_list,
        bad_user_list=bad_user_list,
    )
    if follow_status == FollowerStatus.NOT_FOLLOWING:
        mute_and_block_user(driver, action, username_element)


def add_user_to_class(
    username: str,
    follow_status: FollowerStatus,
    good_user_list: set[str],
    bad_user_list: set[str],
):
    """
    Add a user to the appropriate list based on their follow status.

    Behavior
    --------
    This function adds a user to the good or bad user list based on their follow status.
    - If the user is a good user (is flollowing or following in network), adds them to the good user list and writes to the good user file.
    - If the user is a bad user (not following), adds them to the bad user list and writes to the bad user file and writes to the bad user file.

    Parameters
    ----------
    - username : `str`
        The username of the user to check.
    - follow_status : `FollowerStatus`
        The follow status of the user.
    - good_user_list : `set[str]`
        The set of good users.
    - bad_user_list : `set[str]`
        The set of bad users.
    """
    logger = logging.getLogger("A_LOG")
    if follow_status == FollowerStatus.ERROR:
        logger.debug(f"Error checking user @{username}")
        return
    if follow_status == FollowerStatus.NOT_FOLLOWING:
        logger.debug(f"User @{username} is a bad user")
        bad_user_list.add(username)
        add_user_to_file("bad", username)
        logger.debug(f"User @{username} added to bad user list")
        return
    if (
        follow_status == FollowerStatus.FOLLOWING
        or follow_status == FollowerStatus.FOLLOWING_BY_NETWORK
    ):
        logger.debug(f"User @{username} is a good user")
        good_user_list.add(username)
        add_user_to_file("good", username)
        logger.debug(f"User @{username} added to good user list")
        return


def mute_and_block_user(driver, action, username_element):
    """
    Mute and block a user based on their username element.

    Behavior
    --------
    This function mutes and blocks a user based on their username element.

    Parameters
    ----------
    - driver : `selenium.webdriver.Chrome`
        The Selenium WebDriver instance.
    - action : `selenium.webdriver.ActionChains`
        The ActionChains instance for performing actions on the browser.
    - username_element : `WebElement`
        The WebElement representing the username element.
    """
    try:
        logger = logging.getLogger("A_LOG")
        # action.move_to_element(username_element).perform()
        action.click(username_element).perform()
        more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='More']"))
        )
        action.click(more_button).perform()
        more_menu = driver.find_element(By.XPATH, "//div[@role='menu']")

        mute_button = WebDriverWait(more_menu, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, ".//div[@role='menuitem' and @data-testid='mute']")
            )
        )
        action.click(mute_button).perform()
        logger.debug("Muted user complete")

        action.click(more_button).perform()
        more_menu = driver.find_element(By.XPATH, "//div[@role='menu']")

        block_button = WebDriverWait(more_menu, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, ".//div[@role='menuitem' and @data-testid='block']")
            )
        )
        action.click(block_button).perform()
        confirm_block_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@role='button' and @data-testid='confirmationSheetConfirm']")
            )
        )
        action.click(confirm_block_button).perform()
        logger.debug("Blocked user complete")

        logger.debug("Muted and blocked user complete")
        back_button = driver.find_element(
            By.XPATH, "//button[@aria-label='Back' and @data-testid='app-bar-back']"
        )
        action.click(back_button).perform()
        logger.debug("Back to the timeline complete")
    except Exception as e:
        logger.error(f"Error muting and blocking user: {e}")
        logger.error(traceback.format_exc())
        return None
