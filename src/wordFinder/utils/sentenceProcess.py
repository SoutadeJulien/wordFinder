import re

from wordFinder.utils import syntaxColors


def wordInLine(word: str, line: str, isLiteral: bool) -> bool:
        """Gets if the provided line contains the provided word.

        There is two ways to search the word, with a simple check or with a regex.

        Parameters:
            isLiteral: If true, the method will search if the provided word is in the sentence, if false, the method will search the word using a regex.
            word: The word to search.
            line: The line that is used to search for the word.

        Returns:
            True if the line contains the word, else False.
        """
        if isLiteral:
            if word in line:
                return True

        else:
            pattern = r"\b" + re.escape(word) + r"\b"

            if re.search(pattern, line):
                return True

        return False


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
