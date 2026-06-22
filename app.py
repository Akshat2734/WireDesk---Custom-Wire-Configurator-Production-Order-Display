"""Compatibility WSGI entry point; production uses server.app directly."""

from server.app import create_app
from server.extension.socket_io import socketio


app = create_app()


if __name__ == "__main__":
    socketio.run(app, debug=app.debug)
