import pytest

from Mobilewright.rpc.protocol import (
    HardwareButton,
    Orientation,
    Platform,
    SwipeDirection,
)
from Mobilewright.utils.type_converters import (
    to_hardware_button,
    to_orientation,
    to_platform,
    to_seconds,
    to_swipe_direction,
)


class TestToPlatform:

    def test_ios(self):
        assert to_platform('ios') == Platform.IOS

    def test_android(self):
        assert to_platform('android') == Platform.ANDROID

    def test_case_insensitive(self):
        assert to_platform('IOS') == Platform.IOS
        assert to_platform('Android') == Platform.ANDROID

    def test_invalid(self):
        with pytest.raises(ValueError, match='Invalid platform'):
            to_platform('windows')


class TestToOrientation:

    def test_portrait(self):
        assert to_orientation('portrait') == Orientation.PORTRAIT

    def test_landscape(self):
        assert to_orientation('landscape') == Orientation.LANDSCAPE

    def test_invalid(self):
        with pytest.raises(ValueError, match='Invalid orientation'):
            to_orientation('diagonal')


class TestToSwipeDirection:

    def test_all_directions(self):
        assert to_swipe_direction('up') == SwipeDirection.UP
        assert to_swipe_direction('down') == SwipeDirection.DOWN
        assert to_swipe_direction('left') == SwipeDirection.LEFT
        assert to_swipe_direction('right') == SwipeDirection.RIGHT

    def test_invalid(self):
        with pytest.raises(ValueError, match='Invalid swipe direction'):
            to_swipe_direction('diagonal')


class TestToHardwareButton:

    def test_home(self):
        assert to_hardware_button('HOME') == HardwareButton.HOME

    def test_case_insensitive(self):
        assert to_hardware_button('back') == HardwareButton.BACK
        assert to_hardware_button('Power') == HardwareButton.POWER

    def test_invalid(self):
        with pytest.raises(ValueError, match='Invalid hardware button'):
            to_hardware_button('INVALID')


class TestToSeconds:

    def test_none(self):
        assert to_seconds(None) is None

    def test_int(self):
        assert to_seconds(10) == 10.0

    def test_float(self):
        assert to_seconds(5.5) == 5.5

    def test_rf_time_string(self):
        assert to_seconds('10s') == 10.0
        assert to_seconds('1 min') == 60.0
        assert to_seconds('500ms') == 0.5
