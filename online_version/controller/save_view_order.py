from sqlalchemy.exc import IntegrityError
from online_version.model.order_sql import AnalyticsDB, OrdersDB, OutboxDB
from online_version.extension.sqlmodel import db

def save_order(value, user):
    search_key = OrdersDB.query.filter_by(
        idempotency_key = value.get("idempotency_key")
    ).first()
    if search_key:
        return {
            'message': 'Order already exists',
            "order_id": search_key.order_id
        }
    else:
        order = OrdersDB(
            user_id = user,
            order_id=value.get("order_id"),
            idempotency_key=value.get("idempotency_key"),
            wire_type=value.get("wire_type"),
            variant=value.get("variant"),
            material=value.get("material"),
            nominal_area_sqmm=value.get("nominal_area_sqmm"),
            number_of_cores=value.get("number_of_cores"),
            conductor_class=value.get("conductor_class"),
            nominal_insulation_ti_mm=value.get("nominal_insulation_ti_mm"),
            nominal_sheath_ts_mm=value.get("nominal_sheath_ts_mm"),
            max_width_mm=value.get("max_width_mm"),
            max_height_mm=value.get("max_height_mm"),
            max_overall_diameter_mm=value.get("max_overall_diameter_mm"),
            max_twisted_diameter_mm=value.get("max_twisted_diameter_mm"),
            recommended_core_layup=value.get("recommended_core_layup"),
            strand_diameter_mm=value.get("strand_diameter_mm"),
            tolerance_percent=value.get("tolerance_percent"),
            number_of_strands_per_core=value.get("number_of_strands_per_core"),
            number_of_strands=value.get("number_of_strands"),
            insulation_percent=value.get("insulation_percent"),
            inner_layer_percent=value.get("inner_layer_percent"),
            outer_layer_percent=value.get("outer_layer_percent"),
            bedding_percent=value.get("bedding_percent"),
            sheath_percent=value.get("sheath_percent"),
            length_meters=value.get("length_meters")
        )

        analytics = AnalyticsDB(
            user_id = user,
            order_id=value.get("order_id"),
            idempotency_key=value.get("idempotency_key"),
            wire_type=value.get("wire_type"),
            table_ref=value.get("table_ref"),
            conductor_class=value.get("conductor_class"),
            variant=value.get("variant"),
            material=value.get("material"),
            conductor_weight_kg=value.get("conductor_weight_kg"),
            aluminium_weight_kg=value.get("aluminium_weight_kg"),
            copper_rate_per_kg=value.get("copper_rate_per_kg"),
            metal_rate_per_kg=value.get("metal_rate_per_kg"),
            pvc_rate_per_kg=value.get("pvc_rate_per_kg"),
            pvc_weight_kg=value.get("pvc_weight_kg"),
            weight_per_meter_kg=value.get("weight_per_meter_kg"),
            cost_per_meter=value.get("cost_per_meter"),
            total_cost=value.get("total_cost"),
            length_meters=value.get("length_meters")
        )
        try:
            db.session.add(order)
            db.session.add(analytics)
            db.session.commit()
            return {
                "order_id": order.order_id,
                "idempotency_key": order.idempotency_key
            }
        except IntegrityError:
            db.session.rollback()
            # Another request may have inserted the same key
            existing = OrdersDB.query.filter_by(
                idempotency_key=value.get("idempotency_key")
            ).first()
            if existing:
                return {
                    "message": "Order already exists",
                    "order_id": existing.order_id,
                    "idempotency_key": existing.idempotency_key
                }
            raise
        except Exception:
            db.session.rollback()
            raise
        
        
#another function that saves the info in outbox so that it can be used seperately
def view_order(value, user):
    search_key = OutboxDB.query.filter_by(
        idempotency_key = value.get("idempotency_key")
    ).first()
    if search_key:
        return {
            'message': 'Order already exists',
            "order_id": search_key.order_id
        }
    else:
        vieworder = OutboxDB(
            user_id = user,
            order_id=value.get("order_id"),
            idempotency_key=value.get("idempotency_key"),
            wire_type=value.get("wire_type"),
            variant=value.get("variant"),
            material=value.get("material"),
            nominal_area_sqmm=value.get("nominal_area_sqmm"),
            number_of_cores=value.get("number_of_cores"),
            conductor_class=value.get("conductor_class"),
            nominal_insulation_ti_mm=value.get("nominal_insulation_ti_mm"),
            nominal_sheath_ts_mm=value.get("nominal_sheath_ts_mm"),
            max_width_mm=value.get("max_width_mm"),
            max_height_mm=value.get("max_height_mm"),
            max_overall_diameter_mm=value.get("max_overall_diameter_mm"),
            max_twisted_diameter_mm=value.get("max_twisted_diameter_mm"),
            recommended_core_layup=value.get("recommended_core_layup"),
            strand_diameter_mm=value.get("strand_diameter_mm"),
            tolerance_percent=value.get("tolerance_percent"),
            number_of_strands_per_core=value.get("number_of_strands_per_core"),
            number_of_strands=value.get("number_of_strands"),
            insulation_percent=value.get("insulation_percent"),
            inner_layer_percent=value.get("inner_layer_percent"),
            outer_layer_percent=value.get("outer_layer_percent"),
            bedding_percent=value.get("bedding_percent"),
            sheath_percent=value.get("sheath_percent"),
            length_meters=value.get("length_meters")
        )
    try:
        db.session.add(vieworder)
        db.session.commit()
        return {
            "order_id": vieworder.order_id,
            "idempotency_key": vieworder.idempotency_key
        }
    except IntegrityError:
            db.session.rollback()
            # Another request may have inserted the same key
            existing = OrdersDB.query.filter_by(
                idempotency_key=value.get("idempotency_key")
            ).first()
            if existing:
                return {
                    "message": "Order already exists",
                    "order_id": existing.order_id,
                    "idempotency_key": existing.idempotency_key
                }
            raise
    except Exception:
            db.session.rollback()
            raise