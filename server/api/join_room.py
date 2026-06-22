from server.extension.socket_io import socketio
from flask_socketio import join_room, send

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['email']
    join_room(room)
    send(username+'has entered the room', to = room)