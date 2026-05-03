import os

from robot.api import logger

from .keywords._application import _Application
from .keywords._connection import _Connection
from .keywords._element import _Element
from .keywords._navigation import _Navigation
from .keywords._orientation import _Orientation
from .keywords._recording import _Recording
from .keywords._runonfailure import _RunOnFailure
from .keywords._screen import _Screen
from .keywords._waiting import _Waiting
from .utils.connection_cache import DeviceConnectionCache
from .utils.type_converters import to_seconds
from .version import VERSION


class MobileWrightLibrary(
    _Connection,
    _Application,
    _Screen,
    _Element,
    _Waiting,
    _Orientation,
    _Navigation,
    _Recording,
    _RunOnFailure,
):
    """MobileWrightLibrary is a Robot Framework library for mobile testing
    using the MobileWright framework.

    It communicates with a MobileWright mobilecli server via WebSocket JSON-RPC
    to automate iOS and Android devices.

    = Compatibility =

    Tested against MobileWright mobilecli server ``>= v0.0.30``.
    The library version follows its own SemVer cycle, independent of
    MobileWright upstream.

    = Locator Syntax =

    Elements are located using ``strategy=value`` syntax:

    | ``label=Submit``        | Accessibility label        |
    | ``testid=login-btn``    | Test ID / resource ID      |
    | ``text=Hello World``    | Text content               |
    | ``type=UIButton``       | Node type                  |
    | ``role=button``         | Accessibility role         |
    | ``placeholder=Search``  | Placeholder text           |

    Locators can be chained with ``>>`` to narrow scope:
    | ``type=ListView >> text=Item 1``  |

    = Index Selectors =

    When multiple elements match, use the ``index`` argument:
    | ``index=first``  | First match (default) |
    | ``index=last``   | Last match            |
    | ``index=2``      | Third match (0-based) |

    = Example =

    | ***** Settings *****
    | Library    MobileWrightLibrary    server_url=ws://localhost:9100
    |
    | ***** Test Cases *****
    | Login Test
    |     Connect To Device
    |     Launch App    com.example.myapp
    |     Fill Element    testid=username    admin
    |     Tap Element    label=Submit
    |     Wait Until Element Is Visible    text=Welcome
    """

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(
        self,
        server_url='ws://localhost:9100',
        timeout='10s',
        platform=None,
        run_on_failure='Capture Screenshot',
        screenshot_directory=None,
    ):
        _RunOnFailure.__init__(self)
        self._server_url = server_url
        self._timeout = to_seconds(timeout)
        self._platform = platform
        self._cache = DeviceConnectionCache()
        self._screenshot_dir = screenshot_directory or os.getcwd()
        self._screenshot_counter = 0

        if run_on_failure and run_on_failure.upper() != 'NONE':
            self._run_on_failure_keyword = run_on_failure
        else:
            self._run_on_failure_keyword = None
