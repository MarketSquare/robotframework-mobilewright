from robot.api import logger

from ..rpc.protocol import AppInfo
from ._runonfailure import run_on_failure


class _Application:

    @run_on_failure
    def launch_app(self, bundle_id):
        """Launches an application by its bundle ID.

        ``bundle_id`` is the application identifier (e.g., ``com.example.app``).

        Example:
        | Launch App | com.example.myapp |
        """
        self._cache.current.call('device.apps.launch', bundleId=bundle_id)
        logger.info(f"Launched app: {bundle_id}")

    @run_on_failure
    def terminate_app(self, bundle_id):
        """Terminates a running application.

        Example:
        | Terminate App | com.example.myapp |
        """
        self._cache.current.call('device.apps.terminate', bundleId=bundle_id)
        logger.info(f"Terminated app: {bundle_id}")

    @run_on_failure
    def install_app(self, app_path):
        """Installs an application from the given path.

        ``app_path`` is the path to the .apk (Android) or .ipa/.zip (iOS).

        Example:
        | Install App | /path/to/app.apk |
        """
        self._cache.current.call('device.apps.install', path=app_path)
        logger.info(f"Installed app from: {app_path}")

    @run_on_failure
    def uninstall_app(self, bundle_id):
        """Uninstalls an application by its bundle ID.

        Example:
        | Uninstall App | com.example.myapp |
        """
        self._cache.current.call('device.apps.uninstall', bundleId=bundle_id)
        logger.info(f"Uninstalled app: {bundle_id}")

    @run_on_failure
    def list_apps(self):
        """Returns a list of installed applications.

        Each app is a dictionary with keys: bundle_id, name, version.

        Example:
        | @{apps}= | List Apps |
        """
        result = self._cache.current.call('device.apps.list')
        raw = result if isinstance(result, list) else (result or {}).get('apps', [])
        apps = [AppInfo.from_dict(a) for a in raw]
        return [vars(a) for a in apps]

    @run_on_failure
    def get_foreground_app(self):
        """Returns information about the currently active (foreground) application.

        Example:
        | ${app}= | Get Foreground App |
        | Log | Current app: ${app}[bundle_id] |
        """
        result = self._cache.current.call('device.apps.foreground')
        app = AppInfo.from_dict(result) if result else None
        return vars(app) if app else {}
