import logging
import traceback

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import WebDriverWait


def get_first_post(driver):
    """
    Get the first post from the timeline.

    Behavior
    --------
    Waits for the timeline to load and retrieves the first tweet.

    Parameters
    ----------
    - driver : `WebDriver`
        The Selenium WebDriver instance.

    Returns
    -------
    - first_post : `WebElement | None`
        The first post element or None if not found
            - The first post return is an article element with attribute data-testid='tweet'

    """
    try:
        logger = logging.getLogger("A_LOG")
        first_post = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "article[data-testid='tweet']",
            ))
        )
        logger.info("First post assigned")
        first_post_link_element = first_post.find_element(
            By.XPATH, "//time"
        ).find_element(By.XPATH, "..")
        first_post_link = first_post_link_element.get_attribute("href")
        logger.debug(f"First post link: {first_post_link}")
        return first_post
    except Exception as e:
        logger.error(f"Error getting the first post: {e}")
        return None


def get_next_post_link(driver, current_post):
    """
    Get the next post from the timeline.

    Behavior
    --------
    Waits for the next post to load and retrieves it.

    Parameters
    ----------
    - driver : `WebDriver`
        The Selenium WebDriver instance.
    - current_post : `WebElement`
        The current post element.

    Returns
    -------
    - next_post : `WebElement | None`
        The next post element or None if not found.
    """
    try:
        logger = logging.getLogger("A_LOG")
        next_post: WebElement = driver.find_elements(
            locate_with(By.XPATH, "//article[@data-testid='tweet']").to_right_of(current_post)
        )
        print(f"Find {len(next_post)} next post")
        for post in next_post:
            next_post_link = (
                post.find_element(By.XPATH, "//time")
                .find_element(By.XPATH, "..")
                .get_attribute("href")
            )
            print(f"Next post link: {next_post_link}")
        input("Enter to continue...")
        logger.info("Next post link found")
        logger.debug(f"Next post link: {next_post_link}")
        return next_post_link
    except Exception as e:
        logger.error(f"Error getting the next post: {e}")
        logger.error(traceback.format_exc())
        return None
