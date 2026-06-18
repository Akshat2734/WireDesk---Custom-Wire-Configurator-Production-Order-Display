from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def config_sqlalchemy_flask(value):
    value.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    value.config['SQLALCHEMY_BINDS'] = {
        'replica': os.environ.get('REPLICA_DB_URI')
    }
    value.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(value)
