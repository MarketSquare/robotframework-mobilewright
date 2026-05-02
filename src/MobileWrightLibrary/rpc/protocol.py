from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Platform(str, Enum):
    IOS = 'ios'
    ANDROID = 'android'


class Orientation(str, Enum):
    PORTRAIT = 'portrait'
    LANDSCAPE = 'landscape'


class SwipeDirection(str, Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class HardwareButton(str, Enum):
    HOME = 'HOME'
    BACK = 'BACK'
    POWER = 'POWER'
    VOLUME_UP = 'VOLUME_UP'
    VOLUME_DOWN = 'VOLUME_DOWN'
    D_PAD_UP = 'D_PAD_UP'
    D_PAD_DOWN = 'D_PAD_DOWN'
    D_PAD_LEFT = 'D_PAD_LEFT'
    D_PAD_RIGHT = 'D_PAD_RIGHT'
    D_PAD_CENTER = 'D_PAD_CENTER'


class DeviceType(str, Enum):
    REAL = 'real'
    SIMULATOR = 'simulator'
    EMULATOR = 'emulator'


class DeviceState(str, Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'


@dataclass
class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @classmethod
    def from_dict(cls, data: dict) -> 'BoundingBox':
        return cls(
            x=data.get('x', 0),
            y=data.get('y', 0),
            width=data.get('width', 0),
            height=data.get('height', 0),
        )


@dataclass
class ScreenSize:
    width: int
    height: int

    @classmethod
    def from_dict(cls, data: dict) -> 'ScreenSize':
        return cls(width=data['width'], height=data['height'])


@dataclass
class ViewNode:
    type: str = ''
    text: str = ''
    label: str = ''
    test_id: str = ''
    role: str = ''
    placeholder: str = ''
    bounds: Optional[BoundingBox] = None
    visible: bool = True
    enabled: bool = True
    selected: bool = False
    focused: bool = False
    checked: bool = False
    value: Optional[str] = None
    children: list['ViewNode'] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'ViewNode':
        bounds = None
        if data.get('bounds'):
            bounds = BoundingBox.from_dict(data['bounds'])
        children = [cls.from_dict(c) for c in data.get('children', [])]
        return cls(
            type=data.get('type', ''),
            text=data.get('text', ''),
            label=data.get('label', data.get('accessibilityLabel', '')),
            test_id=data.get('testId', data.get('resourceId', '')),
            role=data.get('role', data.get('accessibilityRole', '')),
            placeholder=data.get('placeholder', ''),
            bounds=bounds,
            visible=data.get('visible', data.get('isVisible', True)),
            enabled=data.get('enabled', data.get('isEnabled', True)),
            selected=data.get('selected', data.get('isSelected', False)),
            focused=data.get('focused', data.get('isFocused', False)),
            checked=data.get('checked', data.get('isChecked', False)),
            value=data.get('value'),
            children=children,
        )


@dataclass
class AppInfo:
    bundle_id: str
    name: str = ''
    version: str = ''

    @classmethod
    def from_dict(cls, data: dict) -> 'AppInfo':
        return cls(
            bundle_id=data.get('bundleId', ''),
            name=data.get('name', ''),
            version=data.get('version', ''),
        )


@dataclass
class DeviceInfo:
    id: str
    name: str = ''
    platform: str = ''
    type: str = ''
    state: str = ''
    os_version: str = ''

    @classmethod
    def from_dict(cls, data: dict) -> 'DeviceInfo':
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            platform=data.get('platform', ''),
            type=data.get('type', ''),
            state=data.get('state', ''),
            os_version=data.get('osVersion', ''),
        )


@dataclass
class Session:
    device_id: str
    platform: str

    @classmethod
    def from_dict(cls, data: dict) -> 'Session':
        return cls(
            device_id=data.get('deviceId', ''),
            platform=data.get('platform', ''),
        )


@dataclass
class RecordingResult:
    status: str
    duration: float = 0.0
    file: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'RecordingResult':
        return cls(
            status=data.get('status', ''),
            duration=data.get('duration', 0.0),
            file=data.get('file'),
        )


# --- Exceptions ---

class MobileWrightError(Exception):
    pass


class MobileWrightConnectionError(MobileWrightError):
    pass


class MobileWrightRpcError(MobileWrightError):
    def __init__(self, message: str, code: int = -1, data: Any = None):
        super().__init__(message)
        self.code = code
        self.data = data


class MobileWrightTimeoutError(MobileWrightError):
    pass


class MobileWrightElementNotFoundError(MobileWrightError):
    pass
