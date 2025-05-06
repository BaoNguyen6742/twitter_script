import logging
import traceback

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import config_value
from ..utils.human_timing import human_delay


def get_user_name(driver, post):
    """
    Get the username and username element from a post.

    Behavior
    --------
    1. Wait for the username element to be present in the post.
    2. Scroll the username element into view.
    3. Extract the username from the element's href attribute.


    Parameters
    ----------
    - driver : `selenium.webdriver.Chrome`
        The Selenium WebDriver instance.
    - post : `WebElement`
        The post element from which to extract the username.

    Returns
    -------
    - username : `str`
        The extracted username from the post. The name doesn't include the '@' symbol.
    - username_element : `WebElement`
        The username element found in the post. The user element is the `a` tag that contain the Display name, not the username.
    """
    logger = logging.getLogger("A_LOG")
    try:
        # Find username
        username_element_div = WebDriverWait(
            post, config_value["MIN_WEB_WAITING_TIME"] * 2
        ).until(
            EC.presence_of_element_located((
                By.XPATH,
                ".//div[@data-testid='User-Name']/div[1]",
            ))
        )
        driver.execute_script(
            (
                "arguments[0].scrollIntoView({block: 'center', behavior: 'auto'});"
                "window.scrollBy(0, window.innerHeight * 0.1);"
            ),
            username_element_div,
        )
        human_delay(verbose=config_value["VERBOSE"])
        logger.debug("Find user name")
        username_element = username_element_div.find_element(By.XPATH, ".//a")
        username = username_element.get_attribute("href").split("/")[-1]
        logger.debug(f"Post's user name @{username}")
        return username, username_element
    except NoSuchElementException:
        logger.error("Username element not found")
        logger.error(traceback.format_exc())
        return None, None
    except TimeoutException:
        logger.error("Page load timed out")
        logger.error(traceback.format_exc())
        return None, None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())
        return None, None
