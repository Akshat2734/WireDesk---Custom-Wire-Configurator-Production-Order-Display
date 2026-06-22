from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from werkzeug.security import check_password_hash, generate_password_hash

from server.extension.sqlmodel import db
from server.model.order_sql import User


class Register(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        if not all((email, username, password)):
            return {"error": "email, username and password are required"}, 400
        if User.query.filter(
            (User.email == email) | (User.username == username)
        ).first():
            return {"error": "User already exists"}, 409

        user = User(
            email=email,
            username=username,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered"}, 201


class SignIn(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        if not email or not username:
            return {"error": "email and username are required"}, 400

        user = User.query.filter_by(email=email, username=username).first()
        if user is None:
            return {"error": "Account not found"}, 401
        if password:
            if not check_password_hash(user.password, password):
                return {"error": "Invalid credentials"}, 401
            role = "admin"
        else:
            role = "view"

        token = create_access_token(
            identity=str(user.id), additional_claims={"role": role}
        )
        return {"access_token": token, "role": role}
