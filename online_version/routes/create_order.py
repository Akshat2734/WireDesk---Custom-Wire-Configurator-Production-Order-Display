from flask import jsonify
from flask import Blueprint, request
from online_version.utils.role_required import role_required
from online_version.model.order_sql import db, OrdersDB
from flask_jwt_extended import jwt_required, get_jwt_identity
from online_version.controller.save_view_order import save_order, view_order
from sqlalchemy.exc import OperationalError

create_order = Blueprint("create_order", __name__)

@create_order.route("/create_order", methods = ['POST'])
@jwt_required()
@role_required('admin')
def create_order():   
    #in overlay create a uuid for idempotency key
    data = request.get_json()
    save_order(data)
    #in frontend first join the user to room through email
    view_order(data)
    
    
@create_order.route('/view_orders', methods=['GET'])
def get_orders():
    # Use .with_engine() to target the replica bind
    engine = db.engines['replica']
    with engine.connect() as conn:
        result = conn.execute(db.select(OrdersDB)).fetchall()
    
    return jsonify([row._asdict() for row in result])
def get_orders_with_failover():
    try:
        # Attempt to read from the Replica
        engine = db.engines['replica']
        with engine.connect() as conn:
            result = conn.execute(db.select(OrdersDB)).fetchall()
            return result
            
    except OperationalError:
        print("WARNING: Replica offline. Falling back to Primary node.")
        
        # db.engine is the default Primary connection
        with db.engine.connect() as conn:
            result = conn.execute(db.select(OrdersDB)).fetchall()
            return result