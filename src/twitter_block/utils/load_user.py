import os

from .init_logger import logger


def load_good_users():
    if not os.path.exists("src/twitter_block/config/good_user.txt"):
        with open("src/twitter_block/config/good_user.txt", "w") as f:
            pass  # Create empty file
        good_user = set()
    else:
        with open("src/twitter_block/config/good_user.txt", "r") as f:
            line_count = sum(1 for line in f)
            f.seek(0)
            good_user = {line.strip() for line in f if line.strip()}
    good_count = len(good_user)
    logger.info(f"Good user list loaded with {good_count} users")
    return good_user


def load_bad_users():
    if not os.path.exists("src/twitter_block/config/bad_user.txt"):
        with open("src/twitter_block/config/bad_user.txt", "w") as f:
            pass  # Create empty file
        bad_user = set()
    else:
        with open("src/twitter_block/config/bad_user.txt", "r") as f:
            line_count = sum(1 for line in f)
            f.seek(0)
            bad_user = {line.strip() for line in f if line.strip()}
    bad_count = len(bad_user)
    logger.info(f"bad user list loaded with {bad_count} users")
    return bad_user


def add_user_to_file(file, username):
    with open(f"{file}_user.txt", "a") as f:
        f.write(f"{username}\n")
