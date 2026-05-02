import pytest

from MobileWrightLibrary.rpc.protocol import (
    AppInfo,
    BoundingBox,
    DeviceInfo,
    HardwareButton,
    MobileWrightConnectionError,
    MobileWrightElementNotFoundError,
    MobileWrightError,
    MobileWrightRpcError,
    MobileWrightTimeoutError,
    Orientation,
    Platform,
    RecordingResult,
    ScreenSize,
    Session,
    SwipeDirection,
    ViewNode,
)


class TestEnums:

    def test_platform_values(self):
        assert Platform.IOS == 'ios'
        assert Platform.ANDROID == 'android'

    def test_orientation_values(self):
        assert Orientation.PORTRAIT == 'portrait'
        assert Orientation.LANDSCAPE == 'landscape'

    def test_swipe_direction_values(self):
        assert SwipeDirection.UP == 'up'
        assert SwipeDirection.DOWN == 'down'
        assert SwipeDirection.LEFT == 'left'
        assert SwipeDirection.RIGHT == 'right'

    def test_hardware_button_values(self):
        assert HardwareButton.HOME == 'HOME'
        assert HardwareButton.BACK == 'BACK'
        assert HardwareButton.POWER == 'POWER'


class TestBoundingBox:

    def test_from_dict(self):
        box = BoundingBox.from_dict({'x': 10, 'y': 20, 'width': 100, 'height': 50})
        assert box.x == 10
        assert box.y == 20
        assert box.width == 100
        assert box.height == 50

    def test_center(self):
        box = BoundingBox(x=10, y=20, width=100, height=50)
        assert box.center_x == 60.0
        assert box.center_y == 45.0

    def test_from_dict_defaults(self):
        box = BoundingBox.from_dict({})
        assert box.x == 0
        assert box.y == 0


class TestViewNode:

    def test_from_dict_basic(self):
        node = ViewNode.from_dict({
            'type': 'Button',
            'text': 'Submit',
            'label': 'submit-btn',
            'testId': 'submit',
            'bounds': {'x': 0, 'y': 0, 'width': 100, 'height': 50},
            'visible': True,
            'enabled': True,
        })
        assert node.type == 'Button'
        assert node.text == 'Submit'
        assert node.label == 'submit-btn'
        assert node.test_id == 'submit'
        assert node.bounds is not None

    def test_from_dict_with_children(self):
        node = ViewNode.from_dict({
            'type': 'Screen',
            'children': [
                {'type': 'Button', 'text': 'OK'},
                {'type': 'Text', 'text': 'Hello'},
            ],
        })
        assert len(node.children) == 2
        assert node.children[0].type == 'Button'
        assert node.children[1].text == 'Hello'

    def test_from_dict_accessibility_aliases(self):
        node = ViewNode.from_dict({
            'accessibilityLabel': 'my-label',
            'resourceId': 'my-id',
            'accessibilityRole': 'button',
            'isVisible': False,
            'isEnabled': False,
        })
        assert node.label == 'my-label'
        assert node.test_id == 'my-id'
        assert node.role == 'button'
        assert node.visible is False
        assert node.enabled is False


class TestAppInfo:

    def test_from_dict(self):
        app = AppInfo.from_dict({
            'bundleId': 'com.example.app',
            'name': 'Example',
            'version': '1.0.0',
        })
        assert app.bundle_id == 'com.example.app'
        assert app.name == 'Example'
        assert app.version == '1.0.0'


class TestDeviceInfo:

    def test_from_dict(self):
        device = DeviceInfo.from_dict({
            'id': 'device-123',
            'name': 'iPhone 15',
            'platform': 'ios',
            'type': 'simulator',
            'state': 'online',
            'osVersion': '17.0',
        })
        assert device.id == 'device-123'
        assert device.name == 'iPhone 15'
        assert device.platform == 'ios'
        assert device.os_version == '17.0'


class TestSession:

    def test_from_dict(self):
        session = Session.from_dict({
            'deviceId': 'dev-1',
            'platform': 'android',
        })
        assert session.device_id == 'dev-1'
        assert session.platform == 'android'


class TestRecordingResult:

    def test_from_dict(self):
        result = RecordingResult.from_dict({
            'status': 'completed',
            'duration': 30.5,
            'file': '/tmp/recording.mp4',
        })
        assert result.status == 'completed'
        assert result.duration == 30.5
        assert result.file == '/tmp/recording.mp4'


class TestExceptions:

    def test_exception_hierarchy(self):
        assert issubclass(MobileWrightConnectionError, MobileWrightError)
        assert issubclass(MobileWrightRpcError, MobileWrightError)
        assert issubclass(MobileWrightTimeoutError, MobileWrightError)
        assert issubclass(MobileWrightElementNotFoundError, MobileWrightError)

    def test_rpc_error_fields(self):
        err = MobileWrightRpcError('test error', code=-32600, data={'detail': 'info'})
        assert str(err) == 'test error'
        assert err.code == -32600
        assert err.data == {'detail': 'info'}
