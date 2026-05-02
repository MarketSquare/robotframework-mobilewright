import json
import threading

import websocket

from .protocol import (
    MobileWrightConnectionError,
    MobileWrightRpcError,
    MobileWrightTimeoutError,
)


class MobileWrightRpcClient:

    def __init__(self):
        self._ws = None
        self._request_id = 0
        self._lock = threading.Lock()
        self._url = None
        self._timeout = 10.0

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self._ws.connected

    def connect(self, url: str, timeout: float = 10.0):
        if self._ws and self._ws.connected:
            self.disconnect()
        self._url = url
        self._timeout = timeout
        try:
            self._ws = websocket.WebSocket()
            self._ws.settimeout(timeout)
            self._ws.connect(url)
        except (websocket.WebSocketException, ConnectionError, OSError) as e:
            self._ws = None
            raise MobileWrightConnectionError(
                f"Failed to connect to MobileWright server at {url}: {e}"
            ) from e

    def disconnect(self):
        if self._ws:
            try:
                self._ws.close()
            except websocket.WebSocketException:
                pass
            finally:
                self._ws = None

    def call(self, method: str, timeout: float = None, **params):
        if not self.is_connected:
            raise MobileWrightConnectionError(
                "Not connected to MobileWright server. Call 'Connect To Device' first."
            )
        with self._lock:
            self._request_id += 1
            request_id = self._request_id

        request = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params if params else {},
            'id': request_id,
        }

        effective_timeout = timeout if timeout is not None else self._timeout
        try:
            self._ws.settimeout(effective_timeout)
            self._ws.send(json.dumps(request))
            raw = self._ws.recv()
        except websocket.WebSocketTimeoutException as e:
            raise MobileWrightTimeoutError(
                f"RPC call '{method}' timed out after {effective_timeout}s"
            ) from e
        except websocket.WebSocketException as e:
            self._ws = None
            raise MobileWrightConnectionError(
                f"Connection lost during RPC call '{method}': {e}"
            ) from e

        try:
            response = json.loads(raw)
        except json.JSONDecodeError as e:
            raise MobileWrightRpcError(
                f"Invalid JSON response from server: {raw[:200]}"
            ) from e

        if 'error' in response:
            err = response['error']
            raise MobileWrightRpcError(
                message=err.get('message', 'Unknown RPC error'),
                code=err.get('code', -1),
                data=err.get('data'),
            )

        return response.get('result')
