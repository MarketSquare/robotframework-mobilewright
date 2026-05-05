import json
import socket
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
        self._url = None
        self._timeout = 10.0
        self._device_id = None
        self._request_id = 0
        self._lock = threading.Lock()
        self._auto_reconnect = True

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and self._ws.connected

    @property
    def device_id(self):
        return self._device_id

    def set_device_id(self, device_id):
        self._device_id = device_id

    @staticmethod
    def _to_ws_url(url: str) -> str:
        url = url.rstrip('/')
        if url.startswith('http://'):
            url = 'ws://' + url[len('http://'):]
        elif url.startswith('https://'):
            url = 'wss://' + url[len('https://'):]
        elif not (url.startswith('ws://') or url.startswith('wss://')):
            url = 'ws://' + url
        if not url.endswith('/ws'):
            url = url + '/ws'
        return url

    def connect(self, url: str, timeout: float = 10.0):
        ws_url = self._to_ws_url(url)
        self._url = ws_url
        self._timeout = timeout
        try:
            self._ws = websocket.WebSocket()
            self._ws.settimeout(timeout)
            self._ws.connect(ws_url)
        except (websocket.WebSocketException, ConnectionError, OSError) as e:
            self._ws = None
            raise MobileWrightConnectionError(
                f"Failed to connect to mobilecli WebSocket at {ws_url}: {e}"
            ) from e

    def disconnect(self):
        self._drop_connection()
        self._url = None
        self._device_id = None

    def _drop_connection(self):
        if self._ws:
            try:
                self._ws.close()
            except (websocket.WebSocketException, OSError):
                pass
            finally:
                self._ws = None

    def _ensure_connected(self):
        if self.is_connected:
            return
        if self._auto_reconnect and self._url:
            saved_device = self._device_id
            try:
                self.connect(self._url, self._timeout)
            except MobileWrightConnectionError:
                raise
            self._device_id = saved_device
            return
        raise MobileWrightConnectionError(
            "Not connected to mobilecli server. Call 'Connect To Device' first."
        )

    def call(self, method, _omit_device_id=False, timeout=None, **params):
        last_conn_error = None
        for attempt in range(2):
            try:
                return self._do_call(method, _omit_device_id, timeout, **params)
            except MobileWrightConnectionError as e:
                last_conn_error = e
                if attempt == 0 and self._auto_reconnect and self._url:
                    continue
                raise
        raise last_conn_error

    def _do_call(self, method, _omit_device_id, timeout, **params):
        self._ensure_connected()

        with self._lock:
            self._request_id += 1
            request_id = self._request_id

            if not _omit_device_id and self._device_id and 'deviceId' not in params:
                params['deviceId'] = self._device_id

            request = {
                'jsonrpc': '2.0',
                'method': method,
                'params': params,
                'id': request_id,
            }

            effective_timeout = timeout if timeout is not None else self._timeout
            try:
                self._ws.settimeout(effective_timeout)
                self._ws.send(json.dumps(request))
                raw = self._ws.recv()
            except (websocket.WebSocketTimeoutException, socket.timeout, TimeoutError) as e:
                self._drop_connection()
                raise MobileWrightTimeoutError(
                    f"RPC call '{method}' timed out after {effective_timeout}s"
                ) from e
            except (websocket.WebSocketException, OSError, ConnectionError) as e:
                self._drop_connection()
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
            msg = err.get('message', 'Unknown RPC error')
            data = err.get('data')
            if data:
                msg = f"{msg}: {data}"
            raise MobileWrightRpcError(
                message=msg,
                code=err.get('code', -1),
                data=data,
            )

        return response.get('result')
