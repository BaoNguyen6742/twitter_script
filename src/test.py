from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from twitter_block.browser.init_browser import initialize_twitter_browser
from twitter_block.config import config_value
from twitter_block.users.check_user import check_is_good_user
from twitter_block.users.get_user import get_user_name
from twitter_block.utils.follower_status import FollowerStatus
from twitter_block.utils.human_timing import human_delay
from twitter_block.utils.init_logger import logger
from twitter_block.utils.load_user import (
    add_user_to_file,
    load_bad_users,
    load_good_users,
)


def main():
    good_user = load_good_users()
    bad_user = load_bad_users()

    driver = initialize_twitter_browser()
    action = webdriver.ActionChains(driver)
    goal_reached = False
    force_refresh = False
    while True:
        if not force_refresh:
            total_post = 0
            good_user_streak = 0
            num_batch = 0
        last_post_idx = 0

        while total_post < config_value["MAX_POSTS"]:
            posts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//article[@data-testid='tweet']")
                )
            )
            # List number of posts
            if len(posts) < last_post_idx + 1:
                logger.info("Less posts than before")
                force_refresh = True
                break
            print()
            logger.debug(f"Number of posts: {len(posts)}")
            logger.debug(f"Post idx {last_post_idx}")
            investigate_posts = posts[last_post_idx:] if last_post_idx > 0 else posts
            logger.info(f"Number of new posts: {len(investigate_posts)}")
            for post_idx, post in enumerate(investigate_posts):
                print("\n")
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        post,
                    )
                except Exception as e:
                    logger.error(f"Error scrolling to post: {e}")
                    continue
                logger.info(
                    f"{f"Processing post {total_post+1}/{config_value["MAX_POSTS"]}":-^50}"
                )
                logger.info(f"{f"Batch {num_batch+1}":-^50}")
                logger.info(
                    f"{f"Processing batch {post_idx+1}/{len(investigate_posts)}":-^50}"
                )
                logger.debug("Scroll to post")

                username, username_element = get_user_name(driver, post)
                if username in good_user:
                    logger.info(f"User @{username} already in good user list")
                    good_user_streak += 1
                    total_post += 1
                    continue
                if username in bad_user:
                    logger.info(f"User @{username} already in bad user list")
                    good_user_streak = 0
                    total_post += 1
                    continue
                if username is None:
                    logger.error("Username not found")
                    print("Username not found")
                    total_post += 1
                    continue

                user_status = check_is_good_user(
                    driver, action, username, username_element
                )
                match user_status:
                    case FollowerStatus.FOLLOWING:
                        good_user.add(username)
                        add_user_to_file("good", username)
                        good_user_streak += 1
                        logger.info(f"User @{username} added to good user list")
                    case FollowerStatus.FOLLOWING_BY_NETWORK:
                        good_user.add(username)
                        add_user_to_file("good", username)
                        good_user_streak += 1
                        logger.info(f"User @{username} added to good user list")
                    case FollowerStatus.NOT_FOLLOWING:
                        bad_user.add(username)
                        add_user_to_file("bad", username)
                        good_user_streak = 0
                        logger.info(f"User @{username} added to bad user list")
                        pass
                    case FollowerStatus.ERROR:
                        print("Error in checking follow status")
                        logger.error("Error in checking follow status")
                if good_user_streak >= config_value["MAX_GOOD_USER_STREAK"]:
                    logger.info("Good user streak reached")
                    goal_reached = True
                    break
                total_post += 1
            if goal_reached:
                break
            last_post_idx = total_post
            num_batch += 1
            human_delay(verbose=config_value["VERBOSE"])
            logger.debug(f"Good user streak: {good_user_streak}")

        if goal_reached:
            break
        logger.info("Refreshing the page to load more posts")
        driver.refresh()

    logger.info("All posts processed")

    input("Press Enter to close the browser...")
    print(f"{good_user=}")


if __name__ == "__main__":
    main()
