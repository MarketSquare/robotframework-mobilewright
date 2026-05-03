from robot.api import logger

from ..rpc.client import MobileWrightRpcClient
from ..rpc.protocol import DeviceInfo, Session
from ..utils.type_converters import to_seconds
from ._runonfailure import run_on_failure


class _Connection:

    @run_on_failure
    def connect_to_device(
        self, server_url=None, alias=None, platform=None,
        device_id=None, timeout=None,
    ):
        """Connects to a MobileWright mobilecli server.

        ``server_url`` is the WebSocket URL (default from library import).
        ``alias`` is an optional name for this connection.
        ``platform`` is ``ios`` or ``android`` (auto-detected if omitted).
        ``device_id`` is the specific device ID to connect to.
        ``timeout`` overrides the default timeout for this connection.

        Returns the connection index.

        Example:
        | ${index}= | Connect To Device | server_url=ws://localhost:9100 | alias=mydevice |
        """
        url = server_url or self._server_url
        effective_timeout = to_seconds(timeout) if timeout else self._timeout

        client = MobileWrightRpcClient()
        client.connect(url, timeout=effective_timeout)

        connect_params = {}
        if platform:
            connect_params['platform'] = platform
        if device_id:
            connect_params['deviceId'] = device_id

        result = client.call('connect', **connect_params)
        session = Session.from_dict(result) if result else None

        index = self._cache.register(client, alias)
        logger.info(
            f"Connected to MobileWright server at {url}"
            + (f" (device: {session.device_id})" if session else "")
        )
        return index

    @run_on_failure
    def disconnect_from_device(self):
        """Disconnects the current active device connection.

        Example:
        | Disconnect From Device |
        """
        client = self._cache.current
        try:
            client.call('disconnect')
        except Exception:
            pass
        self._cache.close_current()
        logger.info("Disconnected from device.")

    def close_all_connections(self):
        """Closes all open device connections.

        Typically used in suite teardown.

        Example:
        | Close All Connections |
        """
        self._cache.close_all()
        logger.info("All device connections closed.")

    def switch_device(self, index_or_alias):
        """Switches to a different connected device.

        ``index_or_alias`` is the connection index or alias.

        Example:
        | Switch Device | mydevice |
        """
        self._cache.switch(index_or_alias)
        logger.info(f"Switched to device connection: {index_or_alias}")

    @run_on_failure
    def list_devices(self):
        """Returns a list of available devices from the server.

        Each device is a dictionary with keys: id, name, platform, type, state, os_version.

        Example:
        | @{devices}= | List Devices |
        """
        result = self._cache.current.call('listDevices')
        devices = [DeviceInfo.from_dict(d) for d in (result or [])]
        for d in devices:
            logger.info(
                f"  {d.id} | {d.name} | {d.platform} | {d.type} | {d.state}"
            )
        return [vars(d) for d in devices]

    def set_mobilewright_timeout(self, timeout):
        """Sets the global timeout for MobileWright operations.

        ``timeout`` accepts Robot Framework time strings (e.g., ``10s``, ``1 min``).

        Returns the previous timeout value as a string.

        Example:
        | ${old}= | Set MobileWright Timeout | 15s |
        """
        old = self._timeout
        self._timeout = to_seconds(timeout)
        return f"{old}s"
