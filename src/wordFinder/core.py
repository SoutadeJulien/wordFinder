import os
import json
from typing import Optional, Mapping, Union
import re

import constants
from utils import syntaxColors


CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils/config.json')


def makeDefaultConfig() -> None:
    """Create a default config.json."""
    with open(CONFIG_PATH, 'w') as writeFile:
        json.dump(constants.DEFAULT_CONFIG, writeFile, indent=4)


def storeConfig(configName: str, value: Optional[str]) -> None:
    """Dumps the provided configName and value within the config.json.

    Parameters:
        configName: The key to set in the config.json.
        value: The value to set in the config.json.
    """
    with open(CONFIG_PATH, 'r') as readFile:
        config = json.load(readFile)
        config[configName] = value

    with open(CONFIG_PATH, 'w') as writeFile:
        json.dump(config, writeFile, indent=4)


def getConfig() -> Union[Mapping[str, Union[str, int]], None]:
    """Get the config.json.

    Returns:
        The config.json if is found, else None.
    """
    try:
        with open(CONFIG_PATH, 'r') as readFile:
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
    with open(CONFIG_PATH, 'r') as readFile:
        config = json.load(readFile)
        return config.get(configName, None)


def colorizeLine(line: str, wordToSearch: str) -> str:
    """Colorizes the provided line depending on the targets words from the syntaxColors module.

    Parameters:
        line: The line where to search the word.
        wordToSearch: the word to search in the :param:`line`.

    Returns:
        A colored line in HTML format.
    """
    coloredLine = line

    for word in syntaxColors.regexTargetedWords:
        matches = re.search(word.regex, coloredLine)

        if matches:
            if matches.group(word.matchingGroup) != '':
                coloredLine = coloredLine.replace(matches.group(word.matchingGroup), f"<font color={word.color}>{matches.group(word.matchingGroup)}</font>")

    for word, color in syntaxColors.targetedWords.items():
        if word in line:
            coloredLine = coloredLine.replace(word, f"<font color={color}>{word}</font>")

    if wordToSearch in coloredLine:
        coloredLine = coloredLine.replace(wordToSearch, f"""<font color={"#5ffa16"}>{wordToSearch}</font>""")

    return coloredLine
