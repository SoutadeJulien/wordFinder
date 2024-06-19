from dataclasses import dataclass


@dataclass(frozen=True)
class Matching:
    """The purpose of this class is to keep a regex pattern, its matching group, and the associated color together in one place."""
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
    Matching(r"(?:[(])(?P<arguments>[\w\[\]: ,*.']*)(?:[)])", 'arguments', "#f2a049"),
    Matching(r"\b(?P<Union>Union)\b", 'Union', "#fff566"),
    Matching(r"\b(?P<Callable>Callable)\b", 'Callable', "#fff566"),
    Matching(r"\b(?P<Mapping>Mapping)\b", 'Mapping', "#fff566"),
    Matching(r"\b(?P<str>str)\b", 'str', "#31aade"),
    Matching(r"\b(?P<int>int)\b", 'int', "#31aade"),
    Matching(r"\b(?P<float>float)\b", 'float', "#31aade"),
    Matching(r"\b(?P<list>list)\b", 'list', "#31aade"),
    Matching(r"\b(?P<List>List)\b", 'List', "#fff566"),
    Matching(r"\b(?P<tuple>tuple)\b", 'tuple', "#31aade"),
    Matching(r"\b(?P<Tuple>Tuple)\b", 'Tuple', "#fff566"),
]
