from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from server.extension.sqlmodel import db
from server.model.order_sql import AnalyticsDB, OrdersDB, OutboxDB


ORDER_FIELDS = (
    "wire_type", "variant", "material", "nominal_area_sqmm", "number_of_cores",
    "conductor_class", "nominal_insulation_ti_mm", "nominal_sheath_ts_mm",
    "max_width_mm", "max_height_mm", "max_overall_diameter_mm",
    "max_twisted_diameter_mm", "recommended_core_layup", "strand_diameter_mm",
    "tolerance_percent", "number_of_strands_per_core", "number_of_strands",
    "insulation_percent", "inner_layer_percent", "outer_layer_percent",
    "bedding_percent", "sheath_percent", "length_meters",
)

ANALYTICS_FIELDS = (
    "wire_type", "table_ref", "conductor_class", "variant", "material",
    "conductor_weight_kg", "aluminium_weight_kg", "copper_rate_per_kg",
    "metal_rate_per_kg", "pvc_rate_per_kg", "pvc_weight_kg",
    "weight_per_meter_kg", "cost_per_meter", "total_cost", "length_meters",
)


def _select_fields(data, fields):
    return {field: data.get(field) for field in fields}


def save_order(data, user_id):
    existing = OrdersDB.query.filter_by(
        idempotency_key=data["idempotency_key"]
    ).first()
    if existing:
        return existing.to_dict(), None

    order = OrdersDB(
        user_id=user_id,
        order_id=data["order_id"],
        idempotency_key=data["idempotency_key"],
        **_select_fields(data, ORDER_FIELDS),
    )
    analytics = AnalyticsDB(
        user_id=user_id,
        order_id=data["order_id"],
        idempotency_key=data["idempotency_key"],
        **_select_fields(data, ANALYTICS_FIELDS),
    )
    event = OutboxDB(
        user_id=user_id,
        event_id=str(uuid4()),
        order_id=data["order_id"],
        event_type="order.created",
        payload={"order_id": data["order_id"]},
    )

    try:
        db.session.add_all((order, analytics, event))
        db.session.commit()
        return order.to_dict(), event
    except IntegrityError:
        db.session.rollback()
        existing = OrdersDB.query.filter_by(
            idempotency_key=data["idempotency_key"]
        ).first()
        if existing:
            return existing.to_dict(), None
        raise


def update_order_status(order_id, status, user_id):
    order = OrdersDB.query.filter_by(order_id=order_id).first()
    analytics = AnalyticsDB.query.filter_by(order_id=order_id).first()
    if order is None:
        return None, None

    order.status = status
    if analytics is not None:
        analytics.status = status
    event = OutboxDB(
        user_id=user_id,
        event_id=str(uuid4()),
        order_id=order_id,
        event_type="order.status_changed",
        payload={"order_id": order_id, "status": status},
    )
    db.session.add(event)
    db.session.commit()
    return order.to_dict(), event
