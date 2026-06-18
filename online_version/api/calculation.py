from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from online_version.utils.role_required import role_required
from online_version.controller.calculation_file import CalculationEngine

#Name that will act as app.route and will be used in app.py
calculation_api_for_engine = Blueprint("calculation_api_for_engine", __name__)

#Requires access token as well as admin role for using this function present in the route, api will be used to tranfer input from ui
#inputs as well as product data as well as formula is passed to the function, will use database for this
#the data will then be tranferred to Calculation engine and result as well as previus data will be returned
@calculation_api_for_engine.route('/calculation', methods = ['GET'])
@jwt_required()
@role_required('admin')
def calculation():
    data = {'inputs': {'core_thickness': '100'}}
    product_json_defination = {"constants": {"copper_density": 8.96},
        "calculated": {"total_weight": "copper_density * core_thickness"}}
    user_inputs = data.get("inputs", {})
    engine = CalculationEngine(product_json_defination)
    try:
        results = engine.calculate(user_inputs)
        return jsonify({"status": "success", "calculation": results}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400    