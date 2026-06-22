from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def config_sqlalchemy_flask(value):
    database_uri = value.config.get("SQLALCHEMY_DATABASE_URI") or os.environ.get(
        "SQLALCHEMY_DATABASE_URI"
    )
    if not database_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI must point to PostgreSQL")
    value.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    replica_uri = os.environ.get("REPLICA_DB_URI")
    if replica_uri and "SQLALCHEMY_BINDS" not in value.config:
        value.config["SQLALCHEMY_BINDS"] = {"replica": replica_uri}
    value.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    db.init_app(value)
