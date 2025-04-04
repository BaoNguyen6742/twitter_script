import os
from pathlib import Path

import yaml
from yaml import load

config_file = Path("src/twitter_block/config/config.yaml")

with open(config_file, "r") as file:
    config_value = load(file, Loader=yaml.FullLoader)

if os.name == "nt":
    config_value["chrome_location"] = (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    )
elif os.name == "posix":
    config_value["chrome_location"] = "/usr/bin/google-chrome"
