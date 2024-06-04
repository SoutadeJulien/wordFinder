import os
import json
from typing import Optional, Mapping, Union

import constants


def makeDefaultConfig():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json'), 'w') as writeFile:
        json.dump(constants.DEFAULT_CONFIG, writeFile, indent=4)


def searchPath() -> Optional[str]:
    """Gets the __search_path__ value from the config.json.

    Returns:
        The actual search path.
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json'), 'r') as readFile:
        settings = json.load(readFile)
        return settings.get('__search_path__', None)


def addSearchPath(path: str) -> None:
    """Dumps the provided path to the config.json.

    Parameters:
        path: The path to dump.
    """
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'r') as readFile:
        settings = json.load(readFile)

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json'), 'w') as writeFile:
        settings['__search_path__'] = path
        json.dump(settings, writeFile, indent=4)


def storeConfig(configName, value):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json'), 'r') as readFile:
        config = json.load(readFile)
        config[configName] = value

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json'), 'w') as writeFile:
        json.dump(config, writeFile, indent=4)


def getConfig() -> Optional[Mapping[str, Union[str, int]]]:
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json'), 'r') as readFile:
            return json.load(readFile)

    except FileNotFoundError:
        return None
