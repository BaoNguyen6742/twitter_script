from pathlib import Path

import yaml
from yaml import load

config_file = Path("src/twitter_block/config/config.yaml")

with open(config_file, "r") as file:
    config_value = load(file, Loader=yaml.FullLoader)
