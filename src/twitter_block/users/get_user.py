import logging
import traceback

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import config_value
from ..utils.human_timing import human_delay


def get_user_name(driver, post):
    logger = logging.getLogger("A_LOG")
    try:
        # Find username
        username_element_wait = WebDriverWait(
            post, config_value["MIN_WAITING_TIME"] * 2
        ).until(
            EC.presence_of_element_located(
                (By.XPATH, ".//div[@data-testid='User-Name']")
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            username_element_wait,
        )
        human_delay(verbose=config_value["VERBOSE"])
        logger.debug("Find user name")
        username_element = username_element_wait.find_element(By.XPATH, ".//a")
        # print(f"{username_element.text = }")
        # user_name_a = username_element.find_element(By.XPATH, ".//a")
        username = username_element.get_attribute("href").split("/")[-1]
        logger.debug(f"Post's user name @{username}")
        return username, username_element
    except NoSuchElementException:
        # print(f"Error finding username: {e}")
        # print("Username element not found")
        logger.error("Username element not found")
        print(traceback.format_exc())
        return None
    except TimeoutException:
        # print("Page load timed out")
        logger.error("Page load timed out")
        print(traceback.format_exc())
        return None
    except Exception as e:
        # print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")
        print(traceback.format_exc())
        return None
