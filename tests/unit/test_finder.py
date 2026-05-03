import pytest

from Mobilewright.locators.finder import find_element, find_elements
from Mobilewright.locators.types import LocatorStrategy, ParsedLocator
from Mobilewright.rpc.protocol import (
    BoundingBox,
    MobileWrightElementNotFoundError,
    ViewNode,
)


def _make_node(text='', label='', test_id='', type_='', role='',
               placeholder='', visible=True, enabled=True, children=None):
    return ViewNode(
        type=type_, text=text, label=label, test_id=test_id,
        role=role, placeholder=placeholder,
        bounds=BoundingBox(x=0, y=0, width=100, height=50),
        visible=visible, enabled=enabled,
        children=children or [],
    )


SAMPLE_TREE = [
    _make_node(type_='Screen', children=[
        _make_node(text='Header', label='header', type_='Text'),
        _make_node(type_='ListView', children=[
            _make_node(text='Item 1', test_id='item-1', type_='Cell'),
            _make_node(text='Item 2', test_id='item-2', type_='Cell'),
            _make_node(text='Item 3', test_id='item-3', type_='Cell', visible=False),
        ]),
        _make_node(
            type_='Button', text='Submit', label='Submit',
            role='button', enabled=True,
        ),
    ]),
]


class TestFindElements:

    def test_find_by_text(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TEXT, value='Item 1')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 1
        assert result[0].text == 'Item 1'

    def test_find_by_label(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.LABEL, value='header')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 1
        assert result[0].label == 'header'

    def test_find_by_testid(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TESTID, value='item-2')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 1
        assert result[0].test_id == 'item-2'

    def test_find_by_type(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TYPE, value='Cell')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 3

    def test_find_by_role(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.ROLE, value='button')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 1
        assert result[0].text == 'Submit'

    def test_chain_locators(self):
        locators = [
            ParsedLocator(strategy=LocatorStrategy.TYPE, value='ListView'),
            ParsedLocator(strategy=LocatorStrategy.TEXT, value='Item 2'),
        ]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 1
        assert result[0].text == 'Item 2'

    def test_no_match_returns_empty(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TEXT, value='Nonexistent')]
        result = find_elements(SAMPLE_TREE, locators)
        assert len(result) == 0


class TestFindElement:

    def test_find_first(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TYPE, value='Cell')]
        node = find_element(SAMPLE_TREE, locators, index='first')
        assert node.text == 'Item 1'

    def test_find_last(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TYPE, value='Cell')]
        node = find_element(SAMPLE_TREE, locators, index='last')
        assert node.text == 'Item 3'

    def test_find_by_index(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TYPE, value='Cell')]
        node = find_element(SAMPLE_TREE, locators, index='1')
        assert node.text == 'Item 2'

    def test_not_found_raises_error(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TEXT, value='Nonexistent')]
        with pytest.raises(MobileWrightElementNotFoundError):
            find_element(SAMPLE_TREE, locators)

    def test_index_out_of_range_raises_error(self):
        locators = [ParsedLocator(strategy=LocatorStrategy.TYPE, value='Cell')]
        with pytest.raises(MobileWrightElementNotFoundError):
            find_element(SAMPLE_TREE, locators, index='99')
