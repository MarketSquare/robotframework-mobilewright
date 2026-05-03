from robot.utils import ConnectionCache

from ..rpc.client import MobileWrightRpcClient
from ..rpc.protocol import MobileWrightConnectionError


class DeviceConnectionCache:

    def __init__(self):
        self._cache = ConnectionCache('No device connections open.')
        self._current: MobileWrightRpcClient = None

    @property
    def current(self) -> MobileWrightRpcClient:
        if self._current is None:
            raise MobileWrightConnectionError(
                "No active device connection. Use 'Connect To Device' first."
            )
        return self._current

    def register(self, client: MobileWrightRpcClient, alias: str = None) -> int:
        index = self._cache.register(client, alias)
        self._current = client
        return index

    def switch(self, index_or_alias):
        self._current = self._cache.switch(index_or_alias)
        return self._current

    def close_all(self):
        connections = self._cache.close_all(closer_method='disconnect')
        self._current = None
        return connections

    def close_current(self):
        if self._current is not None:
            self._current.disconnect()
            self._current = None
