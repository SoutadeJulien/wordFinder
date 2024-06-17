import re

from wordFinder import constants


def isLineValid(line: str) -> bool:
    """Checks if the provided word or sentence contains an excluded character.

    This method is used to get if the tool can output a line that contains a comment or a docstring.

    Parameters:
        line: The line to check.

    Returns:
        True if the :param:`line` does not contain any excluded characters, else, False.
    """
    for char in constants.EXCLUDED_CHARACTERS:
        if char in line:
            return False
    return True


def wordInLine(word: str, line: str, isLitteral) -> bool:
        """Gets if the provided line contains the provided word.

        There is two way to search the word, with a simple check or with a regex.

        Parameters:
            word: The word to search.
            line: The line that is used to search for the word.

        Returns:
            True if the line contains the word, else False.
        """
        if isLitteral:
            if word in line:
                return True

        else:
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, line):
                return True

        return False