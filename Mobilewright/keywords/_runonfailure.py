import functools
import traceback

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


class _RunOnFailure:

    def __init__(self):
        self._run_on_failure_keyword = 'Capture Screenshot'
        self._running_on_failure = False

    def register_keyword_to_run_on_failure(self, keyword):
        """Sets the keyword to execute when a Mobilewright keyword fails.

        ``keyword`` is the name of the keyword to run on failure. Use ``None``
        or ``NONE`` to disable this feature.

        Returns the previously registered keyword.
        """
        old = self._run_on_failure_keyword
        self._run_on_failure_keyword = (
            None if keyword and keyword.upper() == 'NONE' else keyword
        )
        return old

    def _run_on_failure(self):
        if self._run_on_failure_keyword is None:
            return
        if self._running_on_failure:
            return
        self._running_on_failure = True
        try:
            BuiltIn().run_keyword(self._run_on_failure_keyword)
        except Exception:
            logger.warn(
                f"Run-on-failure keyword '{self._run_on_failure_keyword}' "
                f"failed:\n{traceback.format_exc()}"
            )
        finally:
            self._running_on_failure = False


def run_on_failure(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception:
            try:
                self._run_on_failure()
            except Exception:
                pass
            raise
    return wrapper
