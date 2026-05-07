from robot.api import logger

from ..rpc.protocol import MobileWrightTimeoutError
from ._runonfailure import run_on_failure


class _Waiting:
    """Explicit waits.

    Note: most users do not need these — every interaction keyword
    (``Tap Element``, ``Fill Element``, etc.) and assertion keyword
    (``Element Should Be Visible``, etc.) already auto-waits. These
    explicit-wait keywords are kept for the cases where you need to
    pause flow until a specific condition is met without performing an
    action, and for parity with AppiumLibrary / SeleniumLibrary idioms.
    """

    @run_on_failure
    def wait_until_element_is_visible(self, locator, timeout=None, message=None):
        """Waits until an element matching the locator is visible.

        Example:
        | Wait Until Element Is Visible | text=Welcome | timeout=10s |
        """
        try:
            self._resolve_visible(locator, timeout=timeout)
            logger.info(f"Element visible: {locator}")
        except MobileWrightTimeoutError as e:
            raise AssertionError(message or str(e))

    @run_on_failure
    def wait_until_element_is_not_visible(self, locator, timeout=None, message=None):
        """Waits until no visible element matches the locator.

        Example:
        | Wait Until Element Is Not Visible | text=Loading | timeout=15s |
        """
        try:
            self._resolve_absent_or_hidden(locator, timeout=timeout)
            logger.info(f"Element no longer visible: {locator}")
        except MobileWrightTimeoutError as e:
            raise AssertionError(message or str(e))

    @run_on_failure
    def wait_until_element_is_enabled(self, locator, timeout=None, message=None):
        """Waits until an element matching the locator is enabled.

        Example:
        | Wait Until Element Is Enabled | testid=submit-btn | timeout=5s |
        """
        try:
            self._resolve_state(
                locator, lambda n: n.enabled, 'enabled', timeout=timeout,
            )
            logger.info(f"Element enabled: {locator}")
        except MobileWrightTimeoutError as e:
            raise AssertionError(message or str(e))

    @run_on_failure
    def wait_for_element_state(self, locator, state, timeout=None, message=None):
        """Waits until an element reaches the specified state.

        ``state`` is one of: ``visible``, ``hidden``, ``enabled``, ``disabled``.

        Example:
        | Wait For Element State | testid=panel | visible | timeout=10s |
        | Wait For Element State | text=Spinner | hidden | timeout=30s |
        """
        normalized = state.lower().strip()
        try:
            if normalized == 'visible':
                self._resolve_visible(locator, timeout=timeout)
            elif normalized == 'hidden':
                self._resolve_absent_or_hidden(locator, timeout=timeout)
            elif normalized == 'enabled':
                self._resolve_state(
                    locator, lambda n: n.enabled, 'enabled', timeout=timeout,
                )
            elif normalized == 'disabled':
                self._resolve_state(
                    locator, lambda n: not n.enabled, 'disabled', timeout=timeout,
                )
            else:
                raise ValueError(
                    f"Invalid state '{state}'. Expected: "
                    f"visible, hidden, enabled, disabled"
                )
            logger.info(f"Element reached state '{normalized}': {locator}")
        except MobileWrightTimeoutError as e:
            raise AssertionError(message or str(e))
