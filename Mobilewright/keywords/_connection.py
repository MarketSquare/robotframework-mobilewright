from robot.api import logger

from ..rpc.client import MobileWrightRpcClient
from ..rpc.protocol import DeviceInfo, MobileWrightConnectionError
from ..utils.type_converters import to_seconds
from ._runonfailure import run_on_failure


class _Connection:

    @run_on_failure
    def connect_to_device(
        self, server_url=None, alias=None, platform=None,
        device_id=None, timeout=None,
    ):
        """Connects to a mobilecli HTTP server and selects a device.

        ``server_url`` is the mobilecli HTTP URL (default ``http://localhost:12000``).
        ``alias`` is an optional name for this connection.
        ``platform`` is ``ios`` or ``android`` — used to filter devices
        when ``device_id`` is not specified.
        ``device_id`` is the specific device ID to use. When omitted, the
        first online device matching ``platform`` is selected.
        ``timeout`` overrides the default timeout for this connection.

        Returns the connection index.

        Example:
        | ${index}= | Connect To Device | server_url=http://localhost:12000 | alias=mydevice |
        | Connect To Device | platform=android |
        | Connect To Device | device_id=emulator-5554 |
        """
        url = server_url or self._server_url
        effective_timeout = to_seconds(timeout) if timeout else self._timeout

        client = MobileWrightRpcClient()
        client.connect(url, timeout=effective_timeout)

        if not device_id:
            result = client.call('devices.list', _omit_device_id=True)
            devices = (result or {}).get('devices', [])
            online = [d for d in devices if d.get('state', '').lower() == 'online']
            if platform:
                online = [
                    d for d in online
                    if d.get('platform', '').lower() == platform.lower()
                ]
            if not online:
                client.disconnect()
                raise MobileWrightConnectionError(
                    f"No online devices found"
                    + (f" for platform '{platform}'" if platform else "")
                    + ". Use 'List Devices' to see what's available."
                )
            device_id = online[0].get('id')
            logger.info(
                f"Auto-selected device: {device_id} "
                f"({online[0].get('name', '?')}, {online[0].get('platform', '?')})"
            )

        client.set_device_id(device_id)
        index = self._cache.register(client, alias)
        logger.info(f"Connected to mobilecli at {url} (device: {device_id})")
        return index

    @run_on_failure
    def disconnect_from_device(self):
        """Disconnects the current active device connection.

        Example:
        | Disconnect From Device |
        """
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
        result = self._cache.current.call('devices.list', _omit_device_id=True)
        raw_devices = (result or {}).get('devices', [])
        devices = [DeviceInfo.from_dict(d) for d in raw_devices]
        for d in devices:
            logger.info(
                f"  {d.id} | {d.name} | {d.platform} | {d.type} | {d.state}"
            )
        return [vars(d) for d in devices]

    @run_on_failure
    def get_device_info(self):
        """Returns info about the currently selected device.

        Returns a dict with keys depending on platform (id, name, platform,
        os version, screen size, etc.).

        Example:
        | ${info}= | Get Device Info |
        """
        return self._cache.current.call('device.info')

    def set_mobilewright_timeout(self, timeout):
        """Sets the global timeout for Mobilewright operations.

        ``timeout`` accepts Robot Framework time strings (e.g., ``10s``, ``1 min``).

        Returns the previous timeout value as a string.

        Example:
        | ${old}= | Set Mobilewright Timeout | 15s |
        """
        old = self._timeout
        self._timeout = to_seconds(timeout)
        return f"{old}s"
