from flask import Blueprint
from flask_jwt_extended import jwt_required
from sqlalchemy import select

from server.extension.socket_io import socketio
from server.extension.sqlmodel import db
from server.model.order_sql import OutboxDB
from server.utils.role_required import role_required


stream_data = Blueprint("stream_data", __name__)


@stream_data.post("/stream_data")
@jwt_required()
@role_required("admin")
def streaming():
    events = db.session.execute(
        select(OutboxDB)
        .where(OutboxDB.status == "pending")
        .order_by(OutboxDB.timestamp)
    ).scalars().all()

    for event in events:
        socketio.emit("orders_updated", event.payload)
        event.status = "processed"
    db.session.commit()
    return {"message": "Events streamed", "count": len(events)}, 200
