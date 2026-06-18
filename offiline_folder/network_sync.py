from PyQt6.QtNetwork import QUdpSocket, QHostAddress
from PyQt6.QtCore import QObject, pyqtSignal


class SyncManager(QObject):

    update_received = pyqtSignal()

    def __init__(self, port=5555):
        super().__init__()

        self.port = port
        self.socket = QUdpSocket(self)

        self.socket.bind(
            self.port,
            QUdpSocket.BindFlag.ShareAddress |
            QUdpSocket.BindFlag.ReuseAddressHint
        )

        self.socket.readyRead.connect(self.receive_message)

    def receive_message(self):
        while self.socket.hasPendingDatagrams():
            data, host, port = self.socket.readDatagram(
                self.socket.pendingDatagramSize()
            )
            if data == b"DB_UPDATED":
                self.update_received.emit()

    def broadcast(self):
        self.socket.writeDatagram(
            b"DB_UPDATED",
            QHostAddress.SpecialAddress.Broadcast,
            self.port
        )