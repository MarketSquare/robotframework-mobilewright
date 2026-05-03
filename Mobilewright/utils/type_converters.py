from robot.utils import timestr_to_secs, secs_to_timestr

from ..rpc.protocol import (
    HardwareButton,
    Orientation,
    Platform,
    SwipeDirection,
)


def to_platform(value: str) -> Platform:
    try:
        return Platform(value.lower().strip())
    except ValueError:
        raise ValueError(
            f"Invalid platform '{value}'. Expected: ios, android"
        )


def to_orientation(value: str) -> Orientation:
    try:
        return Orientation(value.lower().strip())
    except ValueError:
        raise ValueError(
            f"Invalid orientation '{value}'. Expected: portrait, landscape"
        )


def to_swipe_direction(value: str) -> SwipeDirection:
    try:
        return SwipeDirection(value.lower().strip())
    except ValueError:
        raise ValueError(
            f"Invalid swipe direction '{value}'. Expected: up, down, left, right"
        )


def to_hardware_button(value: str) -> HardwareButton:
    try:
        return HardwareButton(value.upper().strip())
    except ValueError:
        valid = ', '.join(b.value for b in HardwareButton)
        raise ValueError(
            f"Invalid hardware button '{value}'. Expected one of: {valid}"
        )


def to_seconds(value) -> float:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return timestr_to_secs(value)
