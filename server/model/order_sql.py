from datetime import datetime
from typing import Any

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.extension.sqlmodel import db


class SerializableMixin:
    def to_dict(self):
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            result[column.name] = value.isoformat() if isinstance(value, datetime) else value
        return result


class User(SerializableMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column()
    orders = relationship("OrdersDB", back_populates="user")
    analytics = relationship("AnalyticsDB", back_populates="user")
    outbox = relationship("OutboxDB", back_populates="user")


class OrdersDB(SerializableMixin, db.Model):
    user = relationship("User", back_populates="orders")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(unique=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
    idempotency_key: Mapped[str] = mapped_column(unique=True)
    wire_type: Mapped[str | None]
    variant: Mapped[str | None]
    material: Mapped[str | None]
    nominal_area_sqmm: Mapped[float | None]
    number_of_cores: Mapped[int | None]
    conductor_class: Mapped[str | None]
    nominal_insulation_ti_mm: Mapped[float | None]
    nominal_sheath_ts_mm: Mapped[float | None]
    max_width_mm: Mapped[float | None]
    max_height_mm: Mapped[float | None]
    max_overall_diameter_mm: Mapped[float | None]
    max_twisted_diameter_mm: Mapped[float | None]
    recommended_core_layup: Mapped[float | None]
    strand_diameter_mm: Mapped[float | None]
    tolerance_percent: Mapped[float | None]
    number_of_strands_per_core: Mapped[int | None]
    number_of_strands: Mapped[int | None]
    insulation_percent: Mapped[float | None]
    inner_layer_percent: Mapped[float | None]
    outer_layer_percent: Mapped[float | None]
    bedding_percent: Mapped[float | None]
    sheath_percent: Mapped[float | None]
    length_meters: Mapped[int | None]
    status: Mapped[str] = mapped_column(default="preprocessing", index=True)


class AnalyticsDB(SerializableMixin, db.Model):
    user = relationship("User", back_populates="analytics")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
    idempotency_key: Mapped[str] = mapped_column(unique=True)
    wire_type: Mapped[str | None]
    table_ref: Mapped[str | None]
    conductor_class: Mapped[str | None]
    variant: Mapped[str | None]
    material: Mapped[str | None]
    conductor_weight_kg: Mapped[float | None]
    aluminium_weight_kg: Mapped[float | None]
    copper_rate_per_kg: Mapped[float | None]
    metal_rate_per_kg: Mapped[float | None]
    pvc_rate_per_kg: Mapped[float | None]
    pvc_weight_kg: Mapped[float | None]
    weight_per_meter_kg: Mapped[float | None]
    cost_per_meter: Mapped[float | None]
    total_cost: Mapped[float | None]
    length_meters: Mapped[int | None]
    status: Mapped[str] = mapped_column(default="preprocessing", index=True)


class OutboxDB(SerializableMixin, db.Model):
    user = relationship("User", back_populates="outbox")
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(unique=True)
    order_id: Mapped[str] = mapped_column(index=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now, index=True)
    event_type: Mapped[str]
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(default="pending", index=True)
