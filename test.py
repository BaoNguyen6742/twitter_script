import time
import configparser
import random
from datetime import datetime
from selenium import webdriver
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.service import Service

import traceback
from enum import Enum
import logging
import coloredlogs

import os
import time

MIN_WAITING_TIME = 1
VERBOSE = False


class FollowerStatus(Enum):
    FOLLOWING = 1
    FOLLOWING_BY_NETWORK = 2
    NOT_FOLLOWING = 3
    ERROR = 4


def human_delay(
    min_seconds=MIN_WAITING_TIME, max_seconds=MIN_WAITING_TIME * 1.5, verbose=True
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


# File operations
def load_good_users():
    if not os.path.exists("good_user.txt"):
        with open("good_user.txt", "w") as f:
            pass  # Create empty file
        return set()
    else:
        with open("good_user.txt", "r") as f:
            return {line.strip() for line in f if line.strip()}


def load_bad_users():
    if not os.path.exists("bad_user.txt"):
        with open("bad_user.txt", "w") as f:
            pass  # Create empty file
        return set()
    else:
        with open("bad_user.txt", "r") as f:
            return {line.strip() for line in f if line.strip()}


def add_user_to_file(file, username):
    with open(f"{file}_user.txt", "a") as f:
        f.write(f"{username}\n")


def initialize_twitter_browser():
    logger = logging.getLogger("A_LOG")
    opt = uc.ChromeOptions()
    opt.binary_location = "/usr/bin/google-chrome"
    chromedriver_exe_location = "chromedriver-linux64/chromedriver"
    profile_path = r"Profile 3"
    opt.add_argument(r"--user-data-dir=/home/baonguyen/.config/google-chrome")
    opt.add_argument("--profile-directory={}".format(profile_path))
    opt.add_argument("--disable-notifications")
    # print("Starting Chrome browser...")
    logger.info("Starting Chrome browser...")
    driver = uc.Chrome(
        options=opt,
        driver_executable_path=chromedriver_exe_location,
        # service=service,
    )
    driver.get("https://twitter.com")
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, "//span[text()='For you']"))
    )

    return driver


def get_user_name(driver, post):
    logger = logging.getLogger("A_LOG")
    try:
        # Find username
        WebDriverWait(driver, MIN_WAITING_TIME * 2).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-testid='User-Name']")
            )
        )
        human_delay(verbose=VERBOSE)
        logger.debug("Find user name")
        username_element = post.find_element(
            By.XPATH, ".//div[@data-testid='User-Name']//a"
        )
        # print(f"{username_element.text = }")
        # user_name_a = username_element.find_element(By.XPATH, ".//a")
        username = username_element.get_attribute("href").split("/")[-1]
        logger.debug(f"Post's user name @{username}")
        return username, username_element
    except NoSuchElementException as e:
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


def check_is_good_user(driver, action, username, username_element):
    try:
        logger = logging.getLogger("A_LOG")
        # Hover over username
        # print("Scroll to user name")
        logger.debug("Scroll to user name")
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            username_element,
        )
        human_delay(verbose=VERBOSE)
        # print("Hover over user name")
        logger.debug("Hover over user name")
        action.move_to_element(username_element).perform()
        hover_card: EC.WebElement = WebDriverWait(driver, MIN_WAITING_TIME * 3).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@data-testid='HoverCard']")
            )
        )
        human_delay(min_seconds=MIN_WAITING_TIME * 1.5, verbose=VERBOSE)
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
        logger.info("Hover out")
        body_element = driver.find_element(
            By.XPATH, "//a[@data-testid='AppTabBar_Home_Link']"
        )
        action.move_to_element(body_element).perform()
        human_delay(verbose=VERBOSE)
        return status
    except Exception as e:
        print(f"Error finding username: {e}")
        print(traceback.format_exc())
        return None


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
    except NoSuchElementException as e:
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
    except Exception as e:
        # print(f"Error finding username: {e}")
        logger.error("Error finding username")
        print(traceback.format_exc())
        return FollowerStatus.ERROR


def main():
    # Set up the WebDriver
    coloredlogs.install()
    logger = logging.getLogger("A_LOG")
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(logging.DEBUG)

    # Create a console handler
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    # Load good users
    good_user = load_good_users()
    logger.info(f"Good user list loaded")
    bad_user = load_bad_users()
    logger.info(f"Bad user list loaded")
    driver = initialize_twitter_browser()
    # Get lít of posts
    total_post = 1
    while total_post < 100:
        posts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//article[@data-testid='tweet']")
            )
        )
        # List number of posts
        logger.info(f"Number of posts: {len(posts)}")
        action = webdriver.ActionChains(driver)
        for post_idx, post in enumerate(posts):
            logger.info(f"{f"Processing post {total_post}/100":-^50}")
            logger.info(f"{f"Processing batch {post_idx+1}/{len(posts)}":-^50}")
            username, username_element = get_user_name(driver, post)
            if username in good_user or username in bad_user:
                logger.info(f"User @{username} already in bad or good user list")
                # print(f"User @{username} already in good user list")
                continue
            if username is None:
                logger.error("Username not found")
                print("Username not found")
                continue

            user_status = check_is_good_user(driver, action, username, username_element)
            match user_status:
                case FollowerStatus.FOLLOWING:
                    # print(f"User @{username} is in follower list")
                    # logger.info(f"User @{username} is in follower list")
                    good_user.add(username)
                    add_user_to_file("good", username)
                    logger.info(f"User @{username} added to good user list")
                case FollowerStatus.FOLLOWING_BY_NETWORK:
                    # print(f"User @{username} is not in follower list but in network")
                    # logger.info(
                    #     f"User @{username} is not in follower list but in network"
                    # )
                    good_user.add(username)
                    add_user_to_file("good", username)
                    logger.info(f"User @{username} added to good user list")
                case FollowerStatus.NOT_FOLLOWING:
                    bad_user.add(username)
                    add_user_to_file("bad", username)
                    logger.info(f"User @{username} added to bad user list")
                    pass
                    # logger.info(f"User @{username} is not in follower list")
                case FollowerStatus.ERROR:
                    print("Error in checking follow status")
                    logger.error("Error in checking follow status")
            total_post += 1

        # refresh the web page
        logger.info("Refreshing the page...")
        driver.refresh()

        human_delay(verbose=VERBOSE)
    logger.info("All posts processed")

    input("Press Enter to close the browser...")
    print(f"{good_user = }")


if __name__ == "__main__":
    main()
