import base64
import os

from robot.api import logger

from ..rpc.protocol import ScreenSize, SwipeDirection, ViewNode
from ..utils.type_converters import to_hardware_button, to_swipe_direction
from ._runonfailure import run_on_failure


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
        result = self._cache.current.call('screenshot', format='png')
        if isinstance(result, str):
            image_data = base64.b64decode(result)
        elif isinstance(result, dict):
            image_data = base64.b64decode(result.get('data', result.get('base64', '')))
        else:
            image_data = result

        if filename:
            filepath = os.path.abspath(filename)
        else:
            self._screenshot_counter = getattr(self, '_screenshot_counter', 0) + 1
            filepath = os.path.join(
                self._screenshot_dir,
                f'mobilewright-screenshot-{self._screenshot_counter}.png',
            )

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        logger.info(
            f'<a href="{filepath}">'
            f'<img src="{filepath}" width="800px"></a>',
            html=True,
        )
        return filepath

    @run_on_failure
    def swipe(self, direction):
        """Swipes the screen in the given direction.

        ``direction`` is one of: ``up``, ``down``, ``left``, ``right``.

        Example:
        | Swipe | down |
        | Swipe | left |
        """
        d = to_swipe_direction(direction)
        size = self._cache.current.call('getScreenSize')
        w, h = size.get('width', 0), size.get('height', 0)
        cx, cy = w // 2, h // 2
        distance_x, distance_y = w // 3, h // 3

        swipe_map = {
            SwipeDirection.UP: (cx, cy + distance_y, cx, cy - distance_y),
            SwipeDirection.DOWN: (cx, cy - distance_y, cx, cy + distance_y),
            SwipeDirection.LEFT: (cx + distance_x, cy, cx - distance_x, cy),
            SwipeDirection.RIGHT: (cx - distance_x, cy, cx + distance_x, cy),
        }
        sx, sy, ex, ey = swipe_map[d]
        self._cache.current.call(
            'swipe', startX=sx, startY=sy, endX=ex, endY=ey, duration=300,
        )
        logger.info(f"Swiped {d.value}")

    @run_on_failure
    def tap_coordinates(self, x, y):
        """Taps at the given screen coordinates.

        Example:
        | Tap Coordinates | 100 | 200 |
        """
        self._cache.current.call('tap', x=int(x), y=int(y))
        logger.info(f"Tapped at ({x}, {y})")

    @run_on_failure
    def double_tap_coordinates(self, x, y):
        """Double-taps at the given screen coordinates.

        Example:
        | Double Tap Coordinates | 100 | 200 |
        """
        self._cache.current.call('doubleTap', x=int(x), y=int(y))
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
            'longPress', x=int(x), y=int(y), duration=int(duration),
        )
        logger.info(f"Long-pressed at ({x}, {y}) for {duration}ms")

    @run_on_failure
    def go_back(self):
        """Navigates back by pressing the BACK button.

        Example:
        | Go Back |
        """
        self._cache.current.call('pressButton', button='BACK')
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
        self._cache.current.call('pressButton', button=btn.value)
        logger.info(f"Pressed button: {btn.value}")

    @run_on_failure
    def get_view_tree(self):
        """Returns the full view hierarchy as a nested dictionary structure.

        Each node contains: type, text, label, test_id, bounds, visible,
        enabled, selected, children.

        Example:
        | ${tree}= | Get View Tree |
        """
        result = self._cache.current.call('getViewHierarchy')
        nodes = [ViewNode.from_dict(n) for n in (result or [])]
        return [vars(n) for n in nodes]

    @run_on_failure
    def get_screen_size(self):
        """Returns the screen size as a dictionary with ``width`` and ``height``.

        Example:
        | ${size}= | Get Screen Size |
        | Log | Width: ${size}[width], Height: ${size}[height] |
        """
        result = self._cache.current.call('getScreenSize')
        size = ScreenSize.from_dict(result) if result else ScreenSize(0, 0)
        return vars(size)
