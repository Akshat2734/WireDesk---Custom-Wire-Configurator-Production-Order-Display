from flask import Flask
from flask_jwt_extended import jwt_required
from flask_restful import Api

from server.api import socket_events  # noqa: F401
from server.api.calculation import calculation_api_for_engine
from server.api.catalog import catalog_wire_types
from server.extension.jwt_authorization import config_jwt_flask
from server.extension.socket_io import socketio
from server.extension.sqlmodel import config_sqlalchemy_flask
from server.metrics import setup_metrics
from server.routes.auth import Register, SignIn
from server.routes.create_order import order_bp
from server.routes.stream_data import stream_data
from server.utils.role_required import role_required


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config is not None:
        app.config.update(test_config)

    config_jwt_flask(app)
    config_sqlalchemy_flask(app)
    socketio.init_app(app)
    api = Api(app)
    setup_metrics(app, socketio)

    @app.get("/")
    @jwt_required()
    @role_required("admin")
    def hello():
        return "Successful"

    app.register_blueprint(catalog_wire_types)
    app.register_blueprint(calculation_api_for_engine)
    app.register_blueprint(order_bp)
    app.register_blueprint(stream_data)
    api.add_resource(Register, "/register")
    api.add_resource(SignIn, "/signin")
    return app


if __name__ == "__main__":
    application = create_app()
    socketio.run(application, debug=application.debug)
