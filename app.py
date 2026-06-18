from flask import Flask 
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required
from online_version.extension.jwt_authorization import config_jwt_flask
from online_version.extension.sqlmodel import config_sqlalchemy_flask
from online_version.routes.auth import Register, SignIn
from online_version.utils.role_required import role_required
from online_version.api.catalog import catalog_wire_types
from online_version.api.calculation import calculation_api_for_engine
from online_version.extension.socket_io import socketio
from metrics import setup_metrics

app = Flask(__name__)

#runs the function from extension folder -> jwt_extension file and is responsible for passing parameter as app,
#The function is responsible for impleting jwt through using lask jwt extended
config_jwt_flask(app)
config_sqlalchemy_flask(app)
socketio.init_app(app)

api = Api(app)
setup_metrics(app, socketio)

#Boiler Plate Code that does nothing
@app.route('/', methods = ['GET'])
@jwt_required()
@role_required('admin')
def hello():
    return "Successful"

#GET Method that shows catalog of wires to the user, required admin rights as well as jwt token
app.register_blueprint(catalog_wire_types)

#GET Method that uses input as well as lookup table for the wire type, then shows the calcualated result using calculation_file that have the calculation engine
app.register_blueprint(calculation_api_for_engine)

#POST Method that register new user and adds them in the database and redirects them to sign in route. 
api.add_resource(Register, '/register')

#POST Method that sign in and assigns role to the person, checks whether user is new and if yes first redirect it to register for ensuring that the user is added in the database.
api.add_resource(SignIn, '/signin')

if __name__ == '__main__':
    if socketio:
        socketio.run(app)
    else:
        app.run(debug = True)