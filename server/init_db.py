from server.app import create_app
from server.extension.sqlmodel import db


def main():
    app = create_app()
    with app.app_context():
        db.create_all(bind_key=None)


if __name__ == "__main__":
    main()
