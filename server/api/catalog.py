from flask import Blueprint, jsonify
from server.utils.role_required import role_required
from flask_jwt_extended import jwt_required

CATALOG_DATA = [
    {"id": "3_core_flat", "name": "3 Core Flat Submersible Cable"},
    {"id": "house_wire", "name": "House Wire"}
]

#Name that will act as app.route and will be used in app.py
catalog_wire_types = Blueprint("catalog_wire_types", __name__)

#Requires access token as well as admin role for using this function present in the route, api will be used to tranfer data from db to ui for user to select the wire type
@catalog_wire_types.route("/catalog", methods = ['GET'])
@jwt_required()
@role_required('admin')
def view_wire():
    return jsonify({"catalog":CATALOG_DATA})