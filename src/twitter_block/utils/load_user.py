import logging
import os
from pathlib import Path


def load_good_users(clear=False):
    """
    Load the list of good users from a file. If the file does not exist, create it.
    
    Behavior
    --------
    - If `clear` is True, the file will be deleted and recreated.
    - If the file does not exist, it will be created as an empty file.
    - If the file exists, it will be read and the usernames will be stored in a set.
    
    
    Parameters
    ----------
    - clear : `bool`. Optional, by default False \\
        Whether to clear the existing user list before loading.
    
    Returns
    -------
    - good_user : `set`
        A set containing the usernames of good users.
    """
    logger = logging.getLogger("A_LOG")
    good_user_path = "src/twitter_block/config/good_user.txt"
    if clear:
        Path(good_user_path).unlink(missing_ok=True)
        logger.info("Good user list cleared")
    if not os.path.exists(good_user_path):
        with open(good_user_path, "w") as f:
            pass  # Create empty file
        good_user = set()
    else:
        with open(good_user_path, "r") as f:
            f.seek(0)
            good_user = {line.strip() for line in f if line.strip()}
    good_count = len(good_user)
    logger.info(f"Good user list loaded with {good_count} users")
    return good_user


def load_bad_users(clear=False):
    """
    Load the list of bad users from a file. If the file does not exist, create it.

    Behavior
    --------
    - If `clear` is True, the file will be deleted and recreated.
    - If the file does not exist, it will be created as an empty file.
    - If the file exists, it will be read and the usernames will be stored in a set.


    Parameters
    ----------
    - clear : `bool`. Optional, by default False
        Whether to clear the existing user list before loading.

    Returns
    -------
    - bad_user : `set`
        A set containing the usernames of bad users.
    """
    logger = logging.getLogger("A_LOG")
    bad_user_path = "src/twitter_block/config/bad_user.txt"
    if clear:
        Path(bad_user_path).unlink(missing_ok=True)
        logger.info("Bad user list cleared")
    if not os.path.exists(bad_user_path):
        with open(bad_user_path, "w") as f:
            pass  # Create empty file
        bad_user = set()
    else:
        with open(bad_user_path, "r") as f:
            f.seek(0)
            bad_user = {line.strip() for line in f if line.strip()}
    bad_count = len(bad_user)
    logger.info(f"Bad user list loaded with {bad_count} users")
    return bad_user


def add_user_to_file(file, username):
    """
    Add a username to the specified user file.

    Behavior
    --------
    Appends the username to the file designated for the user type.

    Parameters
    ----------
    - file : `str`
        The type of user file (good or bad).
    - username : `str`
        The username to be added to the file.
    """
    with open(f"./src/twitter_block/config/{file}_user.txt", "a") as f:
        f.write(f"{username}\n")
