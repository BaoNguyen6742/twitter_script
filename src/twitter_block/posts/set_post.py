import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def set_next_post(driver, next_post_link):
    """
    Return the next post from the timeline.

    Behavior
    --------
    This function retrieves the next post from the user's timeline and performs necessary actions.

    Parameters
    ----------
    - driver : `WebDriver`
        The Selenium WebDriver instance used to interact with the browser.
    - next_post_link : `str`
        The URL link to the next post to be processed.

    Returns
    -------
    - tweet : `WebElement | None`
        The next post element or None if not found.
        - The next post return is an article element with attribute data-testid='tweet'
    """
    try:
        logger = logging.getLogger("A_LOG")
        # Wait for the next post to load
        next_post_link_element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, f"//a[@href='{next_post_link.replace('https://x.com', '')}']"))
        )
        logger.info("Next post assigned")

        xpath = "./ancestor::article[@data-testid='tweet']"
        tweet = next_post_link_element.find_element(By.XPATH, xpath)
        return tweet
    except Exception as e:
        logger.error(f"Error getting the next post: {e}")
        return None
