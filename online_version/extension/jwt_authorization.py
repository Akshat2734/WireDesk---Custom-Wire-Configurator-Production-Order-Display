from flask_jwt_extended import JWTManager
from dotenv import dotenv_values

config = dotenv_values('.env')

def config_jwt_flask(value):
    value.config["JWT_SECRET_KEY"] = config.get('JWT_SECRET_KEY')
    jwt = JWTManager(value)
    return jwt