import sys
import json
from typing import Optional, Mapping, Union
import re

import constants
from utils import syntaxColors


def isPathAppended(moduleName) -> bool:
    """Check if the provided module is present in the PYTHONPATH"""
    for modulePath in sys.path:
        if modulePath == moduleName:
            return True
    return False


def makeDefaultConfig() -> None:
    """Creates a default config.json."""
    with open(constants.CONFIG_PATH, 'w') as writeFile:
        json.dump(constants.DEFAULT_CONFIG, writeFile, indent=4)


def storeConfig(configName: str, value: Optional[str]) -> None:
    """Dumps the provided configName and value within the config.json.

    Parameters:
        configName: The key to set in the config.json.
        value: The value to set in the config.json.
    """
    with open(constants.CONFIG_PATH, 'r') as readFile:
        config = json.load(readFile)
        config[configName] = value

    with open(constants.CONFIG_PATH, 'w') as writeFile:
        json.dump(config, writeFile, indent=4)


def getConfig() -> Union[Mapping[str, Union[str, int, bool]], None]:
    """Get the config.json.

    Returns:
        The config.json if is found, else None.
    """
    try:
        with open(constants.CONFIG_PATH, 'r') as readFile:
            return json.load(readFile)

    except FileNotFoundError:
        return None


def getConfigValueByName(configName: str) -> Union[str, None]:
    """Gets the configuration value from the provided key.

    Parameters:
        configName: The configuration key.

    Returns:
        The value of the provided key if it's present, else, None.
    """
    with open(constants.CONFIG_PATH, 'r') as readFile:
        config = json.load(readFile)
        return config.get(configName, None)



