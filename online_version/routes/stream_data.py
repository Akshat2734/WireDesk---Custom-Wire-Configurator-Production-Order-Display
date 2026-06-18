from flask import Flask, Blueprint
from online_version.model.order_sql import OutboxDB
from flask_socketio import send
from online_version.extension.socket_io import socketio
from online_version.extension.sqlmodel import db
from sqlalchemy import select, delete

stream_data = Blueprint("stream_data", __name__)

@stream_data.route("/stream_data", methods = ["POST"])
def streaming():
    result = db.session.execute(
                select(OutboxDB)
                .where(OutboxDB.status == "pending")
                .order_by(OutboxDB.timeline)
            )
    events = result.scalars().all()
    if events:
        try:
            for event in events:
                socketio.emit(
                    "json",
                    event.to_dict(),
                    to=f"admin_{event.admin_id}"
                )
                event.status = "processed"
            db.session.execute(
                delete(OutboxDB)
                .where(OutboxDB.status == "processed")
            )
            db.session.commit()
        except Exception:
            raise
    return {"message": "Events streamed"}, 200