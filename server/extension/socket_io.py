from flask_socketio import SocketIO
import os

redis_url = os.environ.get("REDIS_URL")

socketio = SocketIO(cors_allowed_origins="*", message_queue=redis_url)
