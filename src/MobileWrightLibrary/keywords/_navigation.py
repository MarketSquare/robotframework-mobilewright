from robot.api import logger

from ._runonfailure import run_on_failure


class _Navigation:

    @run_on_failure
    def open_url(self, url):
        """Opens a URL on the device.

        Example:
        | Open Url | https://example.com |
        """
        self._cache.current.call('openUrl', url=url)
        logger.info(f"Opened URL: {url}")

    @run_on_failure
    def go_to_url(self, url):
        """Opens a URL on the device. Alias for ``Open Url``.

        Example:
        | Go To Url | https://example.com |
        """
        self.open_url(url)
