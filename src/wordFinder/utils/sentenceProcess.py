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
