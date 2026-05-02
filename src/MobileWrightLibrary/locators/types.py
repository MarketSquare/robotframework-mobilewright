from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union
import re


class LocatorStrategy(str, Enum):
    LABEL = 'label'
    TESTID = 'testid'
    TEXT = 'text'
    TYPE = 'type'
    ROLE = 'role'
    PLACEHOLDER = 'placeholder'


@dataclass
class ParsedLocator:
    strategy: LocatorStrategy
    value: Union[str, re.Pattern]
    role_name: Optional[str] = None

    def __str__(self):
        if self.role_name:
            return f"{self.strategy.value}={self.value}[name={self.role_name}]"
        return f"{self.strategy.value}={self.value}"
