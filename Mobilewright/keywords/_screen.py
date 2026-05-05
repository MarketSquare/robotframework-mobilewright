import base64
import os

from robot.api import logger

from ..rpc.protocol import SwipeDirection, ViewNode
from ..utils.type_converters import to_hardware_button, to_swipe_direction
from ._runonfailure import run_on_failure


def _strip_data_uri(s):
    if isinstance(s, str) and s.startswith('data:') and ',' in s:
        return s.split(',', 1)[1]
    return s


class _Screen:

    @run_on_failure
    def capture_screenshot(self, filename=None):
        """Takes a screenshot of the device screen.

        ``filename`` is the path to save the screenshot. If not given, the
        screenshot is saved to the configured screenshot directory with an
        auto-generated name and embedded in the Robot Framework log.

        Returns the path to the saved screenshot file.

        Example:
        | Capture Screenshot |
        | Capture Screenshot | login_page.png |
        """
        result = self._cache.current.call('device.screenshot', format='png')
        image_data = self._decode_screenshot(result)

        if filename:
            filepath = os.path.abspath(filename)
        else:
            self._screenshot_counter = getattr(self, '_screenshot_counter', 0) + 1
            filepath = os.path.join(
                self._screenshot_dir,
                f'mobilewright-screenshot-{self._screenshot_counter}.png',
            )

        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        logger.info(
            f'<a href="{filepath}">'
            f'<img src="{filepath}" width="800px"></a>',
            html=True,
        )
        return filepath

    @staticmethod
    def _decode_screenshot(result):
        if result is None:
            return b''
        if isinstance(result, bytes):
            return result
        if isinstance(result, str):
            return base64.b64decode(_strip_data_uri(result))
        if isinstance(result, dict):
            for key in ('data', 'base64', 'image', 'screenshot', 'content'):
                if key in result and result[key]:
                    return base64.b64decode(_strip_data_uri(result[key]))
        return b''

    def _get_screen_size(self):
        info = self._cache.current.call('device.info') or {}
        device = info.get('device', info)
        size = device.get('screenSize') or device.get('screen') or {}
        width = int(size.get('width', 0) or device.get('width', 0))
        height = int(size.get('height', 0) or device.get('height', 0))
        return width, height

    @run_on_failure
    def swipe(self, direction):
        """Swipes the screen in the given direction.

        ``direction`` is one of: ``up``, ``down``, ``left``, ``right``.

        Example:
        | Swipe | down |
        | Swipe | left |
        """
        d = to_swipe_direction(direction)
        w, h = self._get_screen_size()
        if w == 0 or h == 0:
            raise RuntimeError(
                "Could not determine screen size from device.info. "
                "Try Swipe Element or Tap Coordinates instead."
            )
        cx, cy = w // 2, h // 2
        dx, dy = w // 3, h // 3

        swipe_map = {
            SwipeDirection.UP: (cx, cy + dy, cx, cy - dy),
            SwipeDirection.DOWN: (cx, cy - dy, cx, cy + dy),
            SwipeDirection.LEFT: (cx + dx, cy, cx - dx, cy),
            SwipeDirection.RIGHT: (cx - dx, cy, cx + dx, cy),
        }
        x1, y1, x2, y2 = swipe_map[d]
        self._cache.current.call(
            'device.io.swipe', x1=x1, y1=y1, x2=x2, y2=y2,
        )
        logger.info(f"Swiped {d.value}")

    @run_on_failure
    def tap_coordinates(self, x, y):
        """Taps at the given screen coordinates.

        Example:
        | Tap Coordinates | 100 | 200 |
        """
        self._cache.current.call('device.io.tap', x=int(x), y=int(y))
        logger.info(f"Tapped at ({x}, {y})")

    @run_on_failure
    def double_tap_coordinates(self, x, y):
        """Double-taps at the given screen coordinates.

        Implemented as two consecutive taps since mobilecli has no native
        double-tap RPC.

        Example:
        | Double Tap Coordinates | 100 | 200 |
        """
        client = self._cache.current
        client.call('device.io.tap', x=int(x), y=int(y))
        client.call('device.io.tap', x=int(x), y=int(y))
        logger.info(f"Double-tapped at ({x}, {y})")

    @run_on_failure
    def long_press_coordinates(self, x, y, duration=1000):
        """Long-presses at the given screen coordinates.

        ``duration`` is the press duration in milliseconds (default: 1000).

        Example:
        | Long Press Coordinates | 100 | 200 |
        | Long Press Coordinates | 100 | 200 | duration=2000 |
        """
        self._cache.current.call(
            'device.io.longpress',
            x=int(x), y=int(y), duration=int(duration),
        )
        logger.info(f"Long-pressed at ({x}, {y}) for {duration}ms")

    @run_on_failure
    def go_back(self):
        """Navigates back by pressing the BACK button.

        Example:
        | Go Back |
        """
        self._cache.current.call('device.io.button', button='BACK')
        logger.info("Navigated back")

    @run_on_failure
    def press_button(self, button):
        """Presses a hardware button on the device.

        ``button`` is one of: ``HOME``, ``BACK``, ``POWER``, ``VOLUME_UP``,
        ``VOLUME_DOWN``, ``D_PAD_UP``, ``D_PAD_DOWN``, ``D_PAD_LEFT``,
        ``D_PAD_RIGHT``, ``D_PAD_CENTER``.

        Example:
        | Press Button | HOME |
        | Press Button | VOLUME_UP |
        """
        btn = to_hardware_button(button)
        self._cache.current.call('device.io.button', button=btn.value)
        logger.info(f"Pressed button: {btn.value}")

    @run_on_failure
    def type_text(self, text):
        """Types text into the currently focused element.

        Example:
        | Type Text | Hello World |
        """
        self._cache.current.call('device.io.text', text=text)
        logger.info(f"Typed text: {text}")

    @run_on_failure
    def get_view_tree(self):
        """Returns the full view hierarchy as a list of nested dictionaries.

        Each node contains: type, text, label, test_id, bounds, visible,
        enabled, selected, children.

        Example:
        | ${tree}= | Get View Tree |
        """
        result = self._cache.current.call('device.dump.ui')
        nodes = self._normalize_view_tree(result)
        return [vars(n) for n in nodes]

    @staticmethod
    def _normalize_view_tree(result):
        if result is None:
            return []
        if isinstance(result, list):
            raw_nodes = result
        elif isinstance(result, dict):
            raw_nodes = (
                result.get('elements')
                or result.get('tree')
                or result.get('nodes')
                or result.get('hierarchy')
                or result.get('ui')
                or []
            )
        else:
            return []
        if not isinstance(raw_nodes, list):
            raw_nodes = [raw_nodes]
        return [ViewNode.from_dict(n) for n in raw_nodes]

    @run_on_failure
    def get_screen_size(self):
        """Returns the screen size as a dictionary with ``width`` and ``height``.

        Example:
        | ${size}= | Get Screen Size |
        | Log | Width: ${size}[width], Height: ${size}[height] |
        """
        w, h = self._get_screen_size()
        return {'width': w, 'height': h}
