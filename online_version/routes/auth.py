from flask import jsonify, request, redirect
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from online_version.model.order_sql import User
from online_version.extension.sqlmodel import db
from werkzeug.security import generate_password_hash, check_password_hash

#POST Method that gets the data.json from the frontend and adds the user in the database as new user checking on the way that the user was already not created and hence duplicate account not created is ensured.
class Register(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
        except Exception as e:
            return {'error': str(e)}
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                #user already exists
                return redirect('/signin')
            else:
                    user = User(
                        email = email, 
                        username = username, 
                        password = generate_password_hash(password)
                    )
                    db.session.add(user)
                    db.session.commit()
                    return redirect('/signin')
        except Exception as e:
            return {'error': str(e)}
        

#POST Method that takes user data from frontend, check whether user is present ensures that correct password is right, rbac is assigned based on whether password is provided or not.
class SignIn(Resource):
    def post(self):
        try:
            data = request.get_json()
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            user_admin = User.query.filter_by(email = email, username = username).first()
            if user_admin and check_password_hash(user_admin.password, password):
                role = 'admin'
            else:
                if not password:
                    user = User.query.filter_by(email = email, username = username).first()
                    if user:
                        role = 'view'
                    else:
                        return redirect('/register')
                else:
                    return {'error': 'Account is wrong'}, 401
            if username and email:
                token = create_access_token(identity= str(user_admin.id), additional_claims={"role": role})
                return jsonify({"access_token": token})
        except Exception as e:
            return {'error': str(e)}

        