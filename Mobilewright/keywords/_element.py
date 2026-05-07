import time

from robot.api import logger

from ..locators import find_element, find_elements, parse_locator
from ..rpc.protocol import (
    MobileWrightElementNotFoundError,
    MobileWrightTimeoutError,
    SwipeDirection,
    ViewNode,
)
from ..utils.type_converters import to_seconds, to_swipe_direction
from ._runonfailure import run_on_failure

_POLL_INTERVAL = 0.1
_BOUNDS_STABLE_DURATION = 0.1


class _Element:

    # ---------- Internal helpers ----------

    def _get_view_tree(self):
        result = self._cache.current.call('device.dump.ui')
        if isinstance(result, dict) and 'elements' in result:
            return [ViewNode.from_dict(n) for n in result['elements']]
        if isinstance(result, list):
            return [ViewNode.from_dict(n) for n in result]
        return []

    def _find_element(self, locator, index='first'):
        """Single-shot lookup. No auto-wait. Used by multi-element getters."""
        tree = self._get_view_tree()
        locators = parse_locator(locator)
        return find_element(tree, locators, index=index)

    def _find_elements(self, locator):
        """Single-shot list lookup. No auto-wait."""
        tree = self._get_view_tree()
        locators = parse_locator(locator)
        return find_elements(tree, locators)

    def _resolve_actionable(self, locator, index='first', timeout=None):
        """Poll the view tree until the element is found, visible, enabled,
        and bounds-stable for ``_BOUNDS_STABLE_DURATION`` seconds.

        Used by all interaction keywords (tap, fill, swipe...) so the user
        does not need to add explicit ``Wait Until Element Is Visible``
        before each action.

        Raises :class:`MobileWrightTimeoutError` after ``timeout`` seconds.
        """
        effective_timeout = to_seconds(timeout) if timeout else self._timeout
        end_time = time.monotonic() + effective_timeout
        locators = parse_locator(locator)
        last_bounds = None
        last_bounds_time = None
        last_state = "no match"

        while time.monotonic() < end_time:
            try:
                tree = self._get_view_tree()
                node = find_element(tree, locators, index=index)
            except MobileWrightElementNotFoundError as e:
                last_state = str(e)
                time.sleep(_POLL_INTERVAL)
                continue

            if not (node.visible and node.enabled and node.bounds is not None):
                reasons = []
                if not node.visible:
                    reasons.append('not visible')
                if not node.enabled:
                    reasons.append('not enabled')
                if node.bounds is None:
                    reasons.append('no bounds')
                last_state = ', '.join(reasons)
                last_bounds = None
                last_bounds_time = None
                time.sleep(_POLL_INTERVAL)
                continue

            if last_bounds is not None and last_bounds == node.bounds:
                if time.monotonic() - last_bounds_time >= _BOUNDS_STABLE_DURATION:
                    return node
            else:
                last_bounds = node.bounds
                last_bounds_time = time.monotonic()
                last_state = 'bounds not stable'

            time.sleep(_POLL_INTERVAL)

        raise MobileWrightTimeoutError(
            f"Element '{locator}' not actionable after {effective_timeout}s "
            f"(last state: {last_state})"
        )

    def _resolve_state(self, locator, predicate, description,
                       index='first', timeout=None):
        """Poll the view tree until ``predicate(node)`` is true.

        Used by assertions and getters. The element must exist for the
        predicate to be evaluated (an absent element is treated as 'not
        matching the predicate').
        """
        effective_timeout = to_seconds(timeout) if timeout else self._timeout
        end_time = time.monotonic() + effective_timeout
        locators = parse_locator(locator)

        while time.monotonic() < end_time:
            try:
                tree = self._get_view_tree()
                node = find_element(tree, locators, index=index)
                if predicate(node):
                    return node
            except MobileWrightElementNotFoundError:
                pass
            time.sleep(_POLL_INTERVAL)

        raise MobileWrightTimeoutError(
            f"Element '{locator}' did not become {description} "
            f"after {effective_timeout}s"
        )

    def _resolve_visible(self, locator, index='first', timeout=None):
        """Poll until the element exists and is visible. Used by getters
        that operate on a single element (text, value, bounds, screenshot)."""
        return self._resolve_state(
            locator, lambda n: n.visible, 'visible', index, timeout,
        )

    def _resolve_absent_or_hidden(self, locator, timeout=None):
        """Poll until no visible element matches the locator. Used by
        ``Element Should Not Be Visible``."""
        effective_timeout = to_seconds(timeout) if timeout else self._timeout
        end_time = time.monotonic() + effective_timeout
        locators = parse_locator(locator)

        while time.monotonic() < end_time:
            tree = self._get_view_tree()
            visible = [m for m in find_elements(tree, locators) if m.visible]
            if not visible:
                return
            time.sleep(_POLL_INTERVAL)

        raise MobileWrightTimeoutError(
            f"Element '{locator}' was still visible after {effective_timeout}s"
        )

    # ---------- Interaction keywords (auto-wait actionable) ----------

    @run_on_failure
    def tap_element(self, locator, index='first', timeout=None):
        """Taps the element matching the locator.

        ``locator`` uses the format ``strategy=value``. Supported strategies:
        ``label``, ``testid``, ``text``, ``type``, ``role``, ``placeholder``.
        Chain locators with ``>>``.

        ``index`` selects which match: ``first`` (default), ``last``, or a
        0-based number.

        ``timeout`` overrides the library default while polling for the
        element to be actionable (visible, enabled, bounds stable).

        The keyword auto-waits until the element is actionable, so explicit
        ``Wait Until Element Is Visible`` calls are usually not needed.

        Examples:
        | Tap Element | text=Login |
        | Tap Element | testid=submit-btn |
        | Tap Element | type=ListView >> text=Item 1 |
        | Tap Element | text=Option | index=2 |
        """
        node = self._resolve_actionable(locator, index, timeout)
        x, y = int(node.bounds.center_x), int(node.bounds.center_y)
        self._cache.current.call('device.io.tap', x=x, y=y)
        logger.info(f"Tapped element: {locator}")

    @run_on_failure
    def double_tap_element(self, locator, index='first', timeout=None):
        """Double-taps the element matching the locator.

        Auto-waits until the element is actionable. Implemented as two
        consecutive taps.

        Example:
        | Double Tap Element | text=Item |
        """
        node = self._resolve_actionable(locator, index, timeout)
        x, y = int(node.bounds.center_x), int(node.bounds.center_y)
        client = self._cache.current
        client.call('device.io.tap', x=x, y=y)
        client.call('device.io.tap', x=x, y=y)
        logger.info(f"Double-tapped element: {locator}")

    @run_on_failure
    def long_press_element(self, locator, duration=1000, index='first',
                           timeout=None):
        """Long-presses the element matching the locator.

        ``duration`` is the press duration in milliseconds (default: 1000).
        Auto-waits until the element is actionable.

        Example:
        | Long Press Element | text=Item | duration=2000 |
        """
        node = self._resolve_actionable(locator, index, timeout)
        x, y = int(node.bounds.center_x), int(node.bounds.center_y)
        self._cache.current.call(
            'device.io.longpress', x=x, y=y, duration=int(duration),
        )
        logger.info(f"Long-pressed element: {locator} for {duration}ms")

    @run_on_failure
    def fill_element(self, locator, text, index='first', timeout=None):
        """Types ``text`` into the element matching the locator.

        Taps the element first to focus it, then types the text. Auto-waits
        until the element is actionable.

        Examples:
        | Fill Element | testid=username-input | admin@test.com |
        | Fill Element | placeholder=Search | query text |
        """
        node = self._resolve_actionable(locator, index, timeout)
        x, y = int(node.bounds.center_x), int(node.bounds.center_y)
        client = self._cache.current
        client.call('device.io.tap', x=x, y=y)
        client.call('device.io.text', text=text)
        logger.info(f"Filled element: {locator} with '{text}'")

    @run_on_failure
    def swipe_element(self, locator, direction, index='first', timeout=None):
        """Swipes on the element matching the locator.

        ``direction`` is one of: ``up``, ``down``, ``left``, ``right``.
        Auto-waits until the element is actionable.

        Example:
        | Swipe Element | testid=carousel | left |
        """
        node = self._resolve_actionable(locator, index, timeout)
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
        x1, y1, x2, y2 = swipe_map[d]
        self._cache.current.call(
            'device.io.swipe', x1=x1, y1=y1, x2=x2, y2=y2,
        )
        logger.info(f"Swiped {d.value} on element: {locator}")

    @run_on_failure
    def scroll_element_into_view(self, locator, index='first', max_swipes=10):
        """Scrolls the screen until the element matching the locator is visible.

        ``max_swipes`` is the maximum number of swipe attempts (default: 10).

        Example:
        | Scroll Element Into View | text=Footer Item |
        """
        locators = parse_locator(locator)

        for _ in range(int(max_swipes)):
            tree = self._get_view_tree()
            matches = find_elements(tree, locators)
            if matches:
                node = matches[0] if index == 'first' else matches[-1]
                if node.visible and node.bounds:
                    logger.info(f"Element visible: {locator}")
                    return
            w, h = self._get_screen_size()
            if w == 0 or h == 0:
                raise RuntimeError(
                    "Could not determine screen size from device.info."
                )
            cx, cy = w // 2, h // 2
            dy = h // 4
            self._cache.current.call(
                'device.io.swipe',
                x1=cx, y1=cy + dy, x2=cx, y2=cy - dy,
            )

        raise MobileWrightElementNotFoundError(
            f"Element '{locator}' not found after {max_swipes} swipe attempts"
        )

    # ---------- Single-element getters (auto-wait visible) ----------

    @run_on_failure
    def get_element_text(self, locator, index='first', timeout=None):
        """Returns the text content of the element matching the locator.

        Auto-waits for the element to be visible.

        Example:
        | ${text}= | Get Element Text | testid=title |
        """
        return self._resolve_visible(locator, index, timeout).text

    @run_on_failure
    def get_element_value(self, locator, index='first', timeout=None):
        """Returns the value of the element matching the locator.

        Auto-waits for the element to be visible.

        Example:
        | ${value}= | Get Element Value | testid=input-field |
        """
        return self._resolve_visible(locator, index, timeout).value

    @run_on_failure
    def get_element_bounding_box(self, locator, index='first', timeout=None):
        """Returns the bounding box of the element as a dictionary.

        Keys: ``x``, ``y``, ``width``, ``height``. Auto-waits for the element
        to be visible.

        Example:
        | ${box}= | Get Element Bounding Box | text=Button |
        """
        node = self._resolve_visible(locator, index, timeout)
        if node.bounds:
            return vars(node.bounds)
        return {'x': 0, 'y': 0, 'width': 0, 'height': 0}

    @run_on_failure
    def capture_element_screenshot(self, locator, filename=None, index='first',
                                    timeout=None):
        """Takes a screenshot of the screen.

        Note: mobilecli does not currently support per-element screenshots,
        so this captures the full screen after auto-waiting for the element
        to be visible.

        Example:
        | Capture Element Screenshot | testid=chart | chart.png |
        """
        self._resolve_visible(locator, index, timeout)
        return self.capture_screenshot(filename=filename)

    # ---------- Multi-element queries (no auto-wait) ----------

    @run_on_failure
    def get_element_count(self, locator):
        """Returns the number of elements matching the locator (immediate, no auto-wait).

        Returning ``0`` is a valid result, so this keyword does not poll —
        it answers based on the current view tree.

        Example:
        | ${count}= | Get Element Count | type=UIButton |
        """
        matches = self._find_elements(locator)
        count = len(matches)
        logger.info(f"Found {count} element(s) matching: {locator}")
        return count

    @run_on_failure
    def get_elements(self, locator):
        """Returns all elements matching the locator (immediate, no auto-wait).

        Example:
        | @{elements}= | Get Elements | type=UITableViewCell |
        """
        matches = self._find_elements(locator)
        return [vars(n) for n in matches]

    # ---------- Assertions (auto-wait until predicate) ----------

    @run_on_failure
    def element_should_be_visible(self, locator, index='first',
                                   timeout=None, message=None):
        """Asserts that the element matching the locator is visible.

        Auto-waits up to ``timeout`` for the element to become visible.

        Example:
        | Element Should Be Visible | text=Welcome |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.visible, 'visible', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is not visible"
            )

    @run_on_failure
    def element_should_not_be_visible(self, locator, timeout=None,
                                       message=None):
        """Asserts that no visible element matches the locator.

        Auto-waits up to ``timeout`` for any matching visible element to
        disappear.

        Example:
        | Element Should Not Be Visible | text=Spinner |
        """
        try:
            self._resolve_absent_or_hidden(locator, timeout)
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is visible but should not be"
            )

    @run_on_failure
    def element_should_be_enabled(self, locator, index='first',
                                   timeout=None, message=None):
        """Asserts that the element is enabled. Auto-waits.

        Example:
        | Element Should Be Enabled | testid=submit-btn |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.enabled, 'enabled', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is not enabled"
            )

    @run_on_failure
    def element_should_be_disabled(self, locator, index='first',
                                    timeout=None, message=None):
        """Asserts that the element is disabled. Auto-waits.

        Example:
        | Element Should Be Disabled | testid=submit-btn |
        """
        try:
            self._resolve_state(
                locator, lambda n: not n.enabled, 'disabled', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is enabled but should be disabled"
            )

    @run_on_failure
    def element_should_be_selected(self, locator, index='first',
                                    timeout=None, message=None):
        """Asserts that the element is selected. Auto-waits.

        Example:
        | Element Should Be Selected | testid=checkbox |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.selected, 'selected', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is not selected"
            )

    @run_on_failure
    def element_should_be_focused(self, locator, index='first',
                                   timeout=None, message=None):
        """Asserts that the element is focused. Auto-waits.

        Example:
        | Element Should Be Focused | testid=input |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.focused, 'focused', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is not focused"
            )

    @run_on_failure
    def element_should_be_checked(self, locator, index='first',
                                   timeout=None, message=None):
        """Asserts that the element is checked. Auto-waits.

        Example:
        | Element Should Be Checked | testid=toggle |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.checked, 'checked', index, timeout,
            )
        except MobileWrightTimeoutError:
            raise AssertionError(
                message or f"Element '{locator}' is not checked"
            )

    @run_on_failure
    def element_text_should_be(self, locator, expected, index='first',
                                timeout=None, message=None):
        """Asserts that the element's text matches exactly. Auto-waits.

        Example:
        | Element Text Should Be | testid=title | Welcome Home |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.text == expected,
                f"text == '{expected}'", index, timeout,
            )
        except MobileWrightTimeoutError:
            actual = ''
            try:
                actual = self._find_element(locator, index).text
            except Exception:
                pass
            raise AssertionError(
                message or
                f"Element '{locator}' text was '{actual}', expected '{expected}'"
            )

    @run_on_failure
    def element_text_should_contain(self, locator, expected, index='first',
                                     timeout=None, message=None):
        """Asserts that the element's text contains the expected substring.
        Auto-waits.

        Example:
        | Element Text Should Contain | role=heading | Welcome |
        """
        try:
            self._resolve_state(
                locator, lambda n: expected in (n.text or ''),
                f"text containing '{expected}'", index, timeout,
            )
        except MobileWrightTimeoutError:
            actual = ''
            try:
                actual = self._find_element(locator, index).text
            except Exception:
                pass
            raise AssertionError(
                message or
                f"Element '{locator}' text '{actual}' does not contain '{expected}'"
            )
