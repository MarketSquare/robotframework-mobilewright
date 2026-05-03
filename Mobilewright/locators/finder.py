import re
from typing import List

from ..rpc.protocol import MobileWrightElementNotFoundError, ViewNode
from .types import LocatorStrategy, ParsedLocator


def find_elements(tree: List[ViewNode], locators: List[ParsedLocator]) -> List[ViewNode]:
    nodes = tree
    for locator in locators:
        matched = []
        for node in _flatten(nodes):
            if _matches(node, locator):
                matched.append(node)
        nodes = matched
    return nodes


def find_element(
    tree: List[ViewNode],
    locators: List[ParsedLocator],
    index: str = 'first',
) -> ViewNode:
    matches = find_elements(tree, locators)
    if not matches:
        locator_str = ' >> '.join(str(loc) for loc in locators)
        raise MobileWrightElementNotFoundError(
            f"No element found matching: {locator_str}"
        )
    idx = _resolve_index(index, len(matches))
    return matches[idx]


def _resolve_index(index, count: int) -> int:
    if isinstance(index, str):
        index = index.strip().lower()
        if index == 'first':
            return 0
        if index == 'last':
            return count - 1
        index = int(index)
    if index < 0:
        index = count + index
    if index < 0 or index >= count:
        raise MobileWrightElementNotFoundError(
            f"Index {index} out of range, found {count} element(s)"
        )
    return index


def _flatten(nodes: List[ViewNode]) -> List[ViewNode]:
    result = []
    for node in nodes:
        result.append(node)
        result.extend(_flatten(node.children))
    return result


def _matches(node: ViewNode, locator: ParsedLocator) -> bool:
    strategy = locator.strategy
    value = locator.value

    if strategy == LocatorStrategy.LABEL:
        return _match_string(node.label, value)
    elif strategy == LocatorStrategy.TESTID:
        return _match_string(node.test_id, value)
    elif strategy == LocatorStrategy.TEXT:
        return _match_string(node.text, value)
    elif strategy == LocatorStrategy.TYPE:
        return _match_string(node.type, value)
    elif strategy == LocatorStrategy.ROLE:
        if not _match_string(node.role, value):
            return False
        if locator.role_name and not _match_string(node.label, locator.role_name):
            return False
        return True
    elif strategy == LocatorStrategy.PLACEHOLDER:
        return _match_string(node.placeholder, value)
    return False


def _match_string(actual: str, expected) -> bool:
    if not actual and not expected:
        return True
    if not actual:
        return False
    if isinstance(expected, re.Pattern):
        return bool(expected.search(actual))
    return actual == expected
