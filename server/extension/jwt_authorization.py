from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

def config_jwt_flask(value):
    value.config.setdefault(
        "JWT_SECRET_KEY",
        os.environ.get("JWT_SECRET_KEY", "local-development-secret-change-me"),
    )
    jwt = JWTManager(value)
    return jwt
