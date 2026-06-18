from flask_socketio import SocketIO
import os

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

socketio = SocketIO(cors_allowed_origins="*", message_queue=redis_url)