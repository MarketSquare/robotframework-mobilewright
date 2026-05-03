import re
from typing import List

from .types import LocatorStrategy, ParsedLocator

CHAIN_SEPARATOR = ' >> '

STRATEGY_MAP = {
    'label': LocatorStrategy.LABEL,
    'testid': LocatorStrategy.TESTID,
    'text': LocatorStrategy.TEXT,
    'type': LocatorStrategy.TYPE,
    'role': LocatorStrategy.ROLE,
    'placeholder': LocatorStrategy.PLACEHOLDER,
}

_REGEX_PATTERN = re.compile(r'^/(.+)/([gimsux]*)$')


def parse_locator(locator_string: str) -> List[ParsedLocator]:
    parts = locator_string.split(CHAIN_SEPARATOR)
    return [_parse_single(part.strip()) for part in parts]


def _parse_single(locator: str) -> ParsedLocator:
    sep_index = locator.find('=')

    if sep_index == -1:
        return ParsedLocator(strategy=LocatorStrategy.TEXT, value=locator)

    prefix = locator[:sep_index].strip().lower()
    value_str = locator[sep_index + 1:].strip()

    strategy = STRATEGY_MAP.get(prefix)
    if strategy is None:
        return ParsedLocator(strategy=LocatorStrategy.TEXT, value=locator)

    value = _parse_value(value_str)

    role_name = None
    if strategy == LocatorStrategy.ROLE and '[' in value_str:
        role_part, bracket_part = value_str.split('[', 1)
        value = role_part.strip()
        if bracket_part.startswith('name=') and bracket_part.endswith(']'):
            role_name = bracket_part[5:-1].strip()

    return ParsedLocator(strategy=strategy, value=value, role_name=role_name)


def _parse_value(value_str: str):
    match = _REGEX_PATTERN.match(value_str)
    if match:
        pattern, flags_str = match.groups()
        flags = 0
        if 'i' in flags_str:
            flags |= re.IGNORECASE
        if 'm' in flags_str:
            flags |= re.MULTILINE
        if 's' in flags_str:
            flags |= re.DOTALL
        return re.compile(pattern, flags)
    return value_str
