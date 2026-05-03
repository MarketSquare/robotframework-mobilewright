import time

from robot.api import logger

from ..locators import find_elements, parse_locator
from ..rpc.protocol import MobileWrightTimeoutError, ViewNode
from ..utils.type_converters import to_seconds
from ._runonfailure import run_on_failure

_POLL_INTERVAL = 0.5


class _Waiting:

    def _wait_until(self, condition_fn, locator, timeout, message, description):
        effective_timeout = to_seconds(timeout) if timeout else self._timeout
        end_time = time.monotonic() + effective_timeout
        locators = parse_locator(locator)

        while time.monotonic() < end_time:
            result = self._cache.current.call('getViewHierarchy')
            tree = [ViewNode.from_dict(n) for n in (result or [])]
            matches = find_elements(tree, locators)

            if condition_fn(matches):
                logger.info(f"Condition met: {description} for '{locator}'")
                return True

            remaining = end_time - time.monotonic()
            if remaining > 0:
                time.sleep(min(_POLL_INTERVAL, remaining))

        raise AssertionError(
            message or f"Timeout {effective_timeout}s: {description} "
                        f"not met for '{locator}'"
        )

    @run_on_failure
    def wait_until_element_is_visible(self, locator, timeout=None, message=None):
        """Waits until an element matching the locator is visible.

        ``timeout`` overrides the default timeout. Accepts RF time strings.

        Example:
        | Wait Until Element Is Visible | text=Welcome | timeout=10s |
        """
        self._wait_until(
            condition_fn=lambda matches: any(m.visible for m in matches),
            locator=locator,
            timeout=timeout,
            message=message,
            description='element visible',
        )

    @run_on_failure
    def wait_until_element_is_not_visible(self, locator, timeout=None, message=None):
        """Waits until no visible element matches the locator.

        Example:
        | Wait Until Element Is Not Visible | text=Loading... | timeout=15s |
        """
        self._wait_until(
            condition_fn=lambda matches: not any(m.visible for m in matches),
            locator=locator,
            timeout=timeout,
            message=message,
            description='element not visible',
        )

    @run_on_failure
    def wait_until_element_is_enabled(self, locator, timeout=None, message=None):
        """Waits until an element matching the locator is enabled.

        Example:
        | Wait Until Element Is Enabled | testid=submit-btn | timeout=5s |
        """
        self._wait_until(
            condition_fn=lambda matches: any(m.enabled for m in matches),
            locator=locator,
            timeout=timeout,
            message=message,
            description='element enabled',
        )

    @run_on_failure
    def wait_for_element_state(self, locator, state, timeout=None, message=None):
        """Waits until an element reaches the specified state.

        ``state`` is one of: ``visible``, ``hidden``, ``enabled``, ``disabled``.

        Example:
        | Wait For Element State | testid=panel | visible | timeout=10s |
        | Wait For Element State | text=Spinner | hidden | timeout=30s |
        """
        state = state.lower().strip()
        conditions = {
            'visible': lambda matches: any(m.visible for m in matches),
            'hidden': lambda matches: not any(m.visible for m in matches),
            'enabled': lambda matches: any(m.enabled for m in matches),
            'disabled': lambda matches: any(not m.enabled for m in matches),
        }
        if state not in conditions:
            raise ValueError(
                f"Invalid state '{state}'. Expected: visible, hidden, enabled, disabled"
            )
        self._wait_until(
            condition_fn=conditions[state],
            locator=locator,
            timeout=timeout,
            message=message,
            description=f'element {state}',
        )
