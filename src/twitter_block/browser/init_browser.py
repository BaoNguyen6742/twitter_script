import logging
from pathlib import Path

import undetected_chromedriver as uc

# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..config import config_value


def initialize_twitter_browser():
    """
    Initialize the Twitter browser using undetected_chromedriver.

    Behavior
    --------
    -  This function sets up the Chrome browser with specific options and user data directory.

    Returns
    -------
    - driver : `WebDriver`
        An instance of the Chrome WebDriver.
    """
    logger = logging.getLogger("A_LOG")
    opt = uc.ChromeOptions()
    # opt = webdriver.ChromeOptions()
    opt.binary_location = config_value["chrome_location"]
    chromedriver_exe_location = str(Path(config_value["chrome_driver"]).resolve())
    profile_name = config_value["profile_name"]

    opt.add_argument(
        f"--user-data-dir={str(Path(config_value['chrome_profile_path']).resolve())}"
    )
    opt.add_argument(f"--profile-directory={profile_name}")
    opt.add_argument("--disable-notifications")
    logger.info("Starting Chrome browser...")
    driver = uc.Chrome(
        options=opt,
        driver_executable_path=chromedriver_exe_location,
    )
    driver.get("https://twitter.com")
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((
            By.CSS_SELECTOR,
            "[aria-label='Timeline: Your Home Timeline']",
        ))
    )

    return driver
