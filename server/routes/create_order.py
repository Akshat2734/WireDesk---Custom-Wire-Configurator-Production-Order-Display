from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from server.controller.save_view_order import save_order, update_order_status
from server.extension.redis_cache import redis_cache
from server.extension.socket_io import socketio
from server.extension.sqlmodel import db
from server.model.order_sql import AnalyticsDB, OrdersDB
from server.utils.role_required import role_required


order_bp = Blueprint("order_bp", __name__)
VALID_STATUSES = {"preprocessing", "processing", "done"}
CACHE_KEYS = tuple(f"orders:v1:{status}" for status in (*VALID_STATUSES, "all"))


def require_idempotency_key(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if not request.headers.get("X-Idempotency-Key"):
            return jsonify({"error": "Missing X-Idempotency-Key header"}), 400
        return function(*args, **kwargs)
    return decorated


def _publish(event):
    if event is None:
        return
    socketio.emit("orders_updated", event.payload)
    event.status = "processed"
    db.session.commit()


def _read_orders(engine, status=None, user_id=None, user_role=None):
    statement = select(OrdersDB, AnalyticsDB).join(
        AnalyticsDB, AnalyticsDB.order_id == OrdersDB.order_id
    ).order_by(OrdersDB.timestamp.desc())
    
    if status:
        statement = statement.where(OrdersDB.status == status)
        
    if user_role != "view" and user_id:
        statement = statement.where(OrdersDB.user_id == user_id)
        
    with Session(engine) as session:
        rows = session.execute(statement).all()
        return [
            {**order.to_dict(), "analytics": analytics.to_dict()}
            for order, analytics in rows
        ]


def _orders_with_failover(status=None, user_id=None, user_role=None):
    try:
        replica = db.engines.get("replica")
        if replica is not None:
            return _read_orders(replica, status, user_id, user_role)
    except SQLAlchemyError:
        pass
    return _read_orders(db.engine, status, user_id, user_role)


@order_bp.post("/create_order")
@require_idempotency_key
@jwt_required()
@role_required("admin")
def create_order():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("order_id"):
        return jsonify({"error": "order_id and a JSON object are required"}), 400

    data["idempotency_key"] = request.headers["X-Idempotency-Key"]
    saved, event = save_order(data, int(get_jwt_identity()))
    redis_cache.delete(*CACHE_KEYS)
    _publish(event)
    return jsonify(saved), 201


@order_bp.get("/view_orders")
@jwt_required()
def get_orders():
    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return jsonify({"error": "Invalid order status"}), 400
    
    current_user_id = int(get_jwt_identity())
    user_role = get_jwt().get("role", "view")

    cache_key = f"orders:v1:{current_user_id}:{status or 'all'}"
    cached = redis_cache.get_json(cache_key)
    if cached is not None:
        return jsonify(cached)

    orders = _orders_with_failover(status, current_user_id, user_role)
    redis_cache.set_json(cache_key, orders)
    return jsonify(orders)


@order_bp.patch("/orders/<order_id>/status")
@jwt_required()
@role_required("admin")
def change_order_status(order_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in VALID_STATUSES:
        return jsonify({"error": "Invalid order status"}), 400

    saved, event = update_order_status(order_id, status, int(get_jwt_identity()))
    if saved is None:
        return jsonify({"error": "Order not found"}), 404
    redis_cache.delete(*CACHE_KEYS)
    _publish(event)
    return jsonify(saved)
