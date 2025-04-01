import time
import configparser
import random
from datetime import datetime
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pickle

# webdriver.


def save_cookie(driver, path):
    with open(path, "wb") as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookie(driver, path):
    with open(path, "rb") as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)


def human_delay(min_seconds=1.0, max_seconds=3.0):
    """Add a random delay to simulate human behavior"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay


def slow_type(element, text, delay_range=(0.05, 0.15)):
    """Type text into an element with human-like delays between keystrokes"""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(*delay_range))


def login_to_twitter(driver, username, password):
    print("Opening Twitter login page...")
    driver.get("https://twitter.com")
    human_delay(2.0, 4.0)

    try:
        # Wait for the username field
        # print("Waiting for username field...")
        # username_field = WebDriverWait(driver, 20).until(
        #     EC.visibility_of_element_located(
        #         (By.XPATH, "//input[@autocomplete='username']")
        #     )
        # )

        # print(f"Typing username: {username}")
        # slow_type(username_field, username)
        # human_delay(1.0, 2.0)

        # # Click Next
        # print("Clicking Next...")
        # next_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
        # )
        # next_button.click()
        # human_delay(2.0, 3.5)

        # # Enter password
        # print("Entering password...")
        # password_field = WebDriverWait(driver, 10).until(
        #     EC.visibility_of_element_located(
        #         (By.XPATH, "//input[@autocomplete='current-password']")
        #     )
        # )
        # slow_type(password_field, password)
        # human_delay(1.5, 2.5)

        # # Log in
        # print("Clicking Log in...")
        # login_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        # )
        # login_button.click()

        # Wait for home page with longer timeout
        print("Waiting for home timeline to load...")
        WebDriverWait(driver, 40).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Home timeline']")
            )
        )

        human_delay(3.0, 5.0)
        print("Successfully logged in!")
        return True

    except Exception as e:
        print(f"Login error: {e}")
        return False


def switch_to_for_you_feed(driver):
    try:
        human_delay(3.0, 5.0)

        # Check if already on "For you" tab
        try:
            driver.find_element(
                By.XPATH,
                "//div[@role='tablist']/div[@aria-selected='true']//span[contains(text(), 'For you')]",
            )
            print("Already on For You feed")
            return True
        except NoSuchElementException:
            pass

        # Click "For you" tab
        print("Looking for For You tab...")
        for_you_tab = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@role='tablist']//span[contains(text(), 'For you')]")
            )
        )

        print("Clicking For You tab...")
        for_you_tab.click()
        human_delay(3.0, 5.0)
        print("Switched to For You feed")
        return True
    except Exception as e:
        print(f"Error switching to For You feed: {e}")
        return False


def check_if_followed_by_network(driver, post_element):
    """Check if the post author is followed by people you follow"""
    try:
        # Find the username element
        username_element = post_element.find_element(
            By.XPATH, ".//div[@data-testid='User-Name']//a"
        )
        href = username_element.get_attribute("href")
        username = href.split("/")[-1]

        print(f"Checking if @{username} is followed by your network...")

        # Slowly move mouse to hover over the profile
        actions = ActionChains(driver)
        actions.move_to_element(username_element).perform()
        human_delay(2.5, 4.0)  # Wait longer for hover card to appear

        # Look for "Followed by..." text in the hover card
        try:
            print("Looking for hover card info...")
            hover_card = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-testid='HoverCard']")
                )
            )
            if hover_card:
                print("Hover card found")
            xpath = r"//div[contains(text(),'Followed by')] | //span[contains(text(),'Follows you')]"
            followed_by_text = hover_card.find_elements(By.XPATH, xpath)

            if followed_by_text:
                print(
                    f"@{username} is followed by people in your network (from hover card)"
                )
                human_delay(1.0, 2.0)
                return True

            # Alternative: Click on profile and check the "Followed by" information
            if not followed_by_text:
                print(
                    f"No follow info in hover card. Checking @{username}'s profile..."
                )
                human_delay(1.0, 2.0)

                # Click on username to open profile
                username_element.click()
                human_delay(4.0, 6.0)  # Wait longer for profile to load

                # Look for "Followed by" text on the profile page
                print("Looking for follow information on profile...")
                followed_by_on_profile = driver.find_elements(
                    By.XPATH,
                    xpath,
                )

                result = len(followed_by_on_profile) > 0
                if result:
                    print(
                        f"@{username} is followed by people in your network (from profile)"
                    )
                else:
                    print(f"@{username} is NOT followed by people in your network")

                # Go back to feed
                print("Going back to feed...")
                driver.back()
                human_delay(3.0, 5.0)

                return result

        except TimeoutException:
            print("Hover card didn't appear or couldn't find follow information")
            # Try profile approach instead
            print(f"Checking @{username}'s profile directly...")
            driver.get(f"https://twitter.com/{username}")
            human_delay(4.0, 6.0)

            followed_by_on_profile = driver.find_elements(
                By.XPATH,
                "//span[contains(text(), 'Followed by') or contains(text(), 'follows you')]",
            )

            result = len(followed_by_on_profile) > 0
            if result:
                print(
                    f"@{username} is followed by people in your network (from profile visit)"
                )
            else:
                print(f"@{username} is NOT followed by people in your network")

            # Go back to feed
            print("Going back to feed...")
            driver.get("https://twitter.com/home")
            human_delay(3.0, 5.0)
            switch_to_for_you_feed(driver)

            return result

        return False
    except Exception as e:
        print(f"Error checking if @{username} is followed by network: {e}")
        return False


def check_if_is_following(driver, post_element):
    """Check if the post author is followed by you"""
    try:
        # Find the username element
        username_element = post_element.find_element(
            By.XPATH, ".//div[@data-testid='User-Name']//a"
        )
        href = username_element.get_attribute("href")
        username = href.split("/")[-1]

        print(f"Checking if @{username} is followed by you...")

        # Slowly move mouse to hover over the profile
        actions = ActionChains(driver)
        actions.move_to_element(username_element).perform()
        human_delay(2.5, 4.0)  # Wait longer for hover card to appear

        # Look for "Followed by..." text in the hover card
        try:
            print("Looking for hover card info...")
            hover_card = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@data-testid='HoverCard']")
                )
            )
            if hover_card:
                print("Hover card found")
            else:
                print("Hover card not found")
            xpath = r".//span[contains(text(),'Following')]"
            followed_by_text = hover_card.find_elements(By.XPATH, xpath)
            print(followed_by_text[0].text)
            html = driver.execute_script(
                "return arguments[0].innerHTML;", followed_by_text[0]
            )
            print(html)

            input("Press Enter to continue...")
            if followed_by_text:
                print(f"@{username} is followed by you (from hover card)")
                human_delay(1.0, 2.0)
                return True
            else:
                print(f"@{username} is NOT followed by you (from hover card)")
                human_delay(1.0, 2.0)
                return False
        except TimeoutException:
            print("Hover card didn't appear or couldn't find follow information")
            # Try profile approach instead
            print(f"Checking @{username}'s profile directly...")
            driver.get(f"https://twitter.com/{username}")
            human_delay(4.0, 6.0)

            followed_by_on_profile = driver.find_elements(
                By.XPATH,
                ".//span[contains(text(), 'Following')]",
            )

            result = len(followed_by_on_profile) > 0
            if result:
                print(f"@{username} is followed by you (from profile visit)")
            else:
                print(f"@{username} is NOT followed by you")

            return result
    except Exception as e:
        print(f"Error checking if @{username} is followed by you: {e}")
        return False


def check_retweet_author(driver, post_element):
    """Check if a post is a retweet and if the original author is followed by your network"""
    try:
        # Check if post is a retweet
        retweet_indicators = post_element.find_elements(
            By.XPATH, ".//span[contains(text(), 'Retweeted')]"
        )

        if not retweet_indicators:
            return None, False  # Not a retweet

        # Find original author
        try:
            print("Checking retweet information...")
            human_delay(1.0, 2.0)

            original_author_elements = post_element.find_elements(
                By.XPATH, ".//div[@data-testid='User-Name']//a"
            )
            if len(original_author_elements) > 1:
                original_author_element = original_author_elements[
                    1
                ]  # The second user is usually the original author
                original_author_href = original_author_element.get_attribute("href")
                original_author = original_author_href.split("/")[-1].lower()

                print(f"Post is a retweet of @{original_author}")

                # Check if original author is followed by network
                print(f"Checking if @{original_author} is followed by your network...")
                human_delay(1.0, 2.0)

                actions = ActionChains(driver)
                actions.move_to_element(original_author_element).perform()
                human_delay(2.5, 4.0)

                try:
                    hover_card = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//div[@data-testid='HoverCard']")
                        )
                    )
                    followed_by_text = hover_card.find_elements(
                        By.XPATH,
                        ".//span[contains(text(), 'Followed by') or contains(text(), 'follows you')]",
                    )

                    if followed_by_text:
                        print(
                            f"Retweeted author @{original_author} is followed by people in your network"
                        )
                        human_delay(1.0, 2.0)
                        return original_author, True

                    # Alternative: click and check
                    print(
                        f"No follow info in hover card. Checking @{original_author}'s profile..."
                    )
                    human_delay(1.0, 2.0)

                    original_author_element.click()
                    human_delay(4.0, 6.0)

                    followed_by_on_profile = driver.find_elements(
                        By.XPATH,
                        "//span[contains(text(), 'Followed by') or contains(text(), 'follows you')]",
                    )

                    result = len(followed_by_on_profile) > 0
                    if result:
                        print(
                            f"Retweeted author @{original_author} is followed by people in your network"
                        )
                    else:
                        print(
                            f"Retweeted author @{original_author} is NOT followed by people in your network"
                        )

                    # Go back to feed
                    print("Going back to feed...")
                    driver.back()
                    human_delay(3.0, 5.0)

                    return original_author, result

                except TimeoutException:
                    print("Hover card didn't appear for retweet author")
                    # Visit profile directly
                    driver.get(f"https://twitter.com/{original_author}")
                    human_delay(4.0, 6.0)

                    followed_by_on_profile = driver.find_elements(
                        By.XPATH,
                        "//span[contains(text(), 'Followed by') or contains(text(), 'follows you')]",
                    )

                    result = len(followed_by_on_profile) > 0
                    if result:
                        print(
                            f"Retweeted author @{original_author} is followed by people in your network"
                        )
                    else:
                        print(
                            f"Retweeted author @{original_author} is NOT followed by people in your network"
                        )

                    # Go back to feed
                    print("Going back to feed...")
                    driver.get("https://twitter.com/home")
                    human_delay(3.0, 5.0)
                    switch_to_for_you_feed(driver)

                    return original_author, result
        except Exception as e:
            print(f"Error checking retweet author details: {e}")
            return None, False

        return None, False
    except Exception as e:
        print(f"Error checking retweet author: {e}")
        return None, False


def mute_and_block_user(driver, username):
    try:
        print(f"Visiting @{username}'s profile to mute and block...")
        driver.get(f"https://twitter.com/{username}")
        human_delay(4.0, 6.0)

        # Click three dots menu
        print("Looking for user actions menu...")
        more_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='userActions']"))
        )

        print("Clicking user actions menu...")
        more_button.click()
        human_delay(2.0, 3.0)

        # Mute user
        try:
            print("Looking for mute option...")
            mute_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Mute')]")
                )
            )

            print(f"Muting @{username}...")
            mute_button.click()
            human_delay(2.0, 3.0)

            # Confirm if needed
            try:
                print("Looking for mute confirmation...")
                confirm_mute = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Mute']"))
                )

                print("Confirming mute...")
                confirm_mute.click()
                human_delay(2.0, 3.0)
            except:
                print("No mute confirmation needed")
                pass
            print(f"Successfully muted @{username}")
        except Exception as e:
            print(f"Could not mute @{username}: {e}")

        # Click three dots again
        print("Opening user actions menu again...")
        more_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='userActions']"))
        )
        more_button.click()
        human_delay(2.0, 3.0)

        # Block user
        try:
            print("Looking for block option...")
            block_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(), 'Block')]")
                )
            )

            print(f"Blocking @{username}...")
            block_button.click()
            human_delay(2.0, 3.0)

            # Confirm if needed
            try:
                print("Looking for block confirmation...")
                confirm_block = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Block']"))
                )

                print("Confirming block...")
                confirm_block.click()
                human_delay(2.0, 3.0)
            except:
                print("No block confirmation needed")
                pass
            print(f"Successfully blocked @{username}")
        except Exception as e:
            print(f"Could not block @{username}: {e}")

        human_delay(1.0, 2.0)
        return True

    except Exception as e:
        print(f"Error muting and blocking @{username}: {e}")
        return False


def process_feed(driver, max_duration=None):
    start_time = time.time()

    # Try to load existing safe accounts
    safe_accounts = set()
    blocked_accounts = set()

    try:
        with open("twitter_safe_accounts.txt", "r") as f:
            for line in f:
                safe_accounts.add(line.strip().lower())
        print(f"Loaded {len(safe_accounts)} safe accounts from saved file")
    except:
        print("No saved safe accounts found. Starting fresh.")

    try:
        with open("twitter_blocked_accounts.txt", "r") as f:
            for line in f:
                blocked_accounts.add(line.strip().lower())
        print(f"Loaded {len(blocked_accounts)} blocked accounts from saved file")
    except:
        print("No saved blocked accounts found. Starting fresh.")

    # Save account lists to file
    def save_accounts():
        with open("twitter_safe_accounts.txt", "w") as f:
            for username in sorted(safe_accounts):
                f.write(f"{username}\n")

        with open("twitter_blocked_accounts.txt", "w") as f:
            for username in sorted(blocked_accounts):
                f.write(f"{username}\n")

        print(
            f"Saved {len(safe_accounts)} safe accounts and {len(blocked_accounts)} blocked accounts"
        )

    # Go to feed
    print("Navigating to Twitter home...")
    driver.get("https://twitter.com/home")
    human_delay(3.0, 5.0)
    switch_to_for_you_feed(driver)

    posts_processed = 0
    clean_posts_count = 0
    muted_blocked_total = 0
    last_refresh_time = time.time()

    # Create log file
    log_filename = (
        f"twitter_cleaning_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    with open(log_filename, "w") as log_file:
        log_file.write(f"Twitter cleaning started at {datetime.now()}\n")

        while True:
            # Check time limit
            current_runtime = time.time() - start_time
            if max_duration and (current_runtime > max_duration):
                log_message = f"Reached maximum duration of {max_duration} seconds ({current_runtime/60:.1f} minutes). Stopping."
                print(log_message)
                log_file.write(f"{log_message}\n")
                break

            # Get posts
            try:
                print("Waiting for tweets to load...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//article[@data-testid='tweet']")
                    )
                )
                posts = driver.find_elements(
                    By.XPATH, "//article[@data-testid='tweet']"
                )
                print(f"Found {len(posts)} tweets in the feed")
            except:
                print("No posts found. Refreshing...")
                driver.refresh()
                human_delay(5.0, 8.0)
                switch_to_for_you_feed(driver)
                continue

            if not posts:
                print("No posts found. Refreshing...")
                driver.refresh()
                human_delay(5.0, 8.0)
                switch_to_for_you_feed(driver)
                continue

            muted_blocked_count = 0
            current_batch_size = min(len(posts), 100)

            for post_index, post in enumerate(posts[:current_batch_size]):
                try:
                    posts_processed += 1

                    print(
                        f"\n--- Processing Post #{posts_processed} ({post_index+1}/{current_batch_size}) ---"
                    )
                    human_delay(1.0, 2.0)

                    # Get post author
                    try:
                        username_element = post.find_element(
                            By.XPATH, ".//div[@data-testid='User-Name']//a"
                        )
                        href = username_element.get_attribute("href")
                        username = href.split("/")[-1].lower()
                        print(f"Post author: @{username}")
                    except:
                        print("Couldn't determine post author, skipping")
                        continue

                    # Skip if already known safe
                    if username in safe_accounts:
                        print(f"@{username} is already known to be safe")

                        # Count toward clean posts
                        if post_index < 15:
                            clean_posts_count += 1
                            print(f"Clean posts count: {clean_posts_count}/15")

                        human_delay(0.5, 1.5)
                        continue

                    # Skip if already blocked
                    if username in blocked_accounts:
                        print(f"@{username} was previously blocked but appears in feed")
                        human_delay(0.5, 1.5)
                        continue

                    # Check if author is followed by people you follow
                    is_follwing = check_if_is_following(driver, post)
                    if is_follwing:
                        print(f"@{username} is followed by you - keeping")
                        safe_accounts.add(username)

                        # Count toward clean posts
                        if post_index < 15:
                            clean_posts_count += 1
                            print(f"Clean posts count: {clean_posts_count}/15")
                        human_delay(0.5, 1.5)
                        continue
                    is_followed_by_network = check_if_followed_by_network(driver, post)

                    if is_followed_by_network:
                        print(f"@{username} is followed by people you follow - keeping")
                        safe_accounts.add(username)

                        # Count toward clean posts
                        if post_index < 15:
                            clean_posts_count += 1
                            print(f"Clean posts count: {clean_posts_count}/15")
                    else:
                        print(
                            f"@{username} is not followed by your network - muting and blocking"
                        )
                        clean_posts_count = 0  # Reset clean posts count

                        if mute_and_block_user(driver, username):
                            muted_blocked_count += 1
                            muted_blocked_total += 1
                            blocked_accounts.add(username)

                            # Save progress
                            save_accounts()

                        # Return to feed
                        print("Returning to feed...")
                        driver.get("https://twitter.com/home")
                        human_delay(4.0, 6.0)
                        switch_to_for_you_feed(driver)

                        # Get posts again
                        try:
                            print("Waiting for tweets to reload...")
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//article[@data-testid='tweet']")
                                )
                            )
                            posts = driver.find_elements(
                                By.XPATH, "//article[@data-testid='tweet']"
                            )
                            if not posts:
                                print("No posts found after returning to feed")
                                break
                        except:
                            print("Couldn't find posts after returning to feed")
                            break

                    # Take a small breather before checking retweets
                    human_delay(1.0, 2.0)

                    # Check for retweets
                    retweeted_username, is_retweeted_followed = check_retweet_author(
                        driver, post
                    )

                    if (
                        retweeted_username
                        and retweeted_username not in safe_accounts
                        and retweeted_username not in blocked_accounts
                    ):
                        if is_retweeted_followed:
                            print(
                                f"Retweeted author @{retweeted_username} is followed by your network - keeping"
                            )
                            safe_accounts.add(retweeted_username)
                        else:
                            print(
                                f"Retweeted author @{retweeted_username} is not followed by your network - muting and blocking"
                            )
                            clean_posts_count = 0  # Reset clean posts count

                            if mute_and_block_user(driver, retweeted_username):
                                muted_blocked_count += 1
                                muted_blocked_total += 1
                                blocked_accounts.add(retweeted_username)

                                # Save progress
                                save_accounts()

                            # Return to feed
                            print("Returning to feed...")
                            driver.get("https://twitter.com/home")
                            human_delay(4.0, 6.0)
                            switch_to_for_you_feed(driver)

                            # Get posts again
                            try:
                                print("Waiting for tweets to reload...")
                                WebDriverWait(driver, 20).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH, "//article[@data-testid='tweet']")
                                    )
                                )
                                posts = driver.find_elements(
                                    By.XPATH, "//article[@data-testid='tweet']"
                                )
                                if not posts:
                                    print("No posts found after returning to feed")
                                    break
                            except:
                                print("Couldn't find posts after returning to feed")
                                break

                    # Check for 15 clean posts
                    if clean_posts_count >= 15:
                        print("\n🎉 First 15 posts are clean. Mission accomplished! 🎉")
                        log_file.write(
                            "First 15 posts are clean. Mission accomplished!\n"
                        )
                        save_accounts()
                        return

                    # Take a breather between posts
                    human_delay(2.0, 4.0)

                except Exception as e:
                    print(f"Error processing post {posts_processed}: {e}")
                    continue

            elapsed_mins = (time.time() - start_time) / 60
            status_msg = f"Processed {posts_processed} posts total, muted and blocked {muted_blocked_total} users total. Running for {elapsed_mins:.1f} minutes."
            print(f"\n--- {status_msg} ---\n")
            log_file.write(f"{status_msg}\n")

            # Save progress
            save_accounts()

            # Take a longer break every now and then
            if posts_processed % 10 == 0:
                print("Taking a short break to appear more human-like...")
                human_delay(5.0, 10.0)

            # Refresh every 100 posts or 5 minutes
            if (posts_processed % 100 == 0) or (time.time() - last_refresh_time > 300):
                print("Refreshing feed...")
                driver.refresh()
                human_delay(5.0, 8.0)
                switch_to_for_you_feed(driver)
                last_refresh_time = time.time()


def main():
    # Configuration
    config = configparser.ConfigParser()
    config.read("twitter_config.ini")

    username = config["Twitter"]["username"]
    password = config["Twitter"]["password"]
    max_duration = (
        int(config["Settings"]["max_duration"])
        if "max_duration" in config["Settings"]
        else None
    )

    if max_duration:
        print(f"Script will run for a maximum of {max_duration/60:.1f} minutes")

    # Browser setup
    # chrome_options = Options()
    # # chrome_options.add_argument("--headless")  # Uncomment to run without visible browser
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--disable-notifications")
    # # user_path = "/home/baonguyen/.config/google-chrome/Profile 2"
    # # chrome_options.add_argument(f"user-data-dir={user_path}")
    # chrome_options.add_argument("--profile-directory=Default")
    opt = uc.ChromeOptions()
    opt.binary_location = "/usr/bin/google-chrome"
    chromedriver_exe_location = "./chromedriver"
    profile_path = r"Profile 3"
    opt.add_argument(r"--user-data-dir=/home/baonguyen/.config/google-chrome")
    opt.add_argument("--profile-directory={}".format(profile_path))
    # opt.add_argument("--window-size={}".format("1920,1080"))
    opt.add_argument("--disable-notifications")
    service = Service(executable_path=chromedriver_exe_location)
    print("Starting Chrome browser...")
    print(f"{opt.arguments}")
    # input("Press Enter to continue...")
    driver = uc.Chrome(options=opt, service=service)
    # driver = webdriver.Chrome(options=chrome_options)
    # foo = input()

    # save_cookie(driver, "./tmp/cookie")
    # raise Exception("Stop here")

    try:
        if login_to_twitter(driver, username, password):
            process_feed(driver, max_duration)
        else:
            print("Failed to log in to Twitter.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        print("Closing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
