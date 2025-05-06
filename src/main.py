import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By

from twitter_block.browser.init_browser import initialize_twitter_browser
from twitter_block.config import config_value
from twitter_block.posts.get_post import get_first_post, get_next_post_link
from twitter_block.posts.set_post import set_next_post
from twitter_block.users import apply_action, check_user, get_user
from twitter_block.utils import init_logger
from twitter_block.utils.follower_status import FollowerStatus
from twitter_block.utils.load_user import (
    load_bad_users,
    load_good_users,
)
from twitter_block.utils.program_status import ProgramStatus


def main() -> None:
    init_logger.clear_log()
    logger = init_logger.get_logger()
    good_user = load_good_users(clear=True)
    bad_user = load_bad_users(clear=True)

    try:
        driver = initialize_twitter_browser()
    except Exception as e:
        logger.error(f"Error initializing Twitter browser: {e}")
        logger.error(traceback.format_exc())
        return

    action = webdriver.ActionChains(driver)
    overall_post = 0
    while True:
        total_post = 0
        good_user_streak = 0
        first_post = get_first_post(driver)
        if first_post is None:
            logger.error("No posts found. Exiting...")
            break
        current_post = first_post
        while True:
            current_post_link = (
                current_post.find_element(By.XPATH, ".//time")
                .find_element(By.XPATH, "..")
                .get_attribute("href")
            )
            logger.debug(f"Current post link: {current_post_link}")

            next_post_link = get_next_post_link(current_post)
            if next_post_link is None:
                logger.error("No more posts found. Exiting...")
                status = ProgramStatus.NO_MORE_POSTS_FOUND
                break
            username, username_element = get_user.get_user_name(driver, current_post)
            if username is None or username_element is None:
                logger.error("No username found. Exiting...")
                status = ProgramStatus.NO_USERNAME
                break
            if username in good_user:
                user_status = FollowerStatus.FOLLOWING
            elif username in bad_user:
                user_status = FollowerStatus.NOT_FOLLOWING
            else:
                user_status = check_user.get_user_status(
                    driver, action, username, username_element
                )
                if user_status is None:
                    logger.error("No user status found. Exiting...")
                    status = ProgramStatus.NO_USER_STATUS
                    break
                apply_action.apply_action(
                    driver,
                    action,
                    username,
                    username_element,
                    user_status,
                    good_user,
                    bad_user,
                )
            overall_post += 1
            if overall_post >= config_value["MAX_POSTS"]:
                logger.info("Reached maximum number of posts. Exiting...")
                status = ProgramStatus.MAX_POSTS
                break
            total_post += 1
            if total_post >= config_value["MAX_POSTS_PER_RELOAD"]:
                logger.info(
                    "Reached maximum number of posts per run. Reload the page..."
                )
                status = ProgramStatus.MAX_POSTS_PER_RUN
                driver.refresh()
                break
            if good_user_streak >= config_value["MAX_GOOD_USER_STREAK"]:
                logger.info("Reached maximum good user streak. Exiting...")
                status = ProgramStatus.MAX_GOOD_USER_STREAK
                break
            elif user_status in (
                FollowerStatus.FOLLOWING,
                FollowerStatus.FOLLOWING_BY_NETWORK,
            ):
                good_user_streak += 1
            else:
                good_user_streak = 0
            current_post = set_next_post(driver, next_post_link)
            if current_post is None:
                logger.error("No next post found. Exiting...")
                status = ProgramStatus.NO_MORE_POSTS_FOUND
                break
            logger.debug("-" * 30)
        match status:
            case ProgramStatus.MAX_POSTS:
                break
            case ProgramStatus.MAX_POSTS_PER_RUN:
                continue
            case ProgramStatus.MAX_GOOD_USER_STREAK:
                break
            case ProgramStatus.NO_MORE_POSTS_FOUND:
                break
            case ProgramStatus.NO_USERNAME:
                break
            case ProgramStatus.NO_USER_STATUS:
                break


if __name__ == "__main__":
    main()
