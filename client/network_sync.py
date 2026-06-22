import socketio
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class SyncManager(QObject):
    update_received = pyqtSignal()
    connection_changed = pyqtSignal(bool)
    connection_error = pyqtSignal(str)

    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.socket = socketio.Client(reconnection=True)
        self.socket.on("connect", self._connected)
        self.socket.on("disconnect", self._disconnected)
        self.socket.on("orders_updated", self._orders_updated)
        QTimer.singleShot(0, self.connect_to_server)

    def connect_to_server(self):
        if self.socket.connected:
            return
        try:
            self.socket.connect(self.api_client.base_url, transports=["websocket"])
        except socketio.exceptions.ConnectionError as exc:
            self.connection_error.emit(str(exc))

    def _connected(self):
        self.connection_changed.emit(True)

    def _disconnected(self):
        self.connection_changed.emit(False)

    def _orders_updated(self, _data=None):
        self.update_received.emit()

    def broadcast(self):
        if self.socket.connected:
            self.socket.emit("request_refresh")

    def close(self):
        if self.socket.connected:
            self.socket.disconnect()
