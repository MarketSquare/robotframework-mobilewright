from robot.api import logger

from ..utils.type_converters import to_orientation
from ._runonfailure import run_on_failure


class _Orientation:

    @run_on_failure
    def get_orientation(self):
        """Returns the current device orientation.

        Returns ``portrait`` or ``landscape``.

        Example:
        | ${orientation}= | Get Orientation |
        """
        result = self._cache.current.call('device.io.orientation.get')
        if isinstance(result, str):
            orientation = result
        elif isinstance(result, dict):
            orientation = result.get('orientation', '')
        else:
            orientation = ''
        logger.info(f"Current orientation: {orientation}")
        return orientation

    @run_on_failure
    def set_orientation(self, orientation):
        """Sets the device orientation.

        ``orientation`` is ``portrait`` or ``landscape``.

        Example:
        | Set Orientation | landscape |
        | Set Orientation | portrait |
        """
        o = to_orientation(orientation)
        self._cache.current.call('device.io.orientation.set', orientation=o.value)
        logger.info(f"Set orientation to: {o.value}")
