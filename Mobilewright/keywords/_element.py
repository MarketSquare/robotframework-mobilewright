from robot.api import logger

from ..locators import find_element, find_elements, parse_locator
from ..rpc.protocol import ViewNode
from ._runonfailure import run_on_failure


class _Element:

    def _get_view_tree(self):
        result = self._cache.current.call('getViewHierarchy')
        return [ViewNode.from_dict(n) for n in (result or [])]

    def _find_element(self, locator, index='first'):
        tree = self._get_view_tree()
        locators = parse_locator(locator)
        return find_element(tree, locators, index=index)

    def _find_elements(self, locator):
        tree = self._get_view_tree()
        locators = parse_locator(locator)
        return find_elements(tree, locators)

    # --- Interaction Keywords ---

    @run_on_failure
    def tap_element(self, locator, index='first'):
        """Taps the element matching the locator.

        ``locator`` uses the format ``strategy=value``. Supported strategies:
        ``label``, ``testid``, ``text``, ``type``, ``role``, ``placeholder``.
        Chain locators with ``>>``.

        ``index`` selects which match: ``first`` (default), ``last``, or a 0-based number.

        Examples:
        | Tap Element | text=Login |
        | Tap Element | testid=submit-btn |
        | Tap Element | type=ListView >> text=Item 1 |
        | Tap Element | text=Option | index=2 |
        """
        node = self._find_element(locator, index)
        x, y = node.bounds.center_x, node.bounds.center_y
        self._cache.current.call('tap', x=int(x), y=int(y))
        logger.info(f"Tapped element: {locator}")

    @run_on_failure
    def double_tap_element(self, locator, index='first'):
        """Double-taps the element matching the locator.

        Example:
        | Double Tap Element | text=Item |
        """
        node = self._find_element(locator, index)
        x, y = node.bounds.center_x, node.bounds.center_y
        self._cache.current.call('doubleTap', x=int(x), y=int(y))
        logger.info(f"Double-tapped element: {locator}")

    @run_on_failure
    def long_press_element(self, locator, duration=1000, index='first'):
        """Long-presses the element matching the locator.

        ``duration`` is the press duration in milliseconds (default: 1000).

        Example:
        | Long Press Element | text=Item | duration=2000 |
        """
        node = self._find_element(locator, index)
        x, y = node.bounds.center_x, node.bounds.center_y
        self._cache.current.call(
            'longPress', x=int(x), y=int(y), duration=int(duration),
        )
        logger.info(f"Long-pressed element: {locator} for {duration}ms")

    @run_on_failure
    def fill_element(self, locator, text, index='first'):
        """Types text into the element matching the locator.

        Taps the element first to focus it, then types the text.

        Examples:
        | Fill Element | testid=username-input | admin@test.com |
        | Fill Element | placeholder=Search | query text |
        """
        node = self._find_element(locator, index)
        x, y = node.bounds.center_x, node.bounds.center_y
        self._cache.current.call('tap', x=int(x), y=int(y))
        self._cache.current.call('typeText', text=text)
        logger.info(f"Filled element: {locator} with '{text}'")

    @run_on_failure
    def swipe_element(self, locator, direction, index='first'):
        """Swipes on the element matching the locator.

        ``direction`` is one of: ``up``, ``down``, ``left``, ``right``.

        Example:
        | Swipe Element | testid=carousel | left |
        """
        from ..utils.type_converters import to_swipe_direction
        from ..rpc.protocol import SwipeDirection

        node = self._find_element(locator, index)
        d = to_swipe_direction(direction)
        b = node.bounds
        cx, cy = int(b.center_x), int(b.center_y)
        dx, dy = int(b.width // 3), int(b.height // 3)

        swipe_map = {
            SwipeDirection.UP: (cx, cy + dy, cx, cy - dy),
            SwipeDirection.DOWN: (cx, cy - dy, cx, cy + dy),
            SwipeDirection.LEFT: (cx + dx, cy, cx - dx, cy),
            SwipeDirection.RIGHT: (cx - dx, cy, cx + dx, cy),
        }
        sx, sy, ex, ey = swipe_map[d]
        self._cache.current.call(
            'swipe', startX=sx, startY=sy, endX=ex, endY=ey, duration=300,
        )
        logger.info(f"Swiped {d.value} on element: {locator}")

    @run_on_failure
    def scroll_element_into_view(self, locator, index='first', max_swipes=10):
        """Scrolls the screen until the element matching the locator is visible.

        ``max_swipes`` is the maximum number of swipe attempts (default: 10).

        Example:
        | Scroll Element Into View | text=Footer Item |
        """
        tree = self._get_view_tree()
        locators = parse_locator(locator)

        for _ in range(int(max_swipes)):
            matches = find_elements(tree, locators)
            if matches:
                node = matches[0] if index == 'first' else matches[-1]
                if node.visible and node.bounds:
                    logger.info(f"Element already visible: {locator}")
                    return
            size = self._cache.current.call('getScreenSize')
            cx = size.get('width', 0) // 2
            cy = size.get('height', 0) // 2
            dy = size.get('height', 0) // 4
            self._cache.current.call(
                'swipe', startX=cx, startY=cy + dy, endX=cx, endY=cy - dy,
                duration=300,
            )
            tree = self._get_view_tree()

        from ..rpc.protocol import MobileWrightElementNotFoundError
        raise MobileWrightElementNotFoundError(
            f"Element '{locator}' not found after {max_swipes} swipe attempts"
        )

    # --- Query Keywords ---

    @run_on_failure
    def get_element_text(self, locator, index='first'):
        """Returns the text content of the element matching the locator.

        Example:
        | ${text}= | Get Element Text | testid=title |
        """
        node = self._find_element(locator, index)
        return node.text

    @run_on_failure
    def get_element_value(self, locator, index='first'):
        """Returns the value of the element matching the locator.

        Example:
        | ${value}= | Get Element Value | testid=input-field |
        """
        node = self._find_element(locator, index)
        return node.value

    @run_on_failure
    def get_element_bounding_box(self, locator, index='first'):
        """Returns the bounding box of the element as a dictionary.

        Keys: ``x``, ``y``, ``width``, ``height``.

        Example:
        | ${box}= | Get Element Bounding Box | text=Button |
        """
        node = self._find_element(locator, index)
        if node.bounds:
            return vars(node.bounds)
        return {'x': 0, 'y': 0, 'width': 0, 'height': 0}

    @run_on_failure
    def get_element_count(self, locator):
        """Returns the number of elements matching the locator.

        Example:
        | ${count}= | Get Element Count | type=UIButton |
        """
        matches = self._find_elements(locator)
        count = len(matches)
        logger.info(f"Found {count} element(s) matching: {locator}")
        return count

    @run_on_failure
    def get_elements(self, locator):
        """Returns all elements matching the locator as a list of dictionaries.

        Example:
        | @{elements}= | Get Elements | type=UITableViewCell |
        """
        matches = self._find_elements(locator)
        return [vars(n) for n in matches]

    @run_on_failure
    def capture_element_screenshot(self, locator, filename=None, index='first'):
        """Takes a screenshot and crops it to the element's bounding box.

        Example:
        | Capture Element Screenshot | testid=chart | chart.png |
        """
        self._find_element(locator, index)
        return self.capture_screenshot(filename=filename)

    # --- Assertion Keywords ---

    @run_on_failure
    def element_should_be_visible(self, locator, index='first', message=None):
        """Asserts that the element matching the locator is visible.

        Example:
        | Element Should Be Visible | text=Welcome |
        """
        node = self._find_element(locator, index)
        if not node.visible:
            raise AssertionError(
                message or f"Element '{locator}' is not visible"
            )

    @run_on_failure
    def element_should_not_be_visible(self, locator, index='first', message=None):
        """Asserts that no visible element matches the locator.

        Example:
        | Element Should Not Be Visible | text=Error |
        """
        tree = self._get_view_tree()
        locators = parse_locator(locator)
        matches = find_elements(tree, locators)
        visible = [m for m in matches if m.visible]
        if visible:
            raise AssertionError(
                message or f"Element '{locator}' is visible but should not be"
            )

    @run_on_failure
    def element_should_be_enabled(self, locator, index='first', message=None):
        """Asserts that the element is enabled.

        Example:
        | Element Should Be Enabled | testid=submit-btn |
        """
        node = self._find_element(locator, index)
        if not node.enabled:
            raise AssertionError(
                message or f"Element '{locator}' is not enabled"
            )

    @run_on_failure
    def element_should_be_disabled(self, locator, index='first', message=None):
        """Asserts that the element is disabled.

        Example:
        | Element Should Be Disabled | testid=submit-btn |
        """
        node = self._find_element(locator, index)
        if node.enabled:
            raise AssertionError(
                message or f"Element '{locator}' is enabled but should be disabled"
            )

    @run_on_failure
    def element_should_be_selected(self, locator, index='first', message=None):
        """Asserts that the element is selected.

        Example:
        | Element Should Be Selected | testid=checkbox |
        """
        node = self._find_element(locator, index)
        if not node.selected:
            raise AssertionError(
                message or f"Element '{locator}' is not selected"
            )

    @run_on_failure
    def element_should_be_focused(self, locator, index='first', message=None):
        """Asserts that the element is focused.

        Example:
        | Element Should Be Focused | testid=input |
        """
        node = self._find_element(locator, index)
        if not node.focused:
            raise AssertionError(
                message or f"Element '{locator}' is not focused"
            )

    @run_on_failure
    def element_should_be_checked(self, locator, index='first', message=None):
        """Asserts that the element is checked.

        Example:
        | Element Should Be Checked | testid=toggle |
        """
        node = self._find_element(locator, index)
        if not node.checked:
            raise AssertionError(
                message or f"Element '{locator}' is not checked"
            )

    @run_on_failure
    def element_text_should_be(self, locator, expected, index='first', message=None):
        """Asserts that the element's text matches exactly.

        Example:
        | Element Text Should Be | testid=title | Welcome Home |
        """
        node = self._find_element(locator, index)
        actual = node.text
        if actual != expected:
            raise AssertionError(
                message or f"Element '{locator}' text was '{actual}', expected '{expected}'"
            )

    @run_on_failure
    def element_text_should_contain(self, locator, expected, index='first', message=None):
        """Asserts that the element's text contains the expected substring.

        Example:
        | Element Text Should Contain | role=heading | Welcome |
        """
        node = self._find_element(locator, index)
        actual = node.text
        if expected not in (actual or ''):
            raise AssertionError(
                message or f"Element '{locator}' text '{actual}' does not contain '{expected}'"
            )
