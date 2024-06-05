from dataclasses import dataclass


@dataclass(frozen=True)
class RegexWord:
    """This class allows to find a word in a line"""
    regex: str
    matchingGroup: str
    color: str


# Classic matching.
targetedWords = {
    "def": "#e35bba",
    "return": "#db8823",
    "pass": "#d6882f",
    "None": "#B97F39",
    "self": "#de31aa",
    "->": "#d6882f",
    "*args": "#db8823",
    "**kwargs": "#db8823",
}

# Regex matching.
regexTargetedWords = [
    RegexWord(r"(?:[(])(?P<arguments>[\w\[\]: ,*.]*)(?:[)])", 'arguments', "#f2a049"),
    RegexWord(r"\b(?P<Union>Union)\b", 'Union', "#fff566"),
    RegexWord(r"\b(?P<Callable>Callable)\b", 'Callable', "#fff566"),
    RegexWord(r"\b(?P<Mapping>Mapping)\b", 'Mapping', "#fff566"),
    RegexWord(r"\b(?P<str>str)\b", 'str', "#31aade"),
    RegexWord(r"\b(?P<int>int)\b", 'int', "#31aade"),
    RegexWord(r"\b(?P<float>float)\b", 'float', "#31aade"),
    RegexWord(r"\b(?P<list>list)\b", 'list', "#31aade"),
    RegexWord(r"\b(?P<List>List)\b", 'List', "#fff566"),
    RegexWord(r"\b(?P<tuple>tuple)\b", 'tuple', "#31aade"),
    RegexWord(r"\b(?P<Tuple>Tuple)\b", 'Tuple', "#fff566"),
]
