import re

import pytest

from MobileWrightLibrary.locators.parser import parse_locator
from MobileWrightLibrary.locators.types import LocatorStrategy


class TestParseLocator:

    def test_label_strategy(self):
        result = parse_locator('label=Submit')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.LABEL
        assert result[0].value == 'Submit'

    def test_testid_strategy(self):
        result = parse_locator('testid=login-btn')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TESTID
        assert result[0].value == 'login-btn'

    def test_text_strategy(self):
        result = parse_locator('text=Hello World')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TEXT
        assert result[0].value == 'Hello World'

    def test_type_strategy(self):
        result = parse_locator('type=UIButton')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TYPE
        assert result[0].value == 'UIButton'

    def test_role_strategy(self):
        result = parse_locator('role=button')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.ROLE
        assert result[0].value == 'button'

    def test_placeholder_strategy(self):
        result = parse_locator('placeholder=Search here')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.PLACEHOLDER
        assert result[0].value == 'Search here'

    def test_default_text_strategy_no_prefix(self):
        result = parse_locator('Just some text')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TEXT
        assert result[0].value == 'Just some text'

    def test_unknown_strategy_fallback(self):
        result = parse_locator('unknown=value')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TEXT
        assert result[0].value == 'unknown=value'

    def test_chain_two_locators(self):
        result = parse_locator('type=ListView >> text=Item 1')
        assert len(result) == 2
        assert result[0].strategy == LocatorStrategy.TYPE
        assert result[0].value == 'ListView'
        assert result[1].strategy == LocatorStrategy.TEXT
        assert result[1].value == 'Item 1'

    def test_chain_three_locators(self):
        result = parse_locator('type=Form >> testid=field >> placeholder=Email')
        assert len(result) == 3
        assert result[0].strategy == LocatorStrategy.TYPE
        assert result[1].strategy == LocatorStrategy.TESTID
        assert result[2].strategy == LocatorStrategy.PLACEHOLDER

    def test_regex_value(self):
        result = parse_locator('text=/Hello.*/i')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.TEXT
        assert isinstance(result[0].value, re.Pattern)
        assert result[0].value.search('Hello World')
        assert result[0].value.search('hello there')

    def test_role_with_name(self):
        result = parse_locator('role=button[name=Submit]')
        assert len(result) == 1
        assert result[0].strategy == LocatorStrategy.ROLE
        assert result[0].value == 'button'
        assert result[0].role_name == 'Submit'

    def test_case_insensitive_strategy(self):
        result = parse_locator('LABEL=Test')
        assert result[0].strategy == LocatorStrategy.LABEL

    def test_value_with_equals_sign(self):
        result = parse_locator('text=a=b')
        assert result[0].strategy == LocatorStrategy.TEXT
        assert result[0].value == 'a=b'
