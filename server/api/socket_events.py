from server.extension.socket_io import socketio


@socketio.on("request_refresh")
def request_refresh():
    socketio.emit("orders_updated", {"reason": "client_refresh"})
